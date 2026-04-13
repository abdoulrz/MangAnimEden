import hashlib
import hmac
import json
import logging

import requests
from django.conf import settings

from .base import PaymentGateway

logger = logging.getLogger(__name__)

FEDAPAY_SANDBOX_BASE = "https://sandbox-api.fedapay.com/v1"
FEDAPAY_LIVE_BASE    = "https://api.fedapay.com/v1"


class FedaPayGateway(PaymentGateway):
    """
    Implémentation FedaPay via HTTP REST (pas de SDK Transaction).
    Le SDK fedapay==0.3.0 ne gère que la vérification de webhook.

    API Docs: https://docs.fedapay.com
    """

    def __init__(self):
        self.secret_key = getattr(settings, 'FEDAPAY_SECRET_KEY', '')
        env = getattr(settings, 'FEDAPAY_ENV', 'sandbox')
        self.base_url = FEDAPAY_SANDBOX_BASE if env == 'sandbox' else FEDAPAY_LIVE_BASE
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }

    def create_payment(self, user, amount, currency='XOF', **kwargs):
        """
        Crée une transaction via l'API REST FedaPay et retourne l'URL de paiement.

        Format validé par tests directs sur l'API sandbox:
        - currency = {"iso": "XOF", "mode": "cybersource"}  (mode requis !)
        - Réponse: data["v1/transaction"]["id"]
        - Token: POST /transactions/{id}/token → {"url": "https://sandbox-process.fedapay.com/..."}
        """
        if not self.secret_key:
            raise RuntimeError("FEDAPAY_SECRET_KEY non configurée dans .env")

        callback_url = kwargs.get(
            'callback_url',
            getattr(settings, 'FEDAPAY_CALLBACK_URL', 'http://localhost:8000/users/payment/callback/')
        )
        transaction_id = kwargs.get('transaction_id', '')

        # --- Étape 1: Créer la transaction ---
        payload = {
            'description': f"MangAnimEDen – {int(amount)} Crédits",
            'amount': int(amount),
            'currency': {'iso': currency, 'mode': 'cybersource'},
            'callback_url': callback_url,
            'custom_metadata': {'django_transaction_id': str(transaction_id)},
            'customer': {
                'email': user.email,
                'firstname': user.nickname,
                'lastname': '.',
            }
        }

        try:
            resp = requests.post(
                self.base_url + '/transactions',
                headers=self.headers,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            body = e.response.text if e.response else ''
            logger.error(f"FedaPay create_payment 4xx/5xx: {e} | body: {body}")
            raise RuntimeError(f"FedaPay API error: {body}")
        except requests.exceptions.RequestException as e:
            logger.error(f"FedaPay create_payment réseau: {e}")
            raise RuntimeError(f"Erreur de connexion FedaPay: {e}")

        data = resp.json()
        # FedaPay retourne la transaction sous la clé "v1/transaction"
        txn = data.get('v1/transaction') or data.get('transaction', {})
        fedapay_txn_id = txn.get('id')

        if not fedapay_txn_id:
            logger.error(f"FedaPay réponse inattendue: {data}")
            raise RuntimeError("Impossible de récupérer l'ID de transaction FedaPay.")

        # --- Étape 2: Générer le token de paiement ---
        try:
            token_resp = requests.post(
                self.base_url + '/transactions/' + str(fedapay_txn_id) + '/token',
                headers=self.headers,
                timeout=15,
            )
            token_resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"FedaPay generate_token error: {e}")
            raise RuntimeError(f"Erreur génération token FedaPay: {e}")

        token_data = token_resp.json()
        payment_url = token_data.get('url', '')

        if not payment_url:
            logger.error(f"FedaPay token response inattendue: {token_data}")
            raise RuntimeError("Impossible de récupérer l'URL de paiement FedaPay.")

        logger.info(
            f"FedaPay: Transaction #{fedapay_txn_id} créée pour {user.nickname} "
            f"– {amount} XOF → {payment_url[:60]}..."
        )
        return payment_url

    def verify_webhook(self, payload: str, signature: str) -> bool:
        """
        Vérifie la signature HMAC-SHA256 envoyée par FedaPay.
        FedaPay envoie: X-FEDAPAY-SIGNATURE: sha256=<hmac_hex>
        """
        secret = getattr(settings, 'FEDAPAY_WEBHOOK_SECRET', '')

        if not secret:
            logger.warning("FEDAPAY_WEBHOOK_SECRET non configuré – bypass en DEBUG.")
            return getattr(settings, 'DEBUG', False)

        if not signature:
            logger.error("FedaPay webhook: header de signature absent.")
            return False

        try:
            # Normaliser: retirer le préfixe "sha256=" si présent
            sig_value = signature.removeprefix('sha256=')

            expected = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(expected, sig_value):
                logger.error(
                    f"FedaPay webhook: signature invalide. "
                    f"Reçu={sig_value[:20]}... Attendu={expected[:20]}..."
                )
                return False
            return True
        except Exception as e:
            logger.error(f"FedaPay webhook verify error: {e}")
            return False
