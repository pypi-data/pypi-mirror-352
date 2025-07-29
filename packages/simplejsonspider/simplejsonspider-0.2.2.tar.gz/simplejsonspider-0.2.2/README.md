# simplejsonspider

**simplejsonspider** 是一个超简单的 Python 工具包，用于请求指定的 JSON API 并将返回内容自动保存为本地 JSON 文件。你只需要指定接口地址、文件名模板和存储路径，即可“一键抓取、自动存储”。注意：该工具包仅支持 JSON 格式的 API 响应。用GPT 4.1 只花了15分钟写的。


---

## 特点

- ⚡️ 支持自定义 HTTP headers 和 cookies
- 🗂 文件名模板自由拼接，支持如 `{id}_{title}.json`
- 🧰 用法极简，适合数据抓取、接口快照、API调试等场景

---

## 安装

```bash
pip install simplejsonspider
````

---

## 快速上手

```python
from simplejsonspider import SimpleJSONSpider

id = 1
title = 'delectus aut autem'

# 创建一个简单的 JSON API 抓取器
spider = SimpleJSONSpider(
    api_url='https://jsonplaceholder.typicode.com/todos/1',          # API接口
    filename_template='{id}_{title}.json',                           # 文件名模板（对应API返回的字段）
    storage_dir='./data'                                             # 存储目录
)
spider.run()
```

执行后，将自动在 `./data` 目录下生成如 `1_delectus aut autem.json` 的文件，内容即API返回的JSON。

---

## 进阶用法：自定义headers与cookies

有些网站需要带自定义User-Agent、Referer或Cookie，直接传递即可：

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.bilibili.com/"
}
cookies = {
    "SESSDATA": "your_cookie"
}

spider = SimpleJSONSpider(
    api_url='https://jsonplaceholder.typicode.com/todos/1', # 示例API接口
    filename_template='{code}.json',     # 根据API返回的字段
    storage_dir='./bili_data',
    headers=headers,
    cookies=cookies
)
spider.run()
```

---

## 文件名模板说明

* 支持 Python 的字符串格式化：`{id}_{title}.json`
* **注意**：模板里的字段必须是API响应JSON顶层的键。

---

## 常见问题

* **遇到 412、403 等错误？**
  请添加正确的 User-Agent、Referer 或 Cookie（详见进阶用法）。

* **保存多个API数据？**
  可在循环中多次创建 SimpleJSONSpider 实例，或自己扩展批量功能。

---

## License

MIT License

---

## 关于作者

\[Zeturn]
\[[GitHub主页](https://github.com/zeturn)]

---

```

---