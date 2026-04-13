"""
Script de test local : approuve manuellement une Transaction PENDING
via le webhook signé HMAC — sans dépendre de FedaPay sandbox.

Usage: python scripts/approve_test_transaction.py [transaction_id]
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import hmac
import hashlib
import json
import requests
from django.conf import settings
from users.models import Transaction


def approve_transaction(txn_id=None):
    # Récupérer la transaction
    if txn_id:
        txn = Transaction.objects.filter(id=txn_id).first()
    else:
        txn = Transaction.objects.filter(status='PENDING').order_by('-created_at').first()

    if not txn:
        print("❌ Aucune transaction PENDING trouvée.")
        return

    print(f"Transaction #{txn.id} | {txn.credits_awarded} crédits | user: {txn.user.nickname} | status: {txn.status}")

    if txn.status != 'PENDING':
        print(f"⚠️  La transaction n'est pas PENDING (status={txn.status}). Abandon.")
        return

    # Construire le payload webhook simulé (format réel FedaPay)
    payload = json.dumps({
        "name": "transaction.approved",
        "object": "v1/transaction",
        "entity": {
            "klass": "v1/transaction",
            "id": 999999,
            "reference": "trx_local_test",
            "amount": txn.credits_awarded,
            "description": "Test local",
            "status": "approved",
            "custom_metadata": {"django_transaction_id": str(txn.id)}
        },
        "account": {"id": 1}
    })

    # Signer avec notre FEDAPAY_WEBHOOK_SECRET
    secret = settings.FEDAPAY_WEBHOOK_SECRET
    signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Envoyer le webhook en local
    url = "http://127.0.0.1:8000/payments/webhook/fedapay/"
    print(f"\nEnvoi du webhook signé vers {url} ...")

    resp = requests.post(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-FEDAPAY-SIGNATURE": signature,
        },
        timeout=10,
    )

    print(f"Réponse HTTP: {resp.status_code}")
    print(f"Body: {resp.text}")

    if resp.status_code == 200 and resp.json().get('status') == 'success':
        txn.refresh_from_db()
        from users.models import UserWallet
        wallet = UserWallet.objects.get(user=txn.user)
        print(f"\n✅ SUCCÈS !")
        print(f"   Transaction #{txn.id} → {txn.status}")
        print(f"   Wallet {txn.user.nickname} → {wallet.credits_balance} crédits")
    else:
        print(f"\n❌ Échec. Vérifiez les logs Django.")


if __name__ == '__main__':
    txn_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    approve_transaction(txn_id)
