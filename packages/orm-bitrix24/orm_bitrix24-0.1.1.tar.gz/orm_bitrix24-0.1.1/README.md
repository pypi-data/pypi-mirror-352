![PyPI - Downloads](https://img.shields.io/pypi/dm/orm-bitrix24)


# ORM-система для работы с Bitrix24


Работа библиотеки находится в стадии разработки. (рекомендуется только для локальной разработки)

Библиотека для удобной работы с API Bitrix24 в объектно-ориентированном стиле.

## Особенности

- ORM-подобный доступ к данным через точечную нотацию
- Удобные методы для создания, обновления и поиска сущностей
- Поддержка связанных объектов и отношений между ними
- Поддержка пользовательских полей
- Работа с товарными позициями сделок
- Асинхронный подход для лучшей производительности

## Установка

```bash
uv add orm-bitrix24
```

## Использование

### Инициализация

```python
from fast_bitrix24 import Bitrix
from entity import Deal

# Инициализация Bitrix клиента
bitrix = Bitrix('https://your-domain.bitrix24.ru/rest/1/your_webhook_token/')

# Инициализация менеджера сущностей
Deal.get_manager(bitrix)
```

### Получение сделок

```python
# Получение всех сделок
deals = await Deal.objects.get_all()

# Фильтрация сделок
deals = await Deal.objects.filter(type_id="SALE", stage_id="NEW")

# Получение сделки по ID
deal = await Deal.get_by_id(bitrix, "123")
```

### Работа со сделкой

```python
# Чтение полей
print(deal.title)
print(deal.opportunity)
print(deal.created_at)  # Автоматически преобразуется в datetime объект

# Чтение связанных объектов (необходимо использовать await)
company = await deal.company
if company:
    print(company.name)

# Изменение значений
deal.title = "Новое название"
deal.opportunity = 15000
deal.tags.append("новый_тег")
await deal.save()

# Создание примечаний
note = await deal.notes.create(text="Примечание к сделке")
```

### Создание новой сделки

```python
# Создание через менеджер объектов
deal = await Deal.objects.create(
    title="Новая сделка",
    opportunity=10000,
    currency_id="RUB",
    stage_id="NEW"
)

# Альтернативный способ создания
deal = Deal(bitrix)
deal.title = "Новая сделка"
deal.opportunity = 10000
deal.currency_id = "RUB"
deal.stage_id = "NEW"
await deal.save()
```

### Работа с товарами сделки

```python
# Получение товаров сделки
products = await deal.products.get_all()
print(f"В сделке {len(products)} товаров")

# Добавление товара
product = deal.products.add(
    product_id=123,  # ID товара из каталога Bitrix24
    price=1000,
    quantity=2,
    discount_rate=10  # 10% скидка
)

# Изменение параметров товара
product.quantity = 3
product.discount_sum = 500  # Скидка фиксированной суммой

# Сохранение товаров сделки
await deal.save()
```

### Пользовательские поля

```python
from entity import Deal, CustomField, TextCustomField, SelectCustomField

# Добавление пользовательских полей напрямую в класс Deal
Deal.add_custom_field('utm_source', CustomField("UTM_SOURCE"))
Deal.add_custom_field('delivery_address', TextCustomField("UF_CRM_DELIVERY_ADDRESS"))
Deal.add_custom_field('delivery_type', SelectCustomField("UF_CRM_DELIVERY_TYPE"))

# Инициализация менеджера
Deal.get_manager(bitrix)

# Использование пользовательских полей
deals = await Deal.objects.get_all()
deal = deals[0]
deal.delivery_address = "ул. Примерная, д. 1, кв. 2"
await deal.save()
```

### Работа со связанными объектами

Важно! Связанные объекты (company, contact и др.) возвращают корутины, которые нужно ожидать с помощью `await`:

```python
# Получение связанной компании
company = await deal.company
if company:
    print(f"Компания: {company.title}")

# Получение связанного контакта
contact = await deal.contact
if contact:
    print(f"Контакт: {contact.full_name}")

# Изменение связанного объекта произойдет только после сохранения сделки
deal.company_id = 5  # Смена компании
await deal.save()
```

## Требования

- Python 3.7+
- fast-bitrix24

## Лицензия

MIT
