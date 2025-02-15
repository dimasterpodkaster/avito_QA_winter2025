import pytest
import re


class TestGetItemStatisticsAPI:
    valid_id = "0cd4183f-a699-4486-83f8-b513dfde477a"
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    invalid_id = "abcd123"
    data = {
        "sellerID": 12345,
        "name": "Перстень",
        "price": 100,
        "statistics": {"likes": 10, "viewCount": 50, "contacts": 5}
    }

    def test_get_statistics_status_code(self, api_client):
        response = api_client.get_item_statistics(self.valid_id)
        assert response.status_code == 200, f"Ожидался код 200, но получен {response.status_code}"

        response = api_client.get_item_statistics(self.non_existent_id)
        assert response.status_code == 404, f"Ожидался код 404, но получен {response.status_code}"

    def test_get_statistics_fields(self, api_client):
        response = api_client.get_item_statistics(self.valid_id)
        data = response.json()
        assert isinstance(data, list)
        errors = []

        for item in data:
            if "likes" not in item:
                errors.append(KeyError(f"Поле 'likes' отсутствует в ответе"))
            if "viewCount" not in item:
                errors.append(KeyError(f"Поле 'viewCount' отсутствует в ответе"))
            if "contacts" not in item:
                errors.append(KeyError(f"Поле 'contacts' отсутствует в ответе"))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_get_statistics_data_types(self, api_client):
        response = api_client.get_item_statistics(self.valid_id)
        data = response.json()
        assert isinstance(data, list)
        errors = []

        for item in data:
            if not isinstance(item.get("likes"), int):
                errors.append(TypeError(f"Поле 'likes' должно быть int, а получено {type(item.get('likes'))}"))
            if not isinstance(item.get("viewCount"), int):
                errors.append(TypeError(f"Поле 'viewCount' должно быть int, а получено {type(item.get('viewCount'))}"))
            if not isinstance(item.get("contacts"), int):
                errors.append(TypeError(f"Поле 'contacts' должно быть int, а получено {type(item.get('contacts'))}"))

        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_post_item_with_statistics(self, api_client):
        response = api_client.post_item(self.data)
        assert response.status_code == 200
        status_text = response.json().get("status", "")
        match = re.search(r"([a-f0-9\-]{36})", status_text)
        assert match, f"Не удалось извлечь ID объявления, ответ: {response.json()}"
        item_id = match.group(1)

        response = api_client.get_item_statistics(item_id)
        assert response.status_code == 200
        stats_list = response.json()
        assert isinstance(stats_list, list) and len(stats_list) > 0, "Список статистик пуст"
        stats = stats_list[0]

        errors = []
        if stats["likes"] != 10:
            errors.append(AssertionError(f"Ожидалось 10 'likes', а получено {stats['likes']}"))
        if stats["viewCount"] != 50:
            errors.append(AssertionError(f"Ожидалось 50 'viewCount', а получено {stats['viewCount']}"))
        if stats["contacts"] != 5:
            errors.append(AssertionError(f"Ожидалось 5 'contacts', а получено {stats['contacts']}"))
        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки: " + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_post_item_with_partial_statistics(self, api_client):
        data = self.data
        del data["statistics"]["contacts"]
        response = api_client.post_item(data)
        assert response.status_code == 200
        status_text = response.json().get("status", "")
        match = re.search(r"([a-f0-9\-]{36})", status_text)
        assert match, f"Не удалось извлечь ID объявления, ответ: {response.json()}"
        item_id = match.group(1)

        response = api_client.get_item_statistics(item_id)
        assert response.status_code == 200
        stats_list = response.json()
        assert isinstance(stats_list, list) and len(stats_list) > 0, "Список статистик пуст"
        stats = stats_list[0]

        assert stats["contacts"] == 0, f"Ожидалось 0 'contacts', а получено {stats['contacts']}"

    def test_post_item_without_statistics(self, api_client):
        data = self.data
        del data["statistics"]
        response = api_client.post_item(data)
        assert response.status_code == 200
        status_text = response.json().get("status", "")
        match = re.search(r"([a-f0-9\-]{36})", status_text)
        assert match, f"Не удалось извлечь ID объявления, ответ: {response.json()}"
        item_id = match.group(1)

        response = api_client.get_item_statistics(item_id)
        assert response.status_code == 200
        stats_list = response.json()
        assert isinstance(stats_list, list) and len(stats_list) > 0, "Список статистик пуст"
        stats = stats_list[0]

        errors = []
        if stats["likes"] != 0:
            errors.append(AssertionError(f"Ожидалось 0, а получено {stats['likes']}"))
        if stats["viewCount"] != 0:
            errors.append(AssertionError(f"Ожидалось 0, а получено {stats['viewCount']}"))
        if stats["contacts"] != 0:
            errors.append(AssertionError(f"Ожидалось 0, а получено {stats['contacts']}"))
        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                error_message = "Обнаружены ошибки:" + " ".join(map(str, errors))
                pytest.fail(error_message, pytrace=False)

    def test_get_statistics_with_invalid_id(self, api_client):
        response = api_client.get_item_statistics(self.invalid_id)
        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"
