from .base import PaymentGateway

class StripeGateway(PaymentGateway):
    """
    Implémentation de Stripe pour les paiements internationaux (Cartes bancaires).
    """
    def create_payment(self, user, amount, currency='USD', **kwargs):
        # TODO: Implémenter la création d'une session Stripe Checkout
        return "https://checkout.stripe.com/demolink"

    def verify_webhook(self, payload, signature):
        # TODO: Implémenter la validation Webhook de Stripe
        return True
