import json
import requests
import sys
from datetime import datetime
from datetime import timedelta
from configparser import ConfigParser

class Citrix:
    
    def __init__(self, company, customer, client_id, client_secret, token, token_created):

        self.__company = company
        self.__token = token
        self.__token_created = datetime.strptime(token_created, '%Y-%m-%d %H:%M:%S.%f')
        self.__date_now = datetime.now()
        self.__customer = customer
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__url_metrics = 'https://{0}.xendesktop.net/Citrix/Monitor/OData/v4/Data/'.format(self.__customer)
        self.__url_token = 'https://trust.citrixworkspacesapi.net/root/tokens/clients'
        self.__headers = {'Authorization': 'CWSAuth bearer={0}'.format(self.__token),
                          'Customer': self.__customer}

    def generateToken(self):

        # verifica a diferença entre a última criação do token e a data de execução do script
        date_difference = self.__date_now - self.__token_created
        token_expired = True if date_difference > timedelta(hours=1) else False

        if (token_expired):

            config = ConfigParser()
            config.read('config.cfg')
            body = {'clientId': self.__client_id,
                    'clientSecret': self.__client_secret}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.__url_token, data=json.dumps(body), headers=headers)
            response_dic = dict(response.json())
            self.__token = response_dic.get('token')
            self.__headers['Authorization'] = 'CWSAuth bearer={0}'.format(self.__token)
            
            # atualiza o arquivo de configuração com o novo token
            config.set(self.__company, 'token', self.__token)
            config.set(self.__company, 'token_created', str(self.__date_now))
            with open('./config.cfg', 'w') as f:
                config.write(f)

    def getMetric(self, metric_name):
        
        url_final = '{0}{1}'.format(self.__url_metrics, metric_name)
        params = {'$top': 2}
        response = requests.get(url_final, headers=self.__headers, params=params)
        print(response.text)

if __name__ == '__main__':

    # SOLOR
    company = sys.argv[1]
    # Sessions
    metric = sys.argv[2]

    # objeto ConfigParser
    config = ConfigParser()
    config.read('config.cfg')

    # obtem as métricas através do arquivo de configuração
    customer = config.get(company, 'customer')
    client_id = config.get(company, 'client_id')
    client_secret = config.get(company, 'client_secret')
    token = config.get(company, 'token')
    token_created = config.get(company, 'token_created')

    # cria um objeto do tipo Citrix
    citrix = Citrix(company, customer, client_id, client_secret, token, token_created)
    citrix.generateToken()
    citrix.getMetric(metric)