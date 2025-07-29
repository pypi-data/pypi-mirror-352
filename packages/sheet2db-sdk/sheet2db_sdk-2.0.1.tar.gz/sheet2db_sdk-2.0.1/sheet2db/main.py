import requests
from typing import List, Dict, Optional, Union, Literal

SortDirection = Literal["asc", "desc"]
Format = Literal["rows", "columns", "matrix"]
UpdateType = Literal["row", "filter"]
DeleteType = Literal["row", "filter"]


class Sheet2DBClient:
    def __init__(self, api_id: str, version: str = "v1"):
        self.api_id = api_id
        self.base_url = f"https://api.sheet2db.io/{version}/data/{api_id}"
        self.headers = {
            "Content-Type": "application/json"
        }

    def use_basic_authentication(self, username: str, password: str):
        self.headers["Authorization"] = f"Basic {requests.auth._basic_auth_str(username, password)}"

    def use_jwt_authentication(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"

    def use_bearer_token_authentication(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"

    def _post(self, path: str, data: dict) -> dict:
        url = f"{self.base_url}/{path}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    def _patch(self, path: str, data: dict) -> dict:
        url = f"{self.base_url}/{path}"
        response = requests.patch(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    def _get(self,path: str, params: dict)-> dict:
        url = f"{self.base_url}/{path}"
        response = requests.get(url,params=params)
        response.raise_for_status()
        return response.json()
    def _delete(self,path: str, params: dict)-> dict:
        url = f"{self.base_url}/{path}"
        response = requests.delete(url,params=params)
        response.raise_for_status()
        return response.json()

    def read(
        self,
        options: Dict,
        sheet: Optional[str] = None
    ) -> List[Dict]:
        path = f"{sheet}" if sheet else ""
        return self._get(path, options)

    def insert(
        self,
        data: List[Dict],
        sheet: Optional[str] = None
    ) -> Dict:
        path = f"{sheet}" if sheet else ""
        return self._post(path, {"data": data})

    def update(
        self,
        options: Dict,
        sheet: Optional[str] = None
    ) -> Dict:
        path = f"{sheet}" if sheet else ""
        return self._patch(path, options)

    def delete(
        self,
        options: Dict,
        sheet: Optional[str] = None
    ) -> Dict:
        path = f"{sheet}" if sheet else ""
        return self._delete(path, options)

    def add_sheet(
        self,
        name: str,
        first_row: Optional[List[str]] = None,
        copy_columns_from: Optional[str] = None
    ) -> Dict:
        data = {"name": name}
        if first_row:
            data["firstRow"] = first_row
        if copy_columns_from:
            data["copyColumnsFrom"] = copy_columns_from
        return self._post("sheet", data)

    def delete_sheet(self, sheet: str) -> Dict:
        path = f"sheet/{sheet}"
        return self._delete(path=path)
