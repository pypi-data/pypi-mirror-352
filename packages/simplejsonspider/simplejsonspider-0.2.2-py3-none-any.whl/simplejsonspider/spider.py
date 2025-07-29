# simplejsonspider/spider.py

import os
import requests
import json
from typing import Dict, Any, Optional

class SimpleJSONSpider:
    def __init__(
        self,
        api_url: str,
        filename_template: str,
        storage_dir: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ):
        self.api_url = api_url
        self.filename_template = filename_template
        self.storage_dir = storage_dir
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.bilibili.com/",
        }
        self.cookies = cookies or {}
        os.makedirs(self.storage_dir, exist_ok=True)

    def fetch_json(self) -> Dict[str, Any]:
        resp = requests.get(self.api_url, headers=self.headers, cookies=self.cookies)
        resp.raise_for_status()
        return resp.json()

    def get_filename(self, json_obj: Dict[str, Any]) -> str:
        try:
            return self.filename_template.format(**json_obj)
        except KeyError as e:
            raise ValueError(f"Key '{e.args[0]}' not found in API response for filename template.")

    def save_json(self, json_obj: Dict[str, Any]):
        filename = self.get_filename(json_obj)
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)

    def run(self):
        json_obj = self.fetch_json()
        self.save_json(json_obj)
