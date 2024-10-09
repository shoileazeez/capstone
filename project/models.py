from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from rest_framework.exceptions import ValidationError

class Profile(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_completed = models.BooleanField(default=False) 
    role_set_once = models.BooleanField(default=False)  

    def __str__(self):
        return self.username

class BuyerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    # Optional: If you want to directly store profile photos in SellerProfile
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # If profile_photo is set in SellerProfile, update the User's profile_photo
        if self.profile_photo:
            self.user.profile_photo = self.profile_photo
            self.user.save(update_fields=['profile_photo'])  # Save only the profile_photo field in User
        
        super().save(*args, **kwargs)  # Call the parent class's save method
        
    def __str__(self):
        return self.user.username    
    

class SellerProfile(models.Model):
    
    
    BANK_CHOICES = [
        ("011", "First Bank of Nigeria"),
        ("404",  "Abbey Mortgage Bank"),
        ("044", "Access Bank"),
        ("058", "Guaranty Trust Bank"),
        ("215", "Unity Bank"),
        ("221", "Stanbic IBTC Bank"),
        ("100",  "Suntrust BanK"),
        ("232", "Sterling Bank"),
        ("033", "United Bank for Africa"),
        ("035", "Wema Bank"),
        ("082", "Keystone Bank"),
        ("101", "Providus Bank"),
        ("102", "Suntrust Bank"),
        ("103", "Titan Trust Bank"),
        ("232", "Sterling Bank"),
        ("999992", "Opay"),
        ("50211", "Kuda Bank"),
        ("100002", "Paga"),
        ("076", "Polaris Bank"),
        ("104",  "parallex Bank"),
        ("50515", "Moniepoint MFB"),
        ("214",  "First City Monument Bank"),
        ("999991", "PalmPay"),
        ("033", "CitiBank Nigeria"),
        ("059", "JPMorgan Chase Bank"),
        ("070", "Fidelity Bank"),
        ("057", "Zenith Bank"),
        ("068", "Standard Chartered Bank"),
        ('000001', 'Test Bank 1'),
        ('000002', 'Test Bank 2'),
        ('000003', 'Test Bank 3'),
        ('301',  'Jaiz Bank'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    paystack_recipient_code = models.CharField(max_length=255, blank=True, null=True) 
    bank_code = models.CharField(max_length=10, choices=BANK_CHOICES,  blank=True, null=True)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=255)
    
    # Optional: If you want to directly store profile photos in SellerProfile
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # If profile_photo is set in SellerProfile, update the User's profile_photo
        if self.profile_photo:
            self.user.profile_photo = self.profile_photo
            self.user.save(update_fields=['profile_photo'])  # Save only the profile_photo field in User
        
        super().save(*args, **kwargs)  # Call the parent class's save method
    
    def get_bank_name(self):
        # Fetch the human-readable bank name from the bank code
        return dict(self.BANK_CHOICES).get(self.bank_code, "Unknown bank")

    def __str__(self):
        return self.user.username

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('cloth', 'Cloth'),
        ('electronics', 'Electronics'),
        ('shoes', 'Shoes'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.category 

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_image = models.ImageField(upload_to='product_photos/', blank=True, null=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the object already exists (i.e., it's an update)
            original = Product.objects.get(pk=self.pk)
            if original.category != self.category:  # Prevent category change
                raise ValidationError("You cannot change the category after the product is created.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name  # Return the product name for better readability
    
    @property
    def formatted_price(self):
        """Return the price formatted with a currency symbol."""
        return f"₦{self.price:.2f}"
    
    def is_in_stock(self, quantity):
        """Check if there is enough stock for the requested quantity."""
        return self.stock_quantity >= quantity

    def reduce_stock(self, quantity):
        """
        Reduce the product stock after successful payment.
        """
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
        else:
            raise ValueError("Insufficient stock to fulfill the order.")
    
class Cart(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goods')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def get_cart_total(self):
        """Calculate the total price for all items in the cart."""
        return sum(item.get_total_price() for item in self.cart_items.all())
        

    def __str__(self):
        return f"Cart of {self.buyer.username}"
    
# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        """Calculate the total price for this cart item."""
        if self.product.price is not None and self.quantity is not None:
            return self.product.price * self.quantity
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # Status could be 'pending', 'paid', 'canceled', etc.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total_amount(self):
        """Calculate total amount for all items in the order."""
        return sum(item.get_total_price() for item in self.order_items.all())

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"

# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        """Calculate total price for this item."""
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"    
    
    
        
class Transaction(models.Model):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_transactions')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_transactions')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='transactions', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    buyer_email = models.EmailField(null=True) 
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    seller_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Transaction {self.reference} - {self.status}"