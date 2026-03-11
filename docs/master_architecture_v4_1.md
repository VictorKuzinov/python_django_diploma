
# Master Architecture v4.1 — Django Diploma Backend (DRF + Frontend Contract)

> У вас проектный пакет называется **`config/`**.  
> В примере преподавателя он назывался `megano/`, но **имя пакета не важно** — важно, чтобы URL-роутинг и контракт API совпадали.

---

## 1) Основные принципы

1. **Frontend трогать нельзя.** Он поставляется как библиотека `django-frontend` (у вас в репозитории — `diploma-frontend`).
2. **Контракт API — swagger из `django-frontend/swagger/swagger.yaml`** (в GitLab рендерится для просмотра).
3. Backend возвращает/принимает данные **строго по контракту** (формат JSON/поля).
4. Все API находятся под префиксом **`/api/`** (frontend ожидает именно так).
5. Реализация делается через **Django REST Framework**, ориентируемся на **APIView** (как рекомендует преподаватель).
6. Делать проект лучше поэтапно: **одно приложение полностью → затем следующее**.

---

## 2) Реальная структура проекта (как у вас сейчас)

```
python_django_diploma/
  manage.py
  config/
    settings.py
    urls.py
    wsgi.py
    asgi.py
  apps/
    authapp/
    catalog/
    basket/
    order/
    payment/
    profile/
    tags/
  diploma-frontend/   # поставляемый пакет фронта (django-frontend)
  docs/
  requirements.txt
  .env.template
  README.md
```

> `diploma-frontend` вы устанавливаете в venv как пакет и подключаете `frontend` в `INSTALLED_APPS`.

---

## 3) Подключение frontend и API (обязательное)

Файл: `config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("frontend.urls")),
    path("api/", include("apps.api_urls")),
    path("admin/", admin.site.urls),
]
```

---

## 4) 7 приложений (как в swagger tags)

- **authapp**: `sign-in`, `sign-up`, `sign-out`
- **catalog**: `categories`, `catalog`, `product`, `review`, `banners`, `sales`, `products/popular`, `products/limited`
- **basket**: `basket`
- **order**: `orders`
- **payment**: `payment`
- **profile**: `profile`, `profile/password`, `profile/avatar`
- **tags**: `tags`

Сборка маршрутов в одном месте:

`apps/api_urls.py` → включает `urls.py` из каждого приложения.

---

## 5) Доменная модель (минимум под контракт)

### catalog
- Category
- Product
- ProductImage
- Specification
- Review

### tags
- Tag

### basket
- BasketItem (с поддержкой гостя через `session_key`)

### order
- Order
- OrderItem

### profile
- Profile
- Avatar

### payment
- Payment (можно как stub на первом этапе)

---

## 6) camelCase в API
Frontend ждёт camelCase (`fullName`, `freeDelivery`, `totalCost`, `createdAt`).

Рекомендуемый подход:
- модели: snake_case
- serializers: camelCase через `source=...`

---

## 7) Особенности передачи данных (важный нюанс)
Преподаватель показал, что иногда данные могут приходить нестандартно (JSON “ключом” в POST).

Поэтому делаем общий helper парсинга для API:
1) `request.data`
2) `json.loads(request.body)`
3) `json.loads(list(request.POST.keys())[0])`

---

## 8) План разработки (по совету преподавателя)
1) **authapp** полностью (sign-in/sign-up/sign-out)
2) **profile** полностью
3) **catalog + tags** (чтобы фронт начал жить на главной/каталоге)
4) **basket**
5) **order + payment**
6) финальное тестирование фронтом

---

## 9) Артефакт для работы: checklist
Используйте файл чек-листа реализации (Endpoint → App → View/Serializer/Model/Status):
- `implementation_checklist.md`
- `implementation_checklist.docx`
