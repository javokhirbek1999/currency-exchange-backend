from django.urls import path
from api.views.transaction_views import TransactionListView

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
]
