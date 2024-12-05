from django.urls import path
from .views import UserRegistrationView, CompleteRegistrationView, UserLoginView, LogoutView, ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView,SellerProductHistoryView, ProductHistoryDetailView, CartView, AddToCartView,RemoveFromCartView
from rest_framework.authtoken.views import obtain_auth_token
from .views import BuyerProfileUpdateView, SellerProfileRetrieveView, SellerProfileUpdateView, BuyerProfileCreateView, SellerProfileCreateView, buyerProfileRetrieveView 
from .views import BuyerTransactionListView, SellerTransactionListView, send_test_email_view
from project.transaction_paystack.paystack_view import PaymentInitializeView, PaymentCallbackView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('complete/register', CompleteRegistrationView.as_view(), name='user-profile'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('send-email/', send_test_email_view, name='send_test_email'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('products/', ProductListView.as_view(), name='product-list'), 
    path('products/create/', ProductCreateView.as_view(), name='product-create'),  
    path('products/update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),  
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/detail/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('seller/products/history/', SellerProductHistoryView.as_view(), name='seller-product-history-overview'),
    path('seller/products/history/<int:pk>/', ProductHistoryDetailView.as_view(), name='seller-product-history-detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('seller/profile/', SellerProfileRetrieveView.as_view(), name='seller-profile-create'),
    path('buyer/profile/', buyerProfileRetrieveView.as_view(), name='buyer-profile-create'),
    path('seller/profile/update/', SellerProfileUpdateView.as_view(), name='seller-profile-update'),
    path('Buyer/profile/create', BuyerProfileCreateView.as_view(), name='Buyer-profile-update'),
    path('Buyer/profile/update/', BuyerProfileUpdateView.as_view(), name='Buyer-profile-create'),
    path('seller/profile/create/', SellerProfileCreateView.as_view(), name='create-seller-profile'),
    path('transactions/buyer/', BuyerTransactionListView.as_view(), name='buyer-transaction-list'),
    path('transactions/seller/', SellerTransactionListView.as_view(), name='seller-transaction-list'),
    path('payment/initialize/', PaymentInitializeView.as_view(), name='payment-initialize'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]

