import json
import requests

class Metrics:
    
    def __init__(self):

        self.api_token = None
        self.api_customer = None

        self.api_url_metrics = 'https://{0}.xendesktop.net/Citrix/Monitor/OData/v4/Data/'.format(self.api_customer)

        self.headers = {'Customer': self.api_customer}

        self.generateToken()

    def generateToken(self):

        api_url_token = 'https://trust.citrixworkspacesapi.net/root/tokens/clients'
        api_client_id = None
        api_client_secret = None

        body = {'clientId': api_client_id,
                'clientSecret': api_client_secret}

        headers = {'Content-Type': 'application/json'}

        response = requests.post(api_url_token, data=json.dumps(body), headers=headers)
        response_dic = dict(response.json())

        self.api_token = response_dic.get('token')
        self.headers['Authorization'] = 'CWSAuth bearer={0}'.format(self.api_token)

        # print(response.text)
        # print(response_dic.get('token'))
    
    def getCatalogs(self):

        api_url_catalogs = '{0}Catalogs'.format(self.api_url_metrics)

        params = {'$top': '1'}

        response = requests.get(api_url_catalogs, headers=self.headers, params=params)

        print(response.text)
    
    def getConnections(self):

        api_url_connections = '{0}Connections'.format(self.api_url_metrics)

        params = {'$top': '1'}

        response = requests.get(api_url_connections, headers=self.headers, params=params)

        print(response.text)

if __name__ == '__main__':
    metrics = Metrics()
    metrics.getCatalogs()