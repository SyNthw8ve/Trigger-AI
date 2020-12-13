import requests


def notify_BE(restricted_endpoint: str, backend_endpoint: str, data = {}):
    requests.post(url=f"{backend_endpoint}/{restricted_endpoint}", data=data)