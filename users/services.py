from django.utils import timezone
from .models import Badge, UserBadge
from reader.models import ReadingProgress

class BadgeService:
    @staticmethod
    def check_badges(user, condition_type):
        """
        Vérifie et attribue les badges pour un type de condition donné.
        Retourne la liste des badges nouvellement acquis.
        """
        # Badges potentiels de ce type
        potential_badges = Badge.objects.filter(condition_type=condition_type)
        
        # Badges déjà acquis
        existing_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        
        newly_awarded = []
        
        for badge in potential_badges:
            if badge.id in existing_badge_ids:
                continue
                
            awarded = False
            
            if condition_type == 'CHAPTERS_READ':
                # Compter les chapitres lus
                count = ReadingProgress.objects.filter(user=user, completed=True).count()
                if count >= badge.threshold:
                    awarded = True
                    
            elif condition_type == 'ACCOUNT_AGE':
                delta = timezone.now() - user.date_joined
                if delta.days >= badge.threshold:
                    awarded = True
            
            # TODO: Implémenter les autres types de conditions au besoin
            
            if awarded:
                UserBadge.objects.create(user=user, badge=badge)
                newly_awarded.append(badge)
                
        return newly_awarded

from django.db import transaction as db_transaction
from .models import Transaction, UserWallet
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def process_transaction_success(transaction_id, webhook_payload=None):
        """
        Process a successful transaction: update status and credit user wallet.
        Thread-safe and atomic to prevent double-crediting.
        """
        try:
            with db_transaction.atomic():
                # Lock the transaction row to prevent parallel processing
                txn = Transaction.objects.select_for_update().get(
                    id=transaction_id, 
                    status='PENDING'
                )
                
                # Mark as success
                txn.status = 'SUCCESS'
                if webhook_payload:
                    txn.webhook_payload = webhook_payload
                txn.save(update_fields=['status', 'webhook_payload'])
                
                # Credit the wallet
                wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=txn.user)
                wallet.credits_balance += txn.credits_awarded
                wallet.save(update_fields=['credits_balance'])
                
                logger.info(
                    f"PaymentService: ✅ Transaction #{transaction_id} approved. "
                    f"User: {txn.user.nickname}, Credits: +{txn.credits_awarded}"
                )
                return True, txn
                
        except Transaction.DoesNotExist:
            logger.warning(f"PaymentService: Transaction #{transaction_id} not found or already processed.")
            return False, "Transaction introuvable ou déjà traitée."
        except Exception as e:
            logger.exception(f"PaymentService: Error processing transaction #{transaction_id}: {e}")
            return False, str(e)
