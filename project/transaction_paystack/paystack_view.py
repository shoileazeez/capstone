from rest_framework import status
import uuid
from rest_framework.response import Response
from rest_framework.views import APIView  # Adjust the import path as necessary
from project.serializers import PaymentInitializeSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from project .models import Transaction, Product,Cart,CartItem
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from project.permissions import IsBuyer
from project.models import Cart
from project.transaction_paystack.paystck import Paystack,PaymentProcessor # Adjust this path according to your structure
from django.conf import settings




class PaymentInitializeView(APIView):
    def post(self, request):
        serializer = PaymentInitializeSerializer(data=request.data)
        
        if serializer.is_valid():
            email = request.user.email  # Automatically fetch the user's email
            cart_id = serializer.validated_data['cart_id']  # Get the cart_id from the validated data
            buyer = request.user
            
            try:
                # Retrieve the cart using the cart ID and calculate the amount
                cart = Cart.objects.get(id=cart_id)
                for item in cart.cart_items.all():
                    product = item.product
                    if item.quantity > product.stock_quantity:
                        return Response(
                            {"error": f"Not enough stock for product {product.name}. Available: {product.stock_quantity}, Requested: {item.quantity}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                amount = int(cart.get_cart_total() * 100)  # Convert amount to kobo (Naira in kobo)

                # Generate a unique reference if not provided
                reference = serializer.validated_data.get('reference') or str(uuid.uuid4())
                callback_url = "http://project.eu-north-1.elasticbeanstalk.com/api/project/payment/callback/"

                # Call Paystack to initialize payment
                response = Paystack.initialize_payment(email, amount, reference, callback_url, request)
                
                for item in cart.cart_items.all():
                    # Assuming you have a CartItem model
                    product = item.product  # Access the product associated with the cart item
                    seller = product.seller
                    
                transaction = Transaction.objects.create(
                    reference=reference,
                    amount=amount / 100,
                    cart=cart,
                    seller=seller,
                    buyer=buyer,  # If you have a user field
                    status='pending',  # or whatever status is appropriate
                )

                # Handle errors in the Paystack API response
                if 'error' in response:
                    return Response({'error': response['error']}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the response status is successful
                if response.get('status'):
                    for item in cart.cart_items.all():
                        product = item.product
                        product.stock_quantity -= item.quantity
                        product.save()
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            # Handle case where the cart is not found
            except Cart.DoesNotExist:
                return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Handle general exceptions
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # If serializer is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    
@method_decorator(csrf_exempt, name='dispatch')
@permission_classes ([IsAuthenticated, IsBuyer])
class PaymentCallbackView(APIView):
    def post(self, request):
        data = request.data
        print("Received callback data:", data) 
        print("Received query parameters:", request.GET)  # Log the query parameters
        
        
        reference = request.GET.get('reference')
        if not reference:
            return Response({"error": "Reference not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the payment with Paystack
        verification_response = Paystack.verify_payment(reference)
        
        print(f"Looking for transaction with reference: {reference}")  # Debugging log

        if verification_response['status']:
            payment_data = verification_response['data']
            # Retrieve the transaction associated with the reference
            try:
                transaction = Transaction.objects.get(reference=reference)
                print(f"Transaction found: {transaction}")
            except Transaction.DoesNotExist:
                return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if transaction is already processed
            if transaction.status in ['completed', 'failed']:
                return Response({"error": "Transaction already processed"}, status=status.HTTP_400_BAD_REQUEST)

            # Update transaction based on payment status
            if payment_data['status'] == 'success':
                transaction.status = 'completed'
                transaction.amount_paid = payment_data.get('amount', 0) / 100  # Optional: Store the actual amount paid
                transaction.save()

                # Handle successful payment logic
                self.handle_successful_payment(transaction)

                return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)

            else:
                transaction.status = 'failed'
                transaction.save()
                return Response({"message": "Payment failed"}, status=status.HTTP_200_OK)

        return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_successful_payment(self, transaction):
        print(f"Processing transaction: {transaction.reference}, Status: {transaction.status}")
        
        if not transaction.cart:
            raise ValueError("Transaction is not linked to a cart.")
        
        cart_items = transaction.cart.cart_items.all()
        
        buyer = transaction.buyer
        buyer_email = buyer.email
        platform_fee_percentage = settings.PLATFORM_FEE_PERCENTAGE / 100 
        # Example: 5% platform fee

        # Distribute payments among sellers
        PaymentProcessor.distribute_payments(
            cart_items=cart_items,
            buyer_email=buyer_email,
            buyer=buyer,
            platform_fee_percentage=platform_fee_percentage,
            
        )
        
        
        
        

    