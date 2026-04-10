from .fedapay import FedaPayGateway
from .stripe import StripeGateway

class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(provider_name):
        provider_name = provider_name.lower()
        if provider_name == 'fedapay':
            return FedaPayGateway()
        elif provider_name == 'stripe':
            return StripeGateway()
        else:
            raise ValueError(f"Gateway {provider_name} non supporté.")
