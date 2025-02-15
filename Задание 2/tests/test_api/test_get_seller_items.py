import pytest
import re


class TestSellerItemsAPI:
    valid_seller_id = 999665  # ID реального продавца
    invalid_seller_id = "abcd123"  # Невалидный sellerId (должен быть числом)
    non_existent_seller_id = 123456789  # ID, у которого точно нет объявлений

    def test_get_seller_items_success(self, api_client):
        response = api_client.get_seller_items(self.valid_seller_id)
        assert response.status_code == 200, f"Ожидался код 200, но получен {response.status_code}"

        data = response.json()
        assert isinstance(data, list), "API должно вернуть список товаров"

    def test_get_seller_items_structure(self, api_client):
        response = api_client.get_seller_items(self.valid_seller_id)
        data = response.json()

        errors = []
        for item in data:
            if not isinstance(item, dict):
                errors.append(TypeError(f"Элемент должен быть словарём, получен {type(item)}"))
                continue
            for field in ["name", "price", "sellerId"]:
                if field not in item:
                    errors.append(KeyError(f"Поле '{field}' отсутствует в товаре: {item}"))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_get_seller_items_empty(self, api_client):
        response = api_client.get_seller_items(self.non_existent_seller_id)

        errors = []
        if response.status_code != 200:
            errors.append(AssertionError(f"Ожидался код 200, но получен {response.status_code}"))

        data = response.json()
        if data != []:
            errors.append(AssertionError(f"Ожидался пустой список [], но получен: {data}"))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_get_seller_items_invalid_seller_id(self, api_client):
        response = api_client.get_seller_items(self.invalid_seller_id)
        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"

    def test_get_seller_items_belongs_to_seller(self, api_client):
        response = api_client.get_seller_items(self.valid_seller_id)
        data = response.json()

        errors = []
        for item in data:
            if item["sellerId"] != self.valid_seller_id:
                errors.append(AssertionError(f"Найден товар с чужим sellerId: {item['sellerId']}"))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_post_and_get_seller_items_match(self, api_client):
        item_data = {
            "name": "Игровая консоль",
            "price": 45000,
            "sellerId": self.valid_seller_id,  # Теперь передаём все данные в `data`
            "statistics": {
                "contacts": 9,
                "likes": 25,
                "viewCount": 25
            }
        }
        post_response = api_client.post_item(item_data)
        data = post_response.json()

        match = re.search(r"([a-f0-9\-]{36})", data["status"])
        assert match, f"Не удалось извлечь ID объявления из {data['status']}"
        item_id = match.group(1)

        get_response = api_client.get_seller_items(self.valid_seller_id)
        seller_items = get_response.json()

        matching_items = [item for item in seller_items if item.get("id") == item_id]
        assert matching_items, f"Объявление с ID {item_id} не найдено в списке товаров продавца"

        fetched_item = matching_items[0]

        errors = []
        for field in ["name", "price", "sellerId"]:
            expected_value = item_data[field]
            actual_value = fetched_item.get(field)

            if actual_value != expected_value:
                errors.append(
                    AssertionError(f"Поле '{field}' не совпадает. Ожидалось {expected_value}, получено {actual_value}"))

        expected_statistics = item_data["statistics"]
        actual_statistics = fetched_item.get("statistics", {})
        for stat_field in ["contacts", "likes", "viewCount"]:
            expected_value = expected_statistics[stat_field]
            actual_value = actual_statistics.get(stat_field)

            if actual_value != expected_value:
                errors.append(
                    f"Поле 'statistics.{stat_field}' не совпадает. Ожидалось {expected_value}, получено {actual_value}")

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)
