import requests
import json
from pprint import pprint

def main():
    url = "http://localhost:8080/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Example method
    payloads = [{
        "method": "parse",
        "params": ["who is 's can be by NUM ?"],
        "jsonrpc": "2.0",
        "id": 0,
    },
    {
        "method": "parse",
        "params": ["what 's do lot for mavs ?"],
        "jsonrpc": "2.0",
        "id": 1,
    },
    {
        "method": "parse",
        "params": ["what is tonto creek 's 's for ?"],
        "jsonrpc": "2.0",
        "id": 2,
    },
    {
        "method": "parse",
        "params": ["what is vermont 's 's go to ?"],
        "jsonrpc": "2.0",
        "id": 3
    }]

    for payload in payloads:
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
        pprint(response)


if __name__ == "__main__":
    main()
