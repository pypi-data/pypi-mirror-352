import requests
def cookies():
    sawad = requests.get('http://46.202.135.52:8801/golden-cookies/ytc')
    return sawad.json().get("cookie", "")