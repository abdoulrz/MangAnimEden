import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from users.models import Transaction, UserWallet
from .factory import PaymentGatewayFactory

logger = logging.getLogger(__name__)

# Événements FedaPay qui signifient un paiement réussi
FEDAPAY_SUCCESS_EVENTS = {'transaction.approved', 'transaction.created'}
# Événements qui signifient un échec à marquer en DB
FEDAPAY_FAILED_EVENTS  = {'transaction.declined', 'transaction.canceled', 'transaction.deleted'}


@csrf_exempt
@require_POST
def webhook_receiver(request, provider):
    """
    Endpoint recevant les notifications de paiement (webhooks) des passerelles.
    URL: /payments/webhook/<provider>/

    Structure réelle du payload FedaPay (observée en sandbox) :
    {
      "name":    "transaction.approved" | "transaction.declined" | ...
      "object":  "v1/transaction"   ← STRING (type), pas un objet !
      "entity":  { id, reference, amount, status, custom_metadata, ... }
      "account": { ... }
    }
    """
    try:
        gateway = PaymentGatewayFactory.get_gateway(provider)
    except ValueError:
        logger.warning(f"Webhook reçu pour provider inconnu: {provider}")
        return JsonResponse({'error': 'Provider invalide'}, status=400)

    payload = request.body.decode('utf-8')

    signature = (
        request.headers.get('X-FEDAPAY-SIGNATURE')
        or request.headers.get('Stripe-Signature')
        or request.headers.get('Webhook-Signature', '')
    )

    if not gateway.verify_webhook(payload, signature):
        logger.error(f"Webhook {provider}: signature invalide. IP={request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'error': 'Signature invalide'}, status=403)

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Payload JSON invalide'}, status=400)

    event_name = data.get('name', '')
    logger.info(f"Webhook {provider}: event={event_name} | top-level keys={list(data.keys())}")

    # --- Extraction de la transaction FedaPay ---
    # data['object'] = STRING ("v1/transaction"), PAS un dict
    # data['entity'] = le vrai objet transaction (dict)
    fedapay_txn = data.get('entity')
    if not isinstance(fedapay_txn, dict):
        # Fallbacks pour d'autres providers ou formats futurs
        fedapay_txn = data.get('transaction') or data.get('v1/transaction') or {}

    logger.info(f"Webhook {provider}: entity keys={list(fedapay_txn.keys()) if isinstance(fedapay_txn, dict) else type(fedapay_txn)}")

    # --- Traitement selon l'événement ---
    # Événements DECLINED / CANCELED → marquer FAILED en DB, pas de crédit
    if event_name in FEDAPAY_FAILED_EVENTS:
        logger.info(f"Webhook {provider}: transaction {event_name} — on marque FAILED si PENDING.")
        _mark_transaction_failed(provider, data, fedapay_txn)
        return JsonResponse({'status': 'noted_failed'})

    # Événements non-succès inconnus → ignorer sans erreur
    if event_name not in FEDAPAY_SUCCESS_EVENTS:
        logger.info(f"Webhook {provider}: événement non géré '{event_name}' → ignoré.")
        return JsonResponse({'status': 'ignored', 'event': event_name})

    # === Traitement SUCCESS ===
    django_txn_id = _extract_django_txn_id(provider, data, fedapay_txn)

    if not django_txn_id:
        logger.warning(f"Webhook {provider}: impossible de résoudre django_transaction_id.")
        return JsonResponse({'status': 'ignored', 'reason': 'no transaction_id'})

    from users.services import PaymentService
    success, result = PaymentService.process_transaction_success(django_txn_id, webhook_payload=data)

    if success:
        return JsonResponse({'status': 'success'})
    else:
        # result contient le message d'erreur
        if "Transaction introuvable" in str(result):
            return JsonResponse({'status': 'already_processed'})
        return JsonResponse({'error': str(result)}, status=500)


def _extract_django_txn_id(provider, data, fedapay_txn):
    """Tente de retrouver l'ID de notre Transaction Django depuis le payload FedaPay."""
    # 1. custom_metadata (source la plus fiable)
    custom_meta = fedapay_txn.get('custom_metadata') if isinstance(fedapay_txn, dict) else None
    if isinstance(custom_meta, dict):
        txn_id = custom_meta.get('django_transaction_id')
        if txn_id:
            logger.info(f"Webhook {provider}: found django_transaction_id={txn_id} via custom_metadata")
            return txn_id

    # 2. transaction_id direct (tests manuels via curl)
    txn_id = data.get('transaction_id')
    if txn_id:
        return txn_id

    # 3. Fallback: dernière Transaction PENDING (heuristique pour sandbox)
    logger.info(f"Webhook {provider}: custom_metadata absent → fallback sur dernière PENDING")
    pending = Transaction.objects.filter(status='PENDING').order_by('-created_at').first()
    if pending:
        logger.info(f"Webhook {provider}: fallback → Transaction PENDING #{pending.id}")
        return pending.id

    return None


def _mark_transaction_failed(provider, data, fedapay_txn):
    """Marque la Transaction Django correspondante comme FAILED."""
    try:
        django_txn_id = _extract_django_txn_id(provider, data, fedapay_txn)
        if not django_txn_id:
            return
        txn = Transaction.objects.filter(id=django_txn_id, status='PENDING').first()
        if txn:
            txn.status = 'FAILED'
            txn.webhook_payload = data
            txn.save(update_fields=['status', 'webhook_payload'])
            logger.info(f"Webhook {provider}: Transaction #{txn.id} marquée FAILED.")
    except Exception as e:
        logger.error(f"Webhook {provider}: erreur lors du marquage FAILED – {e}")
