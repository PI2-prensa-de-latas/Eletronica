import requests
import json
import time

url = "http://159.65.236.163:8080/canCategory"
body = {"trademark":"Coca cola","size":"10",}


post_user = requests.post(url,data=json.dumps(body))