from django.contrib import admin
from .models import Profile , Product , Category, Cart, CartItem, SellerProfile, Transaction,BuyerProfile

class CategoryAdmin(admin.ModelAdmin):
    list_display =  ['category']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [ 'reference', 'created_at', 'status']

@admin.register(BuyerProfile)
class BuyerprofileAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'address', 'phone']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [ 'buyer', 'created_at']

@admin.register(SellerProfile)
class SellerProfileadmin(admin.ModelAdmin):
    list_display = ('user', 'bank_code', 'account_number', 'account_name', 'profile_photo')  # Display fields in the list view
    search_fields = ('user__username', 'bank_code', 'account_number')  # Add search functionality
    list_filter = ('bank_code',) 
    
    
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [ 'product','quantity', 'cart']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'category', 'seller']
    search_fields = ['name', 'category']
    list_filter = [ 'category']
    search_fields = ('name', 'category__category')
    
     
admin.site.register(Profile)

admin.site.register(Category, CategoryAdmin)
# Register your models here.
