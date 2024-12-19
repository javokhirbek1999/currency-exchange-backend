from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Wallet(models.Model):
    """Wallet Database model."""

    CURRENCIES = (
        ('THB', 'Thai Baht'),
        ('USD', 'US Dollar'),
        ('AUD', 'Australian Dollar'),
        ('HKD', 'Hong Kong Dollar'),
        ('CAD', 'Canadian Dollar'),
        ('NZD', 'New Zealand Dollar'),
        ('SGD', 'Singapore Dollar'),
        ('EUR', 'Euro'),
        ('HUF', 'Hungarian Forint'),
        ('CHF', 'Swiss Franc'),
        ('GBP', 'British Pound'),
        ('UAH', 'Ukrainian Hryvnia'),
        ('JPY', 'Japanese Yen'),
        ('CZK', 'Czech Koruna'),
        ('DKK', 'Danish Krone'),
        ('ISK', 'Icelandic Krona'),
        ('NOK', 'Norwegian Krone'),
        ('SEK', 'Swedish Krona'),
        ('HRK', 'Croatian Kuna'),
        ('RON', 'Romanian Leu'),
        ('BGN', 'Bulgarian Lev'),
        ('TRY', 'Turkish Lira'),
        ('ILS', 'Israeli New Shekel'),
        ('CLP', 'Chilean Peso'),
        ('PHP', 'Philippine Peso'),
        ('MXN', 'Mexican Peso'),
        ('ZAR', 'South African Rand'),
        ('BRL', 'Brazilian Real'),
        ('MYR', 'Malaysian Ringgit'),
        ('RUB', 'Russian Ruble'),
        ('IDR', 'Indonesian Rupiah'),
        ('INR', 'Indian Rupee'),
        ('KRW', 'South Korean Won'),
        ('CNY', 'Chinese Yuan'),
        ('XDR', 'Special Drawing Rights (SDR)'),
        ('AFN', 'Afghan Afghani'),
        ('ALL', 'Albanian Lek'),
        ('AMD', 'Armenian Dram'),
        ('AOA', 'Angolan Kwanza'),
        ('BAM', 'Bosnia-Herzegovina Convertible Mark'),
        ('BSD', 'Bahamian Dollar'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('NZD', 'New Zealand Dollar'),
        ('PLN', 'Polish Zloty')
    )

    user = models.ForeignKey('api.User', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    currency = models.CharField(max_length=100, choices=CURRENCIES)
    wallet_address = models.CharField(max_length=40, unique=True, editable=False)

    class Meta:
        # Ensure a user can have only one wallet per currency
        constraints = [
            models.UniqueConstraint(fields=['user', 'currency'], name='unique_wallet_per_currency')
        ]

    def save(self, *args, **kwargs):
        if not self.wallet_address:
            # Generate a more unique wallet address
            self.wallet_address = f"{str(uuid.uuid4())[:18]}{self.user.id}"
        super().save(*args, **kwargs)
