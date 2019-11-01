import requests
import json

url = "http://159.65.236.163:8080/user"
body = {"name":"PI2","email":"pi2@fimDoMundo.com","password":"sochora",}

post_user = requests.post(url,data=json.dumps(body))
