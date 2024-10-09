import requests
from django.conf import settings
from project.models import Product, Transaction
from django.core.mail import send_mail
import json
from project.models import SellerProfile
from django.shortcuts import get_object_or_404
from decimal import Decimal
import uuid

class Paystack:
    @staticmethod
    def initialize_payment(email, amount, reference, callback_url,request):
        url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        callback_url = settings.PAYSTACK_CALLBACK_URL

        payload = {
        'email': email,
        'amount': amount,
        'reference': reference,
        'callback_url': callback_url,
    }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an error for bad HTTP responses (4xx/5xx)
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # For logging
            return {'error': 'HTTP error occurred'}
        except Exception as err:
            print(f"Other error occurred: {err}")  # For logging
            return {'error': 'Something went wrong'}

        try:
            # Ensure we have valid JSON before trying to decode it
            return response.json()
        except ValueError:
            print("Invalid JSON response received")  # For logging
            return {'error': 'Invalid JSON response from Paystack'}

        # response = requests.post(url, json=payload, headers=headers)
        # return response.json()

    @staticmethod
    def verify_payment(reference):
        url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        response = requests.get(url, headers=headers)
        return response.json()

class PaymentProcessor:

    @staticmethod
    def distribute_payments(cart_items, buyer, buyer_email, platform_fee_percentage):
        sellers_payments = {}
        total_amount = 0
        
        

        for item in cart_items:
            product = item.product  # Assuming `cart_items` contains CartItem objects directly
            seller = product.seller.sellerprofile
            quantity = item.quantity
            product_total_price = Decimal(product.price) * Decimal(quantity)
            total_amount += product_total_price

            # Calculate platform fee and seller share
            
            seller_share = product_total_price

            # Store the seller payments
            if seller.id not in sellers_payments:
                sellers_payments[seller.id] = {
                    'seller': seller,
                    'total_amount': 0,
                    'products': [],
                    # 'platform_fee': platform_fee,  # Store platform fee per seller
                }
            
            sellers_payments[seller.id]['total_amount'] += seller_share
            sellers_payments[seller.id]['products'].append({
                'product_id': product.id,
                'product_name': product.name,
                'quantity': quantity,
                'amount': seller_share,
            })
            
            
            platform_fee = total_amount * Decimal(platform_fee_percentage)
            total_after_fee = total_amount - platform_fee
            print(f"Total amount: {total_amount}, Platform fee: {platform_fee}, Total after fee: {total_after_fee}")

        transfers = []
        transactions = []
        for seller_data in sellers_payments.values():
            seller = seller_data['seller']
            seller_share = seller_data['total_amount']
            
           

            if seller_data['total_amount'] is not None:
                seller_share_after_fee = (seller_share / total_amount) * total_after_fee if total_amount > 0 else Decimal(0)
                seller_total_amount = int(seller_share_after_fee * 100)
                reference = f"ref_{str(uuid.uuid4())[:8]}",
            else:
                print(f"Invalid total amount for seller {seller}")
                continue
            print(f'{seller_total_amount},{reference}')# Paystack uses kobo

            # Check if recipient code exists, else create it
            if not seller.paystack_recipient_code:
                recipient_response = PaymentProcessor.create_transfer_recipient(
                    name=seller.account_name,
                    account_number=seller.account_number,
                    bank_code=seller.bank_code
                )
                try:
                    recipient_response = PaymentProcessor.parse_response(recipient_response)
                    PaymentProcessor.validate_status(recipient_response)
                    if 'data' in recipient_response:
                        recipient_code = PaymentProcessor.extract_recipient_code(recipient_response)
                        seller.paystack_recipient_code = recipient_code
                        seller.save()
                        print(f"{recipient_code}")
                        print(f"{recipient_response}")
                    else:
                        print(f"Warning: Response does not contain 'data': {recipient_response}")
                        continue  # Skip to the next seller if no recipient code is provided    
                except ValueError as e:
                    print(f"Error creating recipient: {e}")
                    continue  # Skip this seller if there's an error

            # Prepare transfers for Paystack
            transfers = [
                {
                'amount': seller_total_amount,
                'recipient': seller.paystack_recipient_code,
                'reference': reference,
                
            }]
            print(f"{seller_total_amount}")
            print(f"Seller total amount: {seller_total_amount}, Type: {type(seller_total_amount)}")


            # Create transaction for record-keeping
            seller_obj = get_object_or_404(SellerProfile, id=seller.id)
            transaction = Transaction(
                buyer=buyer,
                buyer_email=buyer_email,
                seller=seller_obj.user,
                cart=item.cart,  
                amount=seller_total_amount,
                platform_fee=platform_fee,
                seller_share=seller_share_after_fee,
                reference=reference,  # Include the cart/order ID for reference
                status='pending'  # Initially set as pending
                
            )
            print(f'seller total amount is :{seller_total_amount}')
            transactions.append(transaction)

        # Initiate the bulk transfer to Paystack
        bulk_transfer_response = PaymentProcessor.initiate_bulk_transfer(transfers)

        # Handle bulk transfer response
        if not bulk_transfer_response.get('status'):
            print(f"Bulk transfer failed: {bulk_transfer_response.get('message')}")
            print(f"Full response: {bulk_transfer_response}")
        else:
            print("Bulk transfer successful")

        # Save transactions after bulk transfer
        for transaction in transactions:
            try:
                transaction.save()
                print("Transaction created successfully.")
            except Exception as e:
                print(f"Error saving transaction: {e}")
                
        for item in cart_items:
            item.delete()  # Delete each cart item
            print(f"Deleted cart item: {item.id}")        

        # Send confirmation emails
        PaymentProcessor.send_confirmation_emails(cart_items, buyer, sellers_payments, platform_fee_percentage)

        return bulk_transfer_response

    @staticmethod
    def create_transfer_recipient(name, account_number, bank_code):
        url = f"{settings.PAYSTACK_BASE_URL}/transferrecipient"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        payload = {
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "NGN",
        }
        
        

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get("message", "Failed to create transfer recipient")

    @staticmethod
    def initiate_bulk_transfer(transfers):
        url = f"{settings.PAYSTACK_BASE_URL}/transfer/bulk"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        payload = {
            "source": "balance",
            "transfers": transfers,
        }
        # Log the payload before sending
        print(f"Initiating transfer with payload: {payload}")


        response = requests.post(url, json=payload, headers=headers)
        print(f"Paystack response: {response.json()}")
        return response.json()
    
    @staticmethod
    def parse_response(response):
        print(f"Raw response received: {response}")
        if not response:
            raise ValueError("Empty or None recipient response received")
        if isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                if "Transfer recipient created successfully" in response:
                    return {'status': 'success', 'message': response}
                else:
                    raise ValueError("Invalid JSON string format: Unable to parse JSON.")
        if isinstance(response, dict):
            return response
    
    # Handle any other types of responses (list, etc.)
        raise ValueError(f"Unexpected response type: {type(response)}")





    @staticmethod
    def validate_status(response):
        if not response.get('status'):
            raise ValueError(f"Failed to create recipient: {response.get('message', 'Unknown error')}")
        return response

    @staticmethod
    def extract_recipient_code(response):
        if 'data' in response and isinstance(response['data'], dict):
            recipient_code = response['data'].get('recipient_code')
            if recipient_code is None:
                raise ValueError("Recipient code is missing")
            return recipient_code
        else:
            raise ValueError("Response does not contain 'data': " + str(response))

    @staticmethod
    def send_confirmation_emails(cart_items, buyer, sellers_payments, platform_fee_percentage):
        for seller_data in sellers_payments.values():
            seller = seller_data['seller']
            seller_products = seller_data['products']
            total_seller_amount = seller_data['total_amount']  # This is the total amount before fees
            platform_fee = total_seller_amount * Decimal(platform_fee_percentage / 100)
            seller_share_after_fee = total_seller_amount - platform_fee

        # Create the email content with product details
            product_details = "\n".join([f"Product ID: {p['product_id']}, Product Name: {p['product_name']}, "
                                     f"Quantity: {p['quantity']}, Amount: {p['amount']}" for p in seller_products])

        # Email content for the seller
            subject = "Payment Confirmation"
            message = (f"Hello {seller.user.first_name},\n\n"
                   f"This is a confirmation of your recent transaction. Below are the details of the products sold:\n"
                   f"{product_details}\n\n"
                   f"Total Amount Before Fees: {total_seller_amount}\n"
                   f"Platform Fee ({platform_fee_percentage}%): {platform_fee}\n"
                   f"Your Share After Fees: {seller_share_after_fee}\n\n"
                   f"Thank you for using our platform.\n"
                   f"Best regards,\n"
                   f"Your Company")
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # From email
                [seller.user.email],  # To email
                fail_silently=False
        )
        buyer_subject = "Order Confirmation"
        buyer_message = (f"Hello {buyer.first_name},\n\n"
                     f"Thank you for your order. Here are the details:\n"
                     f"{product_details}\n\n"
                     f"Best regards,\n"
                     f"Your Company")
        send_mail(
            buyer_subject,
            buyer_message,
            settings.DEFAULT_FROM_EMAIL,  # From email
            [buyer.email],  # To email
            fail_silently=False
    )