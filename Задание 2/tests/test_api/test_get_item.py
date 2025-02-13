import pytest
import warnings


class TestAdvertisementAPI:
    @pytest.fixture
    def sample_item_id(self):
        return "b55a1222-e2ce-490d-9bec-06210269671e"

    def test_get_item_response(self, api_client, sample_item_id):
        response = api_client.get_item(sample_item_id)

        assert response.status_code == 200, f"Ожидался код 200, но получен {response.status_code}"
        assert response.content, "Пустой ответ от сервера"

    import pytest

    def test_get_item_structure(self, api_client, sample_item_id):
        response = api_client.get_item(sample_item_id)
        assert response.status_code == 200, f"Ожидался код 200, но получен {response.status_code}"

        data = response.json()
        items = data if isinstance(data, list) else [data]

        errors = []

        for item in items:
            if not isinstance(item, dict):
                errors.append(TypeError("Элемент списка должен быть словарем"))
                continue

            for field in ["name", "price", "sellerId", "statistics"]:
                if field not in item:
                    errors.append(KeyError(f"Ответ не содержит ключ '{field}'"))

            statistics = item.get("statistics", {})
            if not isinstance(statistics, dict):
                errors.append(TypeError(f"Поле 'statistics' должно быть словарем, получено {type(statistics)}"))

            for stat_field in ["contacts", "like", "viewCount"]:
                if stat_field not in statistics:
                    errors.append(KeyError(f"Ответ не содержит ключ '{stat_field}'"))

        if errors:
            raise errors[0] if len(errors) == 1 else pytest.fail("\n".join(map(str, errors)))

    def test_get_item_data_types(self, api_client, sample_item_id):
        response = api_client.get_item(sample_item_id)
        data = response.json()

        items = data if isinstance(data, list) else [data]

        errors = []

        for item in items:
            for field, expected_type in [("name", str), ("price", (int, float)), ("sellerId", int)]:
                try:
                    assert isinstance(item[field], expected_type), \
                        f"Поле '{field}' должно быть {expected_type}, а получено {type(item[field])}"
                except KeyError:
                    warnings.warn(f"Поле '{field}' отсутствует в ответе, тест продолжается", UserWarning)
                except AssertionError as e:
                    errors.append(AssertionError(str(e)))
                except TypeError:
                    errors.append(TypeError(f"Поле '{field}' содержит некорректный тип данных"))

            statistics = item.get("statistics", {})
            if not isinstance(statistics, dict):
                errors.append(TypeError(f"Поле 'statistics' должно быть словарем, получено {type(statistics)}"))
                continue

            for stat_field in ["contacts", "like", "viewCount"]:
                try:
                    assert isinstance(statistics[stat_field], int), \
                        f"Поле '{stat_field}' должно быть числом, а получено {type(statistics[stat_field])}"
                except KeyError:
                    warnings.warn(f"Поле '{stat_field}' отсутствует в statistics, тест продолжается", UserWarning)
                except AssertionError as e:
                    errors.append(AssertionError(str(e)))
                except TypeError:
                    errors.append(TypeError(f"Поле '{stat_field}' содержит некорректный тип данных"))

        if errors:
            raise errors[0] if len(errors) == 1 else pytest.fail("\n".join(map(str, errors)))

    def test_get_non_existent_item(self, api_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = api_client.get_item(fake_id)

        assert response.status_code == 404, f"Ожидался код 404, но получен {response.status_code}"

    def test_get_item_invalid_id(self, api_client):
        invalid_id = "123abc"
        response = api_client.get_item(invalid_id)

        assert response.status_code == 400, f"Ожидался код 400, но получен {response.status_code}"

    def test_get_item_no_extra_fields(self, api_client, sample_item_id):
        """Проверяем, что API не возвращает лишние поля"""
        response = api_client.get_item(sample_item_id)
        data = response.json()
        items = data if isinstance(data, list) else [data]

        errors = []

        for item in items:
            if not isinstance(item, dict):
                errors.append(TypeError(f"Ожидался словарь, но получен {type(item)}"))
                continue

            unexpected_fields = set(item.keys()) - {"createdAt", "id", "name", "price", "sellerId", "statistics"}
            if unexpected_fields:
                errors.append(KeyError(f"Найдены лишние поля: {unexpected_fields}"))

        if errors:
            raise errors[0] if len(errors) == 1 else pytest.fail("\n".join(map(str, errors)))



