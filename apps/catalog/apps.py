from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """
    Конфигурация приложения catalog.

    Отвечает за:
    - регистрацию приложения в Django
    - подключение сигналов (signals)

    При инициализации приложения (метод ready)
    импортируются обработчики сигналов, чтобы:
    - автоматически пересчитывать рейтинг товара
    - обновлять количество отзывов при изменениях
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    verbose_name = "Каталог"

    def ready(self):
        import apps.catalog.signals  # noqa
