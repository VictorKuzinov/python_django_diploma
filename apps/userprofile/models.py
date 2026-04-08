from django.contrib.auth.models import User
from django.db import models


class Avatar(models.Model):
    """
    Модель аватара пользователя.

    Хранит изображение аватара и текстовое описание.
    Изображение сохраняется в каталоге media/avatars/.

    Используется в модели Profile как внешний ключ.
    """

    src = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        verbose_name="Файл изображения",
    )

    alt = models.CharField(max_length=128, verbose_name="Описание изображения")

    class Meta:
        verbose_name = "Аватар"
        verbose_name_plural = "Аватары"

    def __str__(self):
        """
        Строковое представление объекта аватара.
        """
        return self.alt


class Profile(models.Model):
    """
    Модель профиля пользователя.

    Расширяет стандартную модель Django User
    дополнительной информацией о пользователе:

    - полное имя
    - телефон
    - баланс
    - аватар

    Каждый пользователь имеет ровно один профиль.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )

    fullName = models.CharField(max_length=128, verbose_name="Полное имя")

    phone = models.CharField(
        max_length=20, unique=True, blank=True, null=True, verbose_name="Номер телефона"
    )

    balance = models.DecimalField(
        decimal_places=2, max_digits=10, default=0, verbose_name="Баланс пользователя"
    )

    avatar = models.ForeignKey(
        Avatar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
        verbose_name="Аватар",
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        """
        Строковое представление профиля пользователя.
        """
        return self.fullName
