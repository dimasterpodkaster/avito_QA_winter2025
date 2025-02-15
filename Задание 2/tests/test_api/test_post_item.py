import re
import pytest
import warnings


class TestPostAPI:
    item_data = {
        "name": "Телевизор",
        "price": 36500,
        "sellerId": 999665,
        "statistics": {
            "contacts": 9,
            "likes": 25,
            "viewCount": 25
        }
    }

    def test_post_item_status_code(self, api_client):
        response = api_client.post_item(self.item_data)

        assert response.status_code in [200, 201], f"Ожидался код 200 или 201, но получен {response.status_code}"

    def test_post_item(self, api_client):
        post_response = api_client.post_item(self.item_data)
        data = post_response.json()

        match = re.search(r"([a-f0-9\-]{36})", data["status"])
        assert match, f"Не удалось извлечь ID объявления из {data['status']}"

    def test_verify_item(self, api_client):
        post_response = api_client.post_item(self.item_data)
        data = post_response.json()

        match = re.search(r"([a-f0-9\-]{36})", data["status"])
        item_id = match.group(1)

        get_response = api_client.get_item(item_id)
        assert get_response.status_code == 200, f"Ожидался код 200, но получен {get_response.status_code}"

        fetched_data = get_response.json()
        if isinstance(fetched_data, list):
            assert len(fetched_data) > 0, "Ответ содержит пустой список объявлений"
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

        statistics = fetched_data.get("statistics", {})

        for stat_field in ["contacts", "likes", "viewCount"]:
            try:
                assert statistics[stat_field] == self.item_data["statistics"][stat_field], \
                    f"Ожидалось {self.item_data['statistics'][stat_field]}, а получено {statistics[stat_field]}"
            except KeyError:
                warnings.warn(f"Поле '{stat_field}' отсутствует в разделе statistics, тест продолжается", UserWarning)
            except AssertionError as e:
                errors.append(AssertionError(str(e)))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_post_item_empty_body(self, api_client):
        response = api_client.post_item({})
        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"

    @pytest.mark.parametrize("missing_field", ["name", "price", "statistics"])
    def test_post_item_missing_field(self, api_client, missing_field):
        item_data = {
            "name": "Смартфон",
            "price": 60000,
            "sellerId": 98765,
            "statistics": {
                "contacts": 9,
                "like": 25,
                "viewCount": 25
            }
        }

        del item_data[missing_field]

        response = api_client.post_item(item_data)

        assert response.status_code in [200, 201], f"Ожидался код 200 или 201, но получен {response.status_code}"

    @pytest.mark.parametrize("missing_field", ["sellerId"])
    def test_post_item_missing_seller_id(self, api_client, missing_field):
        item_data = {
            "name": "Смартфон",
            "price": 60000,
            "sellerId": 98765,
            "statistics": {
                "contacts": 9,
                "like": 25,
                "viewCount": 25
            }
        }

        del item_data[missing_field]

        response = api_client.post_item(item_data)

        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"

    @pytest.mark.parametrize("field, value", [
        ("price", "дешево"),  # price должен быть числом
        ("sellerId", "abcd123"),  # sellerId должен быть числом
        ("statistics", "не json")  # statistics должен быть объектом
    ])
    def test_post_item_invalid_data(self, api_client, field, value):
        item_data = {
            "name": "Смартфон",
            "price": 60000,
            "sellerId": 98765,
            "statistics": {
                "contacts": 9,
                "like": 25,
                "viewCount": 25
            }
            , field: value}

        response = api_client.post_item(item_data)

        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"
