from .fedapay import FedaPayGateway
from .stripe import StripeGateway
# TODO (Phase 6): from .nowpayments import NOWPaymentsGateway
# NOWPayments (https://nowpayments.io) will handle crypto payments (BTC, ETH, USDT, etc.)
# SDK: pip install nowpayments | Docs: https://nowpayments.io/docs

class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(provider_name):
        provider_name = provider_name.lower()
        if provider_name == 'fedapay':
            return FedaPayGateway()
        elif provider_name == 'stripe':
            return StripeGateway()
        # elif provider_name == 'nowpayments':        # Phase 6 - Crypto
        #     return NOWPaymentsGateway()
        else:
            raise ValueError(f"Gateway '{provider_name}' non supporté. Disponibles: fedapay, stripe")
