import requests

class RScriptsAPI:
    BASE_URL = "https://rscripts.net/api/v2"

    def __init__(self, username=None):
        self.headers = {}
        if username:
            self.headers["Username"] = username

    def get_scripts(self, page=1, order_by="date", sort="desc", query=None, **filters):
        params = {
            "page": page,
            "orderBy": order_by,
            "sort": sort
        }
        if query:
            params["q"] = query
        params.update({k: str(v).lower() for k, v in filters.items()})
        response = requests.get(f"{self.BASE_URL}/scripts", params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_script_by_id(self, script_id):
        if not script_id:
            raise ValueError("Script ID is required")
        response = requests.get(f"{self.BASE_URL}/script", params={"id": script_id}, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_trending_scripts(self):
        response = requests.get(f"{self.BASE_URL}/trending", headers=self.headers)
        response.raise_for_status()
        return response.json()
