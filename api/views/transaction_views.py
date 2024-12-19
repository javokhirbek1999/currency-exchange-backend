from api.models.transaction import Transaction
from api.serializers.transaction_serializer import TransactionSerializer
from rest_framework import generics, permissions

class TransactionListView(generics.ListAPIView):
    """
    API View to list all transactions for the authenticated user.
    - Users can only see their own transactions.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter transactions to only include those belonging to the logged-in user.
        """
        return Transaction.objects.filter(user=self.request.user)
