from rest_framework import serializers
from .models import Profile, Category, Product,Cart, CartItem, SellerProfile, Transaction, BuyerProfile
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from project.transaction_paystack.paystck import Paystack

User = get_user_model()

class completeregistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'email', 'first_name', 'last_name','role', 'is_completed']
        read_only_fields = ['is_completed', 'email', 'username']

    def update(self, instance, validated_data):
        if instance.role_set_once and 'role' in validated_data:
            raise serializers.ValidationError("Role can only be set once and cannot be changed.")
        if instance.is_completed:
            raise serializers.ValidationError("Profile has already been completed and cannot be edited.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if 'role' in validated_data:
            instance.role_set_once = True

        # Save the instance
        instance.save()
        return instance
               
class buyerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only = True)
    username = serializers.CharField(source='user.username',read_only = True)
    password = serializers.CharField(source='user.password', read_only = True)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(source='user.first_name', required=True)
    last_name = serializers.CharField(source='user.last_name', required=True)
    
    class Meta:
        model = BuyerProfile
        fields = ['username', 'email', 'password', 'profile_photo', 'first_name', 'last_name','address', 'phone']
        read_only_fields = ['role', 'username', 'email']
        
        
    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Resolve lazy user object if it exists
        if isinstance(self.context['request'].user, SimpleLazyObject):
            user = User.objects.get(id=self.context['request'].user.id)  # Ensure user is resolved
        else:
            user = self.context['request'].user
            
        # Use existing user if already created
        Buyer_profile = BuyerProfile.objects.create(user=user, **validated_data)  # Create seller profile
        return {"profile created successfully"}
    
    def to_representation(self, instance):
        """Customize the output representation."""
        representation = super().to_representation(instance)
        representation.pop('password', None)  # Remove the price from the output representation
        return representation
    
class SellerProfileCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only = True)
    username = serializers.CharField(source='user.username', read_only = True)
    first_name = serializers.CharField(source='user.first_name', required=True)
    last_name = serializers.CharField(source='user.last_name', required=True)
    profile_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = SellerProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_photo', 'bank_code', 'account_number', 'account_name']
        read_only_fields = ['role', 'username', 'email']
    def validate_account_number(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Account number must be exactly 10 digits long.")
        if not value.isdigit():
            raise serializers.ValidationError("Account number must contain only numeric digits.")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Resolve lazy user object if it exists
        if isinstance(self.context['request'].user, SimpleLazyObject):
            user = User.objects.get(id=self.context['request'].user.id)  # Ensure user is resolved
        else:
            user = self.context['request'].user
            
          

        # Use existing user if already created
        seller_profile = SellerProfile.objects.create(user=user, **validated_data)  # Create seller profile
        return {"profile created successfully"}
    
class SellerProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', read_only=True)  # Read-only for email
    username = serializers.CharField(source='user.username', read_only=True)  # Read-only for username
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = SellerProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_photo', 'role', 'bank_code', 'account_number', 'account_name']
        read_only_fields = ['role']

    def validate_account_number(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Account number must be exactly 10 digits long.")
        if not value.isdigit():
            raise serializers.ValidationError("Account number must contain only numeric digits.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Update user details
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.save()  # Save the user instance

        # Update seller profile details
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.bank_code = validated_data.get('bank_code', instance.bank_code)
        instance.account_number = validated_data.get('account_number', instance.account_number)
        instance.account_name = validated_data.get('account_name', instance.account_name)
        
        if instance.account_number and instance.bank_code:
            paystack_response = Paystack.create_transfer_recipient(
                name=instance.account_name or instance.user.username,  # Use account name if available
                account_number=instance.account_number,
                bank_code=instance.bank_code
            )
            if paystack_response['status']:
                instance.paystack_recipient_code = paystack_response['data']['recipient_code']
                instance.save()
        return instance  

        instance.save()  # Save the seller profile instance
        return instance    

class BuyerProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', read_only=True)  # Read-only for email
    username = serializers.CharField(source='user.username', read_only=True)  # Read-only for username
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = BuyerProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_photo', 'role', 'address', 'phone']
        read_only_fields = ['role']


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Update user details
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.save()  # Save the user instance

        # Update buyer profile details
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)

        instance.save()  # Save the seller profile instance
        return instance    
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = Profile  # Custom user model
        fields = ['username', 'email', 'password', 'password_confirm']

    # Custom validation for email uniqueness
    def validate_email(self, value):
        """Check if email is already in use."""
        if Profile.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    # Custom validation to check if passwords match
    def validate(self, data):
        """Check that the passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        # Remove the password_confirm field as it's not needed for user creation
        validated_data.pop('password_confirm')

        # Create the user with the provided data and hash the password
        user = Profile(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user
    
class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price',  'product_image','category']
        read_only_fields = [ 'price',]
        
    def get_seller(self, obj):
        return obj.seller.name
    
    def get_seller(self, obj):
        # Append " store" to the seller's name
        return f"{obj.seller} store"    
    def get_price(self, obj):
        # Format price with Naira symbol
        return f"₦{obj.price}"
    
class ProductUpdateSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    formatted_price = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'formatted_price' ,'category', 'seller', 'stock_quantity']
        read_only_fields = ['category', 'seller',]
    
    def get_formatted_price(self, obj):
        """Return the price formatted with the Naira symbol."""
        return f"₦{obj.price:.2f}"  # Format the price with Naira symbol
    
    def get_seller(self, obj):
        return obj.seller.name
    
    def to_representation(self, instance):
        """Customize the output representation."""
        representation = super().to_representation(instance)
        representation.pop('price', None)  # Remove the price from the output representation
        return representation
    
    def get_seller(self, obj):
        # Append " store" to the seller's name
        return f"{obj.seller} store"   
        
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'seller', 'product_image', 'stock_quantity']
        read_only_fields = ['seller']
        category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
        formatted_price = serializers.SerializerMethodField()
        
    def get_formatted_price(self, obj):
        return obj.formatted_price()
    
    def get_seller(self, obj):
        # Append " store" to the seller's name
        return f"{obj.seller} store"
        
class ProductDetailSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'seller', 'stock_quantity', 'product_image',]
        read_only_fields = ['category', 'price','seller']
        
    def get_price(self, obj):
        # Format price with Naira symbol
        return f"₦{obj.price}"
    
    def get_seller(self, obj):
        return obj.seller.name
    
    def get_seller(self, obj):
        # Append " store" to the seller's name
        return f"{obj.seller} store"   
    
class CategorySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'category'] 
        
class ProductHistoryOverviewSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'created_at', 'updated_at'] 
        
class SellerProductHistorySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock_quantity', 'created_at', 'updated_at']                 
        
class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    total_price = serializers.SerializerMethodField()
    price_per_item = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['product', 'price_per_item','quantity', 'total_price']

    def get_price_per_item(self, obj):
        return f"₦{obj.product.price:,.2f}"  

    def get_total_price(self, obj):
        total = obj.product.price * obj.quantity
        return f"₦{total:,.2f}"  

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    overall_total_price = serializers.ReadOnlyField(source='get_cart_total')

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'overall_total_price']
        
    def get_overall_total_price(self, obj):
        total = obj.get_cart_total()
        return f"₦{total:,.2f}"  # Format as currency
    
    
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        """Ensure the product exists and has enough stock."""
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if product.stock_quantity < data['quantity']:
            raise serializers.ValidationError("Not enough stock available.")
        
        return data

    def create(self, validated_data):
        """Add the product to the cart and update stock."""
        user = self.context['request'].user
        cart, created = Cart.objects.get_or_create(buyer=user)
        product = Product.objects.get(id=validated_data['product_id'])

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += validated_data['quantity']
        else:
            cart_item.quantity = validated_data['quantity']
        cart_item.save()        
    

class BuyerTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'status', 'created_at', 'reference', 'cart']  # Exclude seller details

class SellerTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'status', 'created_at', 'reference', 'cart']  # Exclude buyer details
        
        
class PaymentInitializeSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False)  # Optional, auto-generate if not provided
    cart_id = serializers.IntegerField(required=True)
    
    def validate_cart_id(self, value):
        try:
            # Ensure the cart exists
            cart = Cart.objects.get(id=value)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart not found.")
        return value

    def create(self, validated_data):
        # You can add logic here if needed for creating payment objects, etc.
        return validated_data
  

class PaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=255)        