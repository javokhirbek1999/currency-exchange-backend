from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models.wallet import Wallet
from api.models.user import User  # Adjust this import based on your project structure


@receiver(post_save, sender=User)
def create_wallet_for_user(sender, instance, created, **kwargs):
    if created:
        # Create a Wallet with default currency 'PLN'
        Wallet.objects.create(user=instance, balance=0.0, currency='PLN')
