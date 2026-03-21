from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

from .models import Review


@receiver(post_save, sender=Review)
def update_product_on_save(sender, instance, **kwargs):
    product = instance.product
    reviews = product.reviews_list.all()

    product.reviews = reviews.count()

    avg_rating = reviews.aggregate(avg=Avg("rate"))["avg"]
    product.rating = float(avg_rating) if avg_rating is not None else 0

    product.save(update_fields=["reviews", "rating"])


@receiver(post_delete, sender=Review)
def update_product_on_delete(sender, instance, **kwargs):
    product = instance.product
    reviews = product.reviews_list.all()

    product.reviews = reviews.count()

    avg_rating = reviews.aggregate(avg=Avg("rate"))["avg"]
    product.rating = float(avg_rating) if avg_rating is not None else 0

    product.save(update_fields=["reviews", "rating"])