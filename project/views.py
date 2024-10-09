from django.shortcuts import render
from rest_framework import generics
from . import serializers
from .models import Profile , Product, CartItem, Cart, SellerProfile, Transaction, BuyerProfile
from .serializers import  UserRegistrationSerializer, ProductSerializer, ProductListSerializer, ProductDetailSerializer, ProductUpdateSerializer , ProductHistoryOverviewSerializer, SellerProductHistorySerializer,BuyerProfileUpdateSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from project.transaction_paystack.paystck import Paystack
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CartSerializer, AddToCartSerializer, SellerProfileCreateSerializer, completeregistrationSerializer, buyerProfileSerializer, SellerProfileUpdateSerializer, BuyerTransactionSerializer, SellerTransactionSerializer, PaymentVerifySerializer
from django.contrib.auth import authenticate,login, logout
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as filters
from .permissions import IsSeller, IsBuyer , IsOwnerOrReadOnly
from .filters import ProductFilter, DateFilter
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from project.transaction_paystack import paystck
from datetime import datetime
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied
from django.http import Http404


# User Registration View
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'message': 'User registered successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CompleteRegistrationView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = completeregistrationSerializer

    def get_object(self):
        return self.request.user  # self.request.user will be an instance of Profile

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.role_set_once:
            return Response({"detail": "Role can only be set once and cannot be changed."}, status=400)
        if instance.is_completed:
            return Response({"detail": "user registrtion can only be compelete once and cannot be changed."}, status=400)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if not instance.is_completed:
            instance.is_completed = True 
            instance.save()
        
        return Response(serializer.data)

class SellerProfileRetrieveView(generics.RetrieveAPIView):
    serializer_class = SellerProfileCreateSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get_object(self):
        user = self.request.user
        
        # Check if the user has the seller role
        if user.role != 'seller':
            raise PermissionDenied("You do not have permission to access this profile.")
        
        try:
            # Try to get the SellerProfile for the authenticated user
            seller_profile = SellerProfile.objects.get(user=user)
            return seller_profile
        except SellerProfile.DoesNotExist:
            raise Http404("Seller Profile not found.")

class buyerProfileRetrieveView(generics.RetrieveAPIView):
    serializer_class = buyerProfileSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_object(self):
        user = self.request.user
        
        # Check if the user has the buyer role
        if user.role != 'buyer':
            raise PermissionDenied("You do not have permission to access this profile.")
        
        try:
            # Try to get the buyerprofile for the authenticated user
            Buyer_profile = BuyerProfile.objects.get(user=user)
            return Buyer_profile
        except BuyerProfile.DoesNotExist:
            raise Http404("Buyer profile not found.")

class SellerProfileCreateView(generics.CreateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileCreateSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    
    def create(self, request, *args, **kwargs):
        user = request.user
        
        # Check if the user already has a seller profile
        try:
            # Attempt to retrieve the existing seller profile
            existing_profile = SellerProfile.objects.get(user=user)
            return Response({"detail": "You already have a seller profile."}, status=status.HTTP_400_BAD_REQUEST)
        except SellerProfile.DoesNotExist:
            # If it does not exist, proceed to create it
            pass

        # Create a new seller profile
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)  # Associate the created profile with the user

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Create the SellerProfile associated with the authenticated user
        # serializer.save(user=user)

class SellerProfileUpdateView(generics.UpdateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get_object(self):
        user = self.request.user
        return user.sellerprofile  # Assuming OneToOne relationship is set

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # Get the SellerProfile instance for the authenticated user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
class BuyerProfileCreateView(generics.CreateAPIView):
    queryset = BuyerProfile.objects.all()
    serializer_class = buyerProfileSerializer
    permission_classes = [IsAuthenticated, IsBuyer]
    
    def perform_create(self, serializer):
        user = self.request.user
        # Ensure no duplicate profiles for the same user
        if not BuyerProfile.objects.filter(user=user).exists():
            serializer.save(user=user)
        else:
            return Response(
                {'error': 'Profile already exists for this user'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new seller profile
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save(user=user)  # Associate the created profile with the user

        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class BuyerProfileUpdateView(generics.UpdateAPIView):
    queryset = BuyerProfile.objects.all()
    serializer_class = BuyerProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsBuyer]
    
    def get_object(self):
        # Fetch the profile of the logged-in user
        return get_object_or_404(BuyerProfile, user=self.request.user)

    def perform_update(self, serializer):
        # Perform the update if needed, but it's usually handled by the serializer
        serializer.save()

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Get the token of the current user
        user = request.user  # Get the authenticated user
        try:
            # Get the user's token
            token = Token.objects.get(user=user)  # Retrieve the token associated with the user
            if token:
                token.delete()  # Delete the token
                logout(request)  # Invalidate the session
                return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Token not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ProductPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100        
        
class ProductListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly] 
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,SearchFilter)
    filterset_class = ProductFilter 
    filterset_fields = ['category__category']
    search_fields = ['name', 'category__category']  # Search by name and category
    pagination_class = ProductPagination
    
    
    def get_queryset(self):
        """
        Optionally filter products by category if the 'category' query parameter is provided.
        """
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__category=category)
        return queryset

class ProductCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsSeller] 
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    
    def perform_create(self, serializer):
        # Set the current user as the owner of the product
        serializer.save(seller=self.request.user)

class ProductUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsSeller, IsOwnerOrReadOnly] 
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    
    def perform_update(self, serializer):
        # Any additional logic before saving can be added here
        serializer.save()  # Save the updated product
 
class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsSeller, IsOwnerOrReadOnly] 
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    
class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer 
    lookup_field = 'id'     
# Create your views here.



  
class SellerProductHistoryView(generics.ListAPIView):
    serializer_class = ProductHistoryOverviewSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = DateFilter
    search_fields = ['name', 'category__category']  
    pagination_class = ProductPagination

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-created_at')    
    def validate_date(self, year, month=None, day=None):
        current_year = datetime.now().year

        if year and int(year) > current_year:
            raise ValueError("The year cannot be in the future.")
        
        if year and month and day:
            try:
                date = datetime(int(year), int(month), int(day))
                if date > datetime.now():
                    raise ValueError("The date cannot be in the future.")
            except ValueError:
                raise ValueError("Invalid date provided.")
    
    def list(self, request, *args, **kwargs):
        # Retrieve query parameters
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        day = request.query_params.get('day')

        try:
            # Validate date if year is provided
            if year:
                self.validate_date(year, month, day)

            # Proceed with normal filtering if validation passes
            return super().list(request, *args, **kwargs)

        except ValueError as e:
            # Handle validation error and return a response with the error message
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
class ProductHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = SellerProductHistorySerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get_queryset(self):
        # Return only the products of the authenticated seller
        return Product.objects.filter(seller=self.request.user)

    def get_object(self):
        obj = super().get_object()
        # Ensure the product belongs to the authenticated seller
        if obj.seller != self.request.user:
            raise PermissionDenied("You do not have permission to view this product's details.")
        return obj    

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_object(self):
        """Retrieve the cart for the authenticated buyer."""
        user=self.request.user
        cart, created = Cart.objects.get_or_create(buyer=user)
        return cart
    
    
@method_decorator(csrf_exempt, name='dispatch')
class AddToCartView(generics.CreateAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def perform_create(self, serializer):
        """Handle adding an item to the cart."""
        serializer.save()

class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_object(self):
        """Find the cart item based on the buyer and product."""
        user = self.request.user
        product_id = self.kwargs.get('product_id')
        
        try:
            cart = Cart.objects.get(buyer=user)  # Get the cart for the authenticated buyer
            return CartItem.objects.get(cart=cart, product_id=product_id)  # Get the cart item
        except Cart.DoesNotExist:
            # If the cart doesn't exist, return a 404 error
            raise Http404("Cart does not exist.")
        except CartItem.DoesNotExist:
            # If the cart item doesn't exist, return a 404 error with a message
            raise Http404("Product not found in cart.")

    def perform_destroy(self, instance):
        """Remove the cart item and restore the stock."""
        product = instance.product
        product.stock_quantity += instance.quantity  # Restore the stock
        product.save()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UpdateCartItemView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer  # You can reuse the same serializer to handle updates

    def get_object(self):
        """Find the cart item based on the authenticated user and product."""
        user = self.request.user
        product_id = self.kwargs.get('product_id')
        cart = Cart.objects.get(buyer=user)
        return CartItem.objects.get(cart=cart, product_id=product_id)

    def perform_update(self, serializer):
        """Update the cart item quantity and restore or reduce stock accordingly."""
        instance = self.get_object()
        product = instance.product
        new_quantity = serializer.validated_data['quantity']

        # Check if we are increasing or decreasing the quantity
        if new_quantity > instance.quantity:
            # If increasing, check stock
            if product.stock_quantity < (new_quantity - instance.quantity):
                raise serializers.ValidationError("Not enough stock available.")
            product.stock_quantity -= (new_quantity - instance.quantity)  # Update stock accordingly
        else:
            # If decreasing, restore stock
            product.stock_quantity += (instance.quantity - new_quantity)

        product.save()  # Save product stock changes
        instance.quantity = new_quantity  # Update cart item quantity
        instance.save()  # Save changes to cart item    



class BuyerTransactionListView(generics.ListAPIView):
    serializer_class = BuyerTransactionSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user)  # Only return buyer transactions

class SellerTransactionListView(generics.ListAPIView):
    serializer_class = SellerTransactionSerializer
    permission_classes = [IsAuthenticated , IsSeller]

    def get_queryset(self):
        return Transaction.objects.filter(seller=self.request.user) 
            





from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def send_test_email_view(request):
    try:
        send_mail(
            'Test Subject',  # Subject
            'Here is the message.',  # Message body
            settings.DEFAULT_FROM_EMAIL,  # From email
            ['shoileazeez@gmail.com'],  # To email
            fail_silently=False,
        )
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Error sending email: {e}")
