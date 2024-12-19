from rest_framework import serializers
from api.models.wallet import Wallet


class WalletSerializer(serializers.ModelSerializer):

    """Wallet model serializer."""
    
    class Meta:
        model = Wallet 
        fields = '__all__'
        read_only_fields = ('wallet_address', 'balance', 'user')


class WalletDepositWithdrawSerializer(serializers.Serializer): 
    
    """Serializer for depositing money into a wallet."""
    
    bank_account_address = serializers.CharField(
        max_length=255, 
        required=True,
    )
    amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        min_value=0.01, 
        required=True
    )


class WalletTransferSerializer(serializers.Serializer):
    """
    Serializer for transferring money between two wallets.
    """
    source_currency = serializers.ChoiceField(choices=[], required=True)
    destination_currency = serializers.ChoiceField(choices=[], required=True)
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        required=True
    )

    def __init__(self, *args, **kwargs):
        """
        Dynamically set choices for source_currency and destination_currency
        based on the user's wallets.
        """
        user = kwargs['context']['request'].user
        super().__init__(*args, **kwargs)
        user_wallets = Wallet.objects.filter(user=user).values_list('currency', flat=True)
        wallet_choices = [(currency, currency) for currency in user_wallets]
        self.fields['source_currency'].choices = wallet_choices
        self.fields['destination_currency'].choices = wallet_choices

    def validate(self, data):
        """
        Validate the transfer details.
        """
        if data['source_currency'] == data['destination_currency']:
            raise serializers.ValidationError(
                "Source and destination currencies must be different."
            )
        return data