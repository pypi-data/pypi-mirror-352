from requests import post
from requests import get

def getip():
    return get("https://api.ipify.org/?format=text").text

def send_webhook_message(url, message, username=None):
    payload = {"content": message}
    if username:
        payload["username"] = username
    return post(url, json=payload).status_code
