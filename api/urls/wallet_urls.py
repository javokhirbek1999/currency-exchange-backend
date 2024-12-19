from django.urls import path
from api.views.wallet_views import WalletListView, WalletDetailView, WalletDepositView, WalletWithdrawView, WalletTransferView

urlpatterns = [
    path('', WalletListView.as_view(), name='wallet-list-create'),
    path('transfer/', WalletTransferView.as_view(), name='wallet-transfer'),
    path('<str:currency>/', WalletDetailView.as_view(), name='wallet-detail'),
    path('<str:currency>/deposit/', WalletDepositView.as_view(), name='wallet-deposit'),  # Wallet deposit endpoint
    path('<str:currency>/withdraw/', WalletWithdrawView.as_view(), name='wallet-withdraw'),
]
