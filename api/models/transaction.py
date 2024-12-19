from django.db import models

from api.models.wallet import Wallet


class Transaction(models.Model):

    """Transaction database model."""

    TRANSACTION_TYPES = (
        ('DEPOSIT', 'DEPOSIT'),
        ('WITHDRAWL', 'WITHDRAWL'),
        ('TRANSFER', 'TRANSFER'),
    )

    user = models.ForeignKey('api.User', on_delete=models.CASCADE, default=0)
    source = models.CharField(max_length=100) # From which wallet or account is the money transferred from
    destination = models.CharField(max_length=100) # To which wallet is the money transferred to
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        ordering = ['-date']


    @property
    def source_wallet_details(self):

        if self.transaction_type == 'TRANSFER':

            from_wallet = Wallet.objects.get(wallet_address=self.source)
            to_wallet = Wallet.objects.get(wallet_address=self.destination)

            return {
                'user': {
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email
                },
                'transferred_from_wallet': {
                    'wallet_address': from_wallet.wallet_address,
                    'balance': from_wallet.balance,
                    'currency': from_wallet.currency,
                },
                'transferred_to_wallet': {
                    'wallet_address': to_wallet.wallet_address,
                    'balance': to_wallet.balance,
                    'currency': to_wallet.currency
                }
            }
        
        elif self.transaction_type == "DEPOSIT":
            
            wallet = Wallet.objects.get(wallet_address=self.destination)

            return {
                'user': {
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email,
                },
                'transferred_from_bank_address': self.source,
                'transferred_to_wallet': {
                    'wallet_address': wallet.wallet_address,
                    'balance': wallet.balance,
                    'currency': wallet.currency
                }
            }
        
        else:

            wallet = Wallet.objects.get(wallet_address=self.destination)

            return {
                'user': {
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email,
                },
                'transferred_from_wallet': {
                    'wallet_address': wallet.wallet_address,
                    'balance': wallet.balance,
                    'currency': wallet.currency
                },
                'transferred_to_bank_address': self.source
            }
    