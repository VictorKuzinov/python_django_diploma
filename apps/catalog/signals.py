from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Review


def _recalculate_product_rating(product):
    """
    Пересчитывает количество отзывов и рейтинг товара.
    """
    reviews = product.reviews_list.all()

    product.reviews = reviews.count()

    avg_rating = reviews.aggregate(avg=Avg("rate"))["avg"]
    product.rating = float(avg_rating) if avg_rating is not None else 0

    product.save(update_fields=["reviews", "rating"])


@receiver(post_save, sender=Review)
def update_product_on_save(sender, instance, **kwargs):
    """
    Обработчик сигнала post_save для Review.
    """
    _recalculate_product_rating(instance.product)


@receiver(post_delete, sender=Review)
def update_product_on_delete(sender, instance, **kwargs):
    """
    Обработчик сигнала post_delete для Review.
    """
    _recalculate_product_rating(instance.product)
