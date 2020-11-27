import requests 

class Api:

    API_KEY = ''

    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        
    def get(self, url, params):
        headers = {"Authorization": "Bearer " + self.API_KEY}

        return requests.get(url=url, params=params, headers=headers)

    def orders(self):
        url = 'https://api.getjusto.com/api/v1/orders'

        params = {
        "fromDate": "2020-10-12T03:00:00.000Z",
        "toDate": "2020-10-19T03:00:00.000Z",
        "includeNotPaid": "false",
        "useDeliverAt": "false"
        }

        request = self.get(url, params)

        print(request.status_code)
        print(request.text)
        print(request.json())