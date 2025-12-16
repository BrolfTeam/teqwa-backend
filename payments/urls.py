from django.urls import path
from .views import InitializePaymentView, ChapaWebhookView, VerifyPaymentView

urlpatterns = [
    path('initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
    path('webhook/', ChapaWebhookView.as_view(), name='chapa-webhook'),
    path('verify/<str:tx_ref>/', VerifyPaymentView.as_view(), name='verify-payment'),
]
