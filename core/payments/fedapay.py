import hashlib
import hmac
import logging

from django.conf import settings

from .base import PaymentGateway

logger = logging.getLogger(__name__)


class FedaPayGateway(PaymentGateway):
    """
    Implémentation FedaPay pour les paiements locaux en Afrique (XOF/CFA).
    SDK: pip install fedapay
    Docs: https://docs.fedapay.com/integration/python
    """

    def __init__(self):
        try:
            import fedapay as fp
            fp.api_key = settings.FEDAPAY_SECRET_KEY
            fp.environment = getattr(settings, 'FEDAPAY_ENV', 'sandbox')
            self._fp = fp
        except ImportError:
            logger.error("FedaPay SDK non installé. Lancez: pip install fedapay")
            self._fp = None

    def create_payment(self, user, amount, currency='XOF', **kwargs):
        """
        Crée une transaction FedaPay et retourne l'URL de paiement.
        amount : montant en FCFA (= crédits accordés car 1 FCFA = 1 Crédit)
        Retourne l'URL de paiement FedaPay Sandbox/Live.
        """
        if not self._fp:
            raise RuntimeError("FedaPay SDK non disponible.")

        callback_url = kwargs.get(
            'callback_url',
            getattr(settings, 'FEDAPAY_CALLBACK_URL', 'http://localhost:8000/users/payment/callback/')
        )
        transaction_id = kwargs.get('transaction_id', '')

        transaction = self._fp.Transaction.create(**{
            'description': f"MangAnimEDen – Achat de {amount} Crédits",
            'amount': int(amount),
            'currency': {'iso': currency},
            'callback_url': callback_url,
            'customer': {
                'email': user.email,
                'firstname': user.nickname,
                'lastname': '',
            },
            # On stocke l'ID de notre Transaction Django en metadata pour le retrouver dans le webhook
            'custom_metadata': {'django_transaction_id': str(transaction_id)},
        })

        token = transaction.generateToken()
        payment_url = token.get('url') or token.get('token_url', '')
        logger.info(f"FedaPay: Transaction créée pour {user.nickname} – {amount} XOF → {payment_url}")
        return payment_url

    def verify_webhook(self, payload: str, signature: str) -> bool:
        """
        Vérifie la signature HMAC-SHA256 envoyée par FedaPay.
        FedaPay envoie le header: X-FEDAPAY-SIGNATURE: sha256=<hex_digest>
        """
        secret = getattr(settings, 'FEDAPAY_WEBHOOK_SECRET', '')
        if not secret:
            logger.warning("FEDAPAY_WEBHOOK_SECRET non configuré – vérification ignorée en sandbox.")
            # En sandbox sans secret configuré, on laisse passer pour pouvoir tester
            return getattr(settings, 'DEBUG', False)

        secret_bytes = secret.encode('utf-8')
        payload_bytes = payload.encode('utf-8') if isinstance(payload, str) else payload

        expected = 'sha256=' + hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()

        # Comparaison sécurisée (résistante aux timing attacks)
        return hmac.compare_digest(expected, signature)
