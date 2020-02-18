import requests
import json

endpoint = "http://127.0.0.1:8000/api/question/ask/"

headers = {
    "Content-Type": "application/json",
    "Authorization": "JWT yJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFtaXIiLCJleHAiOjE1ODE2NjM2MDcsImVtYWlsIjoiIiwib3JpZ19pYXQiOjE1ODEwNTg4MDd9.pgEHWdbmsC-mgHUz14jZn8yL8Np4m_ldsw9UIiD0uKs"
}

data = {
    "title": "question3 about python",
    "body": "asking3",
    "tags": "python3 django redis"
}

r = requests.post(endpoint, data=json.dumps(data), headers=headers)
print(r.json())

