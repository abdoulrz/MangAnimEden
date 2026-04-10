import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import Transaction, UserWallet
from .factory import PaymentGatewayFactory

@csrf_exempt
def webhook_receiver(request, provider):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        gateway = PaymentGatewayFactory.get_gateway(provider)
    except ValueError:
        return JsonResponse({'error': 'Invalid provider'}, status=400)

    # Extraction du payload et signature
    payload = request.body.decode('utf-8')
    signature = request.headers.get('Webhook-Signature', '')
    
    if not gateway.verify_webhook(payload, signature):
        return JsonResponse({'error': 'Invalid signature'}, status=403)

    try:
        data = json.loads(payload)
        # Attention: la clé ID dépend du provider, on assume 'transaction_id' au sein de note entité
        transaction_id = data.get('transaction_id')
        
        transaction = Transaction.objects.get(id=transaction_id, status='PENDING')
        transaction.status = 'SUCCESS'
        transaction.webhook_payload = data
        transaction.save()
        
        # Atomically credit the wallet
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            wallet = UserWallet.objects.select_for_update().get(user=transaction.user)
            wallet.credits_balance += transaction.credits_awarded
            wallet.save()
            
        return JsonResponse({'status': 'success'})
    except Transaction.DoesNotExist:
        # PENDING transaction not found, possibly already processed
        return JsonResponse({'error': 'Transaction not found or completed'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
