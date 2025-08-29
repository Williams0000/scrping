import requests


API_KEY = "" # clé API

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# On demande à Bright Data de scraper la page souhaitée
data = {
    "zone": "web_unlocker1",
    "url": "", # URL site
    "format": "raw" 
}

response = requests.post(
    "https://api.brightdata.com/request",
    json=data,
    headers=headers
)

with open("output.html", "w", encoding="utf-8") as f:
    f.write(response.text)