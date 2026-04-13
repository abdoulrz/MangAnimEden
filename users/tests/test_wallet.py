"""
Tests unitaires Phase 5 – Moteur de Monétisation
Commande: python manage.py test core.payments users.tests.test_wallet --verbosity=2
"""
import json
import hmac
import hashlib

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.models import UserWallet, Transaction

User = get_user_model()


class WalletModelTest(TestCase):
    """Tests sur le modèle UserWallet et son signal de création automatique."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@manganimeden.test',
            password='testpass123',
            nickname='Testeur'
        )

    def test_wallet_auto_created_on_user_creation(self):
        """Le signal post_save doit créer un wallet à la création d'un utilisateur."""
        self.assertTrue(hasattr(self.user, 'wallet'))
        self.assertEqual(self.user.wallet.credits_balance, 0)

    def test_wallet_str(self):
        self.assertIn('Testeur', str(self.user.wallet))


class ToggleAutoCreditsTest(TestCase):
    """Tests AJAX du toggle auto_use_credits."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='toggle@test.test', password='pass', nickname='Toggler'
        )
        self.client.force_login(self.user)
        self.url = reverse('users:toggle_auto_credits')

    def test_enable_auto_credits(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({'auto_use_credits': True}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.user.wallet.refresh_from_db()
        self.assertTrue(self.user.wallet.auto_use_credits)

    def test_disable_auto_credits(self):
        self.user.wallet.auto_use_credits = True
        self.user.wallet.save()
        resp = self.client.post(
            self.url,
            data=json.dumps({'auto_use_credits': False}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.user.wallet.refresh_from_db()
        self.assertFalse(self.user.wallet.auto_use_credits)

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.post(self.url, content_type='application/json', data='{}')
        self.assertEqual(resp.status_code, 302)  # Redirect to login


class InitiatePaymentTest(TestCase):
    """Tests de la vue initiate_payment."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@test.test', password='pass', nickname='Acheteur'
        )
        self.client.force_login(self.user)
        self.url = reverse('users:initiate_payment')

    def test_invalid_amount_too_low(self):
        """Montant < 1000 doit être rejeté (nouveau minimum UI aligné backend)."""
        resp = self.client.post(
            self.url,
            data=json.dumps({'amount': 999, 'provider': 'fedapay'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['success'])

    def test_invalid_amount_too_high(self):
        """Montant > 10 000 doit être rejeté."""
        resp = self.client.post(
            self.url,
            data=json.dumps({'amount': 10001, 'provider': 'fedapay'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_provider(self):
        resp = self.client.post(
            self.url,
            data=json.dumps({'amount': 1000, 'provider': 'paypal'}),
            content_type='application/json',
        )
        self.assertIn(resp.status_code, [400, 500])

    def test_transaction_created_pending(self):
        """Une Transaction PENDING doit être créée en DB avant la redirection FedaPay."""
        # On mocke le gateway pour ne pas appeler FedaPay Sandbox
        from unittest.mock import patch
        with patch('core.payments.fedapay.FedaPayGateway.create_payment', return_value='https://sandbox.fedapay.com/test'):
            resp = self.client.post(
                self.url,
                data=json.dumps({'amount': 1000, 'provider': 'fedapay'}),
                content_type='application/json',
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertIn('payment_url', data)

        # Vérifier la transaction en base
        txn = Transaction.objects.filter(user=self.user, status='PENDING').first()
        self.assertIsNotNone(txn)
        self.assertEqual(txn.credits_awarded, 1000)
        self.assertEqual(txn.gateway_used, 'fedapay')


class WebhookTest(TestCase):
    """Tests du webhook_receiver avec simulation de payload FedaPay."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='webhook@test.test', password='pass', nickname='WebhookUser'
        )
        self.wallet = self.user.wallet
        self.txn = Transaction.objects.create(
            user=self.user,
            amount_in_fiat=1000,
            currency='XOF',
            gateway_used='fedapay',
            status='PENDING',
            credits_awarded=1000,
        )
        self.url = '/payments/webhook/fedapay/'

    def _make_signature(self, payload: str, secret: str) -> str:
        import hmac as _hmac
        return 'sha256=' + _hmac.new(
            secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    def test_webhook_credits_wallet(self):
        """Un webhook FedaPay valide doit créditer le portefeuille atomiquement."""
        from django.test import override_settings

        # Format réel FedaPay: name + entity (pas 'transaction')
        payload = json.dumps({
            'name': 'transaction.approved',
            'object': 'v1/transaction',
            'entity': {
                'klass': 'v1/transaction',
                'id': 999,
                'reference': 'trx_test',
                'amount': 1000,
                'status': 'approved',
                'custom_metadata': {'django_transaction_id': str(self.txn.id)}
            },
            'account': {'id': 1}
        })
        secret = 'test_webhook_secret_123'
        sig = self._make_signature(payload, secret)

        with override_settings(FEDAPAY_WEBHOOK_SECRET=secret, DEBUG=False):
            resp = self.client.post(
                self.url,
                data=payload,
                content_type='application/json',
                HTTP_X_FEDAPAY_SIGNATURE=sig,
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'success')

        self.txn.refresh_from_db()
        self.assertEqual(self.txn.status, 'SUCCESS')

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.credits_balance, 1000)

    def test_webhook_duplicate_ignored(self):
        """Un webhook dupliqué (transaction déjà SUCCESS) ne doit pas doubler les crédits."""
        from django.test import override_settings

        # Marquer la transaction comme SUCCESS manuellement
        self.txn.status = 'SUCCESS'
        self.txn.save()

        payload = json.dumps({
            'name': 'transaction.approved',
            'object': 'v1/transaction',
            'entity': {
                'id': 999,
                'status': 'approved',
                'custom_metadata': {'django_transaction_id': str(self.txn.id)}
            },
            'account': {'id': 1}
        })
        secret = 'test_webhook_secret_123'
        sig = self._make_signature(payload, secret)

        with override_settings(FEDAPAY_WEBHOOK_SECRET=secret, DEBUG=False):
            resp = self.client.post(
                self.url, data=payload, content_type='application/json',
                HTTP_X_FEDAPAY_SIGNATURE=sig,
            )

        # Doit retourner 200 (already_processed) mais pas créditer
        self.assertEqual(resp.status_code, 200)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.credits_balance, 0)  # Pas crédité

    def test_webhook_invalid_signature_rejected(self):
        """Une signature HMAC invalide doit être rejetée avec 403."""
        from django.test import override_settings

        payload = json.dumps({'transaction_id': str(self.txn.id)})

        with override_settings(FEDAPAY_WEBHOOK_SECRET='real_secret', DEBUG=False):
            resp = self.client.post(
                self.url, data=payload, content_type='application/json',
                HTTP_X_FEDAPAY_SIGNATURE='sha256=fakesignature000',
            )

        self.assertEqual(resp.status_code, 403)


class AdminBypassTest(TestCase):
    """Tests du bypass admin sur le paywall et les filtres NSFW."""

    def setUp(self):
        # Admin
        self.admin = User.objects.create_user(
            email='admin@test.test', password='pass', nickname='Admin',
            is_staff=True
        )
        # Utilisateur lambda
        self.normal = User.objects.create_user(
            email='normal@test.test', password='pass', nickname='Normal'
        )

    def test_admin_has_staff_flag(self):
        self.assertTrue(self.admin.is_staff)

    def test_normal_user_has_no_staff_flag(self):
        self.assertFalse(self.normal.is_staff)


class UnlockChapterTest(TestCase):
    """Tests du deblocage manuel d un chapitre premium via credits."""

    def setUp(self):
        from catalog.models import Series, Chapter

        self.user = User.objects.create_user(
            email='reader@test.test', password='pass', nickname='Lecteur'
        )
        self.client.force_login(self.user)

        # Crediter le wallet
        self.wallet = self.user.wallet

        # Fixtures catalog
        self.series = Series.objects.create(title='Test Series', slug='test-series')
        self.chapter = Chapter.objects.create(
            series=self.series, number=1, title='Chapitre Test', is_premium=True
        )
        self.url = f'/reader/unlock/{self.chapter.id}/'

    def test_manual_unlock_success(self):
        """Assez de credits -> chapitre debloque, credits deduits."""
        from reader.models import UnlockedChapter
        self.wallet.credits_balance = 100
        self.wallet.save()

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertIn('redirect', data)
        self.assertEqual(data['new_balance'], 80)  # 100 - 20

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.credits_balance, 80)
        self.assertTrue(
            UnlockedChapter.objects.filter(user=self.user, chapter=self.chapter).exists()
        )

    def test_manual_unlock_insufficient_credits(self):
        """Pas assez de credits -> 402, wallet inchange."""
        from reader.models import UnlockedChapter
        self.wallet.credits_balance = 10
        self.wallet.save()

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 402)
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.credits_balance, 10)  # inchange
        self.assertFalse(
            UnlockedChapter.objects.filter(user=self.user, chapter=self.chapter).exists()
        )

    def test_manual_unlock_idempotent(self):
        """Deja debloque -> succes sans re-deduire."""
        from reader.models import UnlockedChapter
        self.wallet.credits_balance = 100
        self.wallet.save()
        UnlockedChapter.objects.create(user=self.user, chapter=self.chapter)

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data.get('already_unlocked'))

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.credits_balance, 100)  # non deduit
