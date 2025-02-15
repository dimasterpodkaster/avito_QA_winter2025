import re
import pytest
import warnings


class TestPostPayloadAPI:
    item_data = {
        "name": "Телевизор",
        "price": 36500,
        "sellerId": 999665
    }

    def test_post_item_status_code(self, api_client):
        response = api_client.post_item_on_payload(self.item_data["sellerId"], self.item_data["name"], self.item_data["price"])
        assert response.status_code in [200, 201], f"Ожидался код 200 или 201, но получен {response.status_code}"

    def test_post_item(self, api_client):
        """Проверяем, что API возвращает ID объявления"""
        post_response = api_client.post_item_on_payload(self.item_data["sellerId"], self.item_data["name"], self.item_data["price"])
        data = post_response.json()

        match = re.search(r"([a-f0-9\-]{36})", data["status"])
        assert match, f"Не удалось извлечь ID объявления из {data['status']}"

    def test_verify_item(self, api_client):
        """Проверяем, что объявление создаётся и доступно для GET-запроса"""
        post_response = api_client.post_item_on_payload(self.item_data["sellerId"], self.item_data["name"], self.item_data["price"])
        data = post_response.json()

        match = re.search(r"([a-f0-9\-]{36})", data["status"])
        item_id = match.group(1)

        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 200, f"Ожидался код 200, но получен {get_response.status_code}"

        fetched_data = get_response.json()
        if isinstance(fetched_data, list):
            if not fetched_data:
                pytest.fail(f"Ошибка: API вернул пустой список для ID {item_id}")
            fetched_data = fetched_data[0]

        errors = []

        for field in ["name", "price", "sellerId"]:
            try:
                assert fetched_data[field] == self.item_data[field], \
                    f"Ожидалось {self.item_data[field]}, а получено {fetched_data[field]}"
            except KeyError:
                warnings.warn(f"Поле '{field}' отсутствует в ответе, тест продолжается", UserWarning)
            except AssertionError as e:
                errors.append(AssertionError(str(e)))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_post_item_empty_body(self, api_client):
        """Проверяем, что пустой запрос вызывает 400 Bad Request"""
        response = api_client.post_item_on_payload(999665, "", None)
        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"

    @pytest.mark.parametrize("missing_field", ["name", "price"])
    def test_post_item_missing_field(self, api_client, missing_field):
        """Проверяем, что можно создать объявление без 'name' или 'price'"""
        item_data = {
            "name": "Смартфон",
            "price": 60000
        }

        del item_data[missing_field]

        response = api_client.post_item_on_payload(999665, item_data.get("name", ""), item_data.get("price"))
        assert response.status_code in [200, 201], f"Ожидался код 200 или 201, но получен {response.status_code}"

    def test_post_item_missing_seller_id(self, api_client):
        """Проверяем, что без sellerId запрос вызывает 400"""
        response = api_client.post_item_on_payload(None, "Смартфон", 60000)
        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"

    @pytest.mark.parametrize("field, value", [
        ("price", "дешево"),
        ("sellerId", "abcd123"),
    ])
    def test_post_item_invalid_data(self, api_client, field, value):
        """Проверяем, что невалидные данные вызывают 400"""
        item_data = {"name": "Смартфон", "price": 60000, "sellerId": 999665, field: value}

        response = api_client.post_item_on_payload(item_data["sellerId"], item_data["name"], item_data["price"])
        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"
