import requests
from decimal import Decimal, InvalidOperation
from django.http import Http404
from django.db import IntegrityError, transaction

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.models.wallet import Wallet
from api.models.transaction import Transaction

from api.serializers.wallet_serializer import WalletSerializer, WalletDepositWithdrawSerializer, WalletTransferSerializer
from api.permissions.wallet_permissions import IsOwnerOrReadOnly

class WalletListView(generics.ListCreateAPIView):
    """
    API view to list wallets or create a wallet.
    - Users can only view their own wallets.
    - Only authenticated users can create a wallet.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict wallets to only those owned by the logged-in user.
        """
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user when creating a wallet.
        """
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            # If a wallet with the same currency already exists for the user
            raise ValidationError("A wallet with this currency already exists.")


class WalletDetailView(generics.RetrieveDestroyAPIView):
    """
    API view to retrieve, update, or delete a wallet using the user's email.
    - Only the owner of the wallet can update or delete it.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """
        Override to get the wallet based on the user's email address.
        """
        currency = self.kwargs['currency']
        wallet = Wallet.objects.filter(user=self.request.user, currency=currency).first()
        if not wallet:
            raise Http404("Wallet with this currency does not exist for this user.")
        return wallet


class WalletDepositView(generics.UpdateAPIView):
    """
    API View to retrieve and deposit money into a specified wallet.
    - Retrieves the wallet and allows deposit by updating the `amount` field.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletDepositWithdrawSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_object(self):
        """
        Retrieve the wallet based on the user and currency.
        """
        currency = self.kwargs['currency']
        wallet = Wallet.objects.filter(user=self.request.user, currency=currency).first()
        if not wallet:
            raise Http404("Wallet with this currency does not exist for this user.")
        return wallet

    def update(self, request, *args, **kwargs):
        """
        Handle PUT request to apply deposit logic.
        """
        wallet = self.get_object() 

        # Use WalletDepositSerializer for validating the amount in the request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_account_address = serializer.validated_data.get('bank_account_address')
        amount = serializer.validated_data.get('amount')
        wallet.balance += amount 
        wallet.save()

        Transaction.objects.create(
            user=self.request.user,
            source=bank_account_address,
            destination=wallet.wallet_address,
            transaction_type="DEPOSIT",
            amount=amount,
        )

        return Response({
            "status": "success",
            "type": "deposit",
            "bank_account": bank_account_address,
            "amount": amount,
            "wallet_balance": wallet.balance,
            "wallet_currency": wallet.currency,
        }) 
    

class WalletWithdrawView(generics.UpdateAPIView):
    """
    API View to retrieve and withdraw money from a specified wallet.
    - Retrieves the wallet and allows withdrawal by updating the `amount` field.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletDepositWithdrawSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_object(self):
        """
        Retrieve the wallet based on the user and currency.
        """
        currency = self.kwargs['currency']
        wallet = Wallet.objects.filter(user=self.request.user, currency=currency).first()

        if not wallet:
            raise Http404("Wallet with this currency does not exist for this user.")
        return wallet

    def update(self, request, *args, **kwargs):
        """
        Override update to apply withdrawal logic.
        """
        wallet = self.get_object() 

        # Use WalletDepositSerializer for validating the amount in the request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_account_address = serializer.validated_data['bank_account_address']
        amount = serializer.validated_data.get('amount')

        # Check if withdrawal amount is greater than available balance
        if amount > wallet.balance:
            raise ValidationError("Insufficient balance for this withdrawal.")
        
        wallet.balance -= amount 
        wallet.save()

        Transaction.objects.create(
            user=self.request.user,
            source=bank_account_address,
            destination=wallet.wallet_address,
            transaction_type="WITHDRAWL",
            amount=amount,
        )

        return Response({
            "status": "success",
            "type": "withdrawl",
            "bank_account": bank_account_address,
            "amount": amount,
            "wallet_balance": wallet.balance,
            "wallet_currency": wallet.currency,
        }) 
    


class WalletTransferView(generics.GenericAPIView):
    """
    API View to transfer money between two wallets with different currencies, 
    using exchange rates from the NBP API.
    """
    serializer_class = WalletTransferSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def fetch_exchange_rate(self, source_currency, destination_currency):
        """
        Fetch exchange rates from the NBP API and calculate the rate for conversion.
        """
        try:
            # If source currency is PLN, return 1 since it's already in PLN
            if source_currency == 'PLN' and destination_currency == 'PLN':
                return Decimal(1)

            # If source currency is PLN, convert to destination currency rate
            if source_currency == 'PLN':
                response = requests.get(f'https://api.nbp.pl/api/exchangerates/rates/a/{destination_currency}/')
                response.raise_for_status()
                destination_rate = response.json().get('rates')[0].get('mid')
                return Decimal(1) / Decimal(destination_rate)  # Invert since source is PLN

            # If destination currency is PLN, convert source currency to PLN rate
            if destination_currency == 'PLN':
                response = requests.get(f'https://api.nbp.pl/api/exchangerates/rates/a/{source_currency}/')
                response.raise_for_status()
                source_rate = response.json().get('rates')[0].get('mid')
                return Decimal(source_rate)  # Direct conversion to PLN

            # Otherwise, fetch both source and destination rates for conversion
            source_response = requests.get(f'https://api.nbp.pl/api/exchangerates/rates/a/{source_currency}/')
            source_response.raise_for_status()
            source_rate = source_response.json().get('rates')[0].get('mid')

            destination_response = requests.get(f'https://api.nbp.pl/api/exchangerates/rates/a/{destination_currency}/')
            destination_response.raise_for_status()
            destination_rate = destination_response.json().get('rates')[0].get('mid')

            # Calculate the correct exchange rate for conversion
            return Decimal(source_rate) / Decimal(destination_rate)
        except (requests.RequestException, KeyError, InvalidOperation) as e:
            raise ValidationError(f"Failed to fetch exchange rates: {str(e)}")


    def post(self, request, *args, **kwargs):
        """
        Handle POST request to transfer money between wallets with currency conversion.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        source_currency = serializer.validated_data['source_currency']
        destination_currency = serializer.validated_data['destination_currency']
        amount = serializer.validated_data['amount']  # Amount in source currency

        # Retrieve wallets
        source_wallet = Wallet.objects.filter(user=request.user, currency=source_currency).first()
        destination_wallet = Wallet.objects.filter(user=request.user, currency=destination_currency).first()

        if source_wallet is None or destination_wallet is None:
            return Response(
                {"error": "Source or destination wallet not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure the source wallet has sufficient funds
        if source_wallet.balance < amount:
            return Response(
                {"error": "Insufficient funds in the source wallet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the correct exchange rate and calculate the converted amount
        exchange_rate = self.fetch_exchange_rate(source_currency, destination_currency)
        converted_amount = Decimal(amount) * exchange_rate

        # Perform the transfer
        source_wallet.balance -= Decimal(amount)
        source_wallet.save()

        destination_wallet.balance += converted_amount
        destination_wallet.save()

        Transaction.objects.create(
            user=self.request.user,
            source=source_wallet.wallet_address,
            destination=destination_wallet.wallet_address,
            transaction_type="TRANSFER",
            amount=amount,
        )

        return Response({
            "status": "success",
            "source_currency": source_currency,  # Source wallet currency
            "destination_currency": destination_currency,  # Destination wallet currency
            "source_balance": str(source_wallet.balance),  # Source wallet remaining balance
            "destination_balance": str(destination_wallet.balance),  # Destination wallet updated balance
            "exchange_rate": str(exchange_rate),  # Exchange rate used
            "source_amount": str(amount),  # Original amount in source currency
            "destination_amount": str(converted_amount)  # Transferred amount in destination currency
        }, status=status.HTTP_200_OK)

