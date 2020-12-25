import requests


def notify_BE(restricted_endpoint: str, backend_endpoint: str, data = {}):
    return
    requests.post(url=f"{backend_endpoint}/{restricted_endpoint}", data=data)