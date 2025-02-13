import requests


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_item(self, item_id):
        url = f"{self.base_url}/api/1/item/{item_id}"
        response = requests.get(url, headers={"Accept": "application/json"})
        return response

    def get_seller_items(self, seller_id):
        url = f"{self.base_url}/api/1/{seller_id}/item"
        response = requests.get(url, headers={"Accept": "application/json"})
        return response

    def post_item(self, data):
        url = f"{self.base_url}/api/1/item"
        response = requests.post(url, json=data)
        return response

    def post_item_on_payload(self, seller_id, name, price):
        url = f"{self.base_url}/api/1/item"
        payload = {
            "sellerID": seller_id,
            "name": name,
            "price": price
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json", "Accept": "application/json"})
        return response

    def get_item_statistics(self, item_id):
        url = f"{self.base_url}/api/1/statistic/{item_id}"
        response = requests.get(url, headers={"Accept": "application/json"})
        return response
