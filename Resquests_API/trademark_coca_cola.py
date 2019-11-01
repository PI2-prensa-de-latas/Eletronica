import requests
import json
import time


url = "http://159.65.236.163:8080/SmashedCan"
body = {"user":1,"machine":"1","category":1}

post_user = requests.post(url,data=json.dumps(body))