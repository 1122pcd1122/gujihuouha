import requests

url = "http://localhost:5001/predict"
payload = {
    "text": "令绍使洛阳方略武吏，检司诸宦者。"
}

try:
    response = requests.post(url, json=payload)
    print(response.json())
except Exception as e:
    print(f"请求失败: {e}")