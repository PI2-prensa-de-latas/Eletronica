import requests
import json

url = "http://159.65.236.163:8080/user"
body = {"name":"PI2","email":"pi2@fimDoMundo.com","password":"sochora",}

url = "http://159.65.236.163:8080/canCategory"
body = {"trademark":"Coca cola","size":"10",}

url = "http://159.65.236.163:8080/SmashedCan"
body = {"user":1,"machine":"1","category":1}

post_user = requests.post(url,data=json.dumps(body))
