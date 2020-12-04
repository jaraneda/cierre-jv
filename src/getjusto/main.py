import requests 

class Api:

    API_KEY = ''

    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        
    def get(self, url, data):
        headers = {"Authorization": "Bearer " + self.API_KEY}

        return requests.get(url=url, data=data, headers=headers)

    def orders(self, fromDate, toDate):
        url = 'https://api.getjusto.com/api/v1/orders'

        print(fromDate)
        print(toDate)
        params = {
        "fromDate": fromDate,
        "toDate": toDate,
        "includeNotPaid": "false",
        "useDeliverAt": "false"
        }

        return self.get(url, params)
