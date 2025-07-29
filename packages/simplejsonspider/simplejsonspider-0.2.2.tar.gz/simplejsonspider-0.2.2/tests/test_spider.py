# tests/test_spider.py

import os
import shutil
from simplejsonspider import SimpleJSONSpider

def test_run_and_save_json(tmp_path):
    # 使用jsonplaceholder测试，始终可用
    api_url = "https://jsonplaceholder.typicode.com/todos/1"
    filename_template = "{id}_{title}.json"
    storage_dir = tmp_path / "data"
    storage_dir_str = str(storage_dir)
    
    spider = SimpleJSONSpider(
        api_url=api_url,
        filename_template=filename_template,
        storage_dir=storage_dir_str
    )
    spider.run()
    
    # 取回实际保存的文件名（和API返回字段有关）
    expected_filename = "1_delectus aut autem.json"
    file_path = os.path.join(storage_dir_str, expected_filename)
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert '"id": 1' in content

def test_headers_and_cookies(monkeypatch, tmp_path):
    # 模拟请求，确保headers/cookies能被传递
    api_url = "http://example.com/test"
    filename_template = "dummy.json"
    storage_dir = str(tmp_path)
    headers = {"User-Agent": "pytest-agent"}
    cookies = {"testcookie": "123"}

    class DummyResp:
        def raise_for_status(self): pass
        def json(self): return {"id": 1, "title": "dummy"}
    
    def dummy_get(url, headers=None, cookies=None):
        assert headers["User-Agent"] == "pytest-agent"
        assert cookies["testcookie"] == "123"
        return DummyResp()
    
    monkeypatch.setattr("requests.get", dummy_get)

    spider = SimpleJSONSpider(
        api_url=api_url,
        filename_template="{id}_{title}.json",
        storage_dir=storage_dir,
        headers=headers,
        cookies=cookies,
    )
    spider.run()
    # 检查文件是否生成
    file_path = os.path.join(storage_dir, "1_dummy.json")
    assert os.path.exists(file_path)

