from datetime import date
from celery import shared_task
from .models import EquipmentBooking


@shared_task
def delete_expired_booking():
    expired_booking = EquipmentBooking.objects.filter(booking_date_to__lt=date.today())
    expired_booking.delete()



