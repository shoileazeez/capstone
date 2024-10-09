from project.models import Cart
from celery import shared_task
from datetime import timedelta
from django.utils import timezone

@shared_task
def cancel_unpaid_orders():
    """
    Cancel orders that are still pending after one hour.
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    unpaid_orders = Cart.objects.filter(status='pending', created_at__lt=one_hour_ago)

    for order in unpaid_orders:
        order.cancel_if_not_paid()