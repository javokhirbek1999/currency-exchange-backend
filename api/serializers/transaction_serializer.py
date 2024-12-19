from rest_framework import serializers

from api.models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):

    """Transaction model serializer."""
    
    class Meta:
        model = Transaction 
        fields = ('user', 'source', 'destination', 'transaction_type', 'amount', 'date', 'source_wallet_details',)
        read_only_fields = ('date',)
