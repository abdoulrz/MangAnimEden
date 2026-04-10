from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    """
    Interface abstraite pour les passerelles de paiement.
    """
    @abstractmethod
    def create_payment(self, user, amount, currency='XOF', **kwargs):
        """Initie une transaction et retourne un lien de paiement ou un token"""
        pass

    @abstractmethod
    def verify_webhook(self, payload, signature):
        """Vérifie la signature du webhook cryptographiquement pour éviter la fraude"""
        pass
