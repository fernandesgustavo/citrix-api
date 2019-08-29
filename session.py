import json
import requests
import sys
from datetime import datetime
from datetime import timedelta
from configparser import ConfigParser

class Session:
    
    def __init__(self, company, file, customer, client_id, client_secret, token, token_created):

        self.__company = company
        self.__file = file
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
            config.read(self.__file)
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
            with open(self.__file, 'w') as f:
                config.write(f)
    
    def sessions_disconnected(self):

        url_final = '{}{}'.format(self.__url_metrics, 'Sessions')
        params = {'$apply': 'groupby((ConnectionState),aggregate(SessionKey with countdistinct as NumberOfSessions))',
                    '$filter': 'ConnectionState eq 2'}
        response = requests.get(url_final, headers=self.__headers, params=params)
        return (response.json()['value'][0]['NumberOfSessions'])

    def sessions_terminated(self):

        url_final = '{}{}'.format(self.__url_metrics, 'Sessions')
        params = {'$apply': 'groupby((ConnectionState),aggregate(SessionKey with countdistinct as NumberOfSessions))',
                    '$filter': 'ConnectionState eq 3'}
        response = requests.get(url_final, headers=self.__headers, params=params)
        return (response.json()['value'][0]['NumberOfSessions'])

    def sessions_active(self):

        url_final = '{}{}'.format(self.__url_metrics, 'Sessions')
        params = {'$apply': 'groupby((ConnectionState),aggregate(SessionKey with countdistinct as NumberOfSessions))',
                  '$filter': 'ConnectionState eq 5'}
        response = requests.get(url_final, headers=self.__headers, params=params)
        return (response.json()['value'][0]['NumberOfSessions'])

if __name__ == '__main__':

    # objeto ConfigParser
    file = './config.cfg'
    config = ConfigParser()
    config.read(file)

    # SOLOR
    company = sys.argv[1]
    # active
    metric = sys.argv[2]

    # obtem as métricas através do arquivo de configuração
    customer = config.get(company, 'customer')
    client_id = config.get(company, 'client_id')
    client_secret = config.get(company, 'client_secret')
    token = config.get(company, 'token')
    token_created = config.get(company, 'token_created')

    # cria um objeto do tipo Session
    session = Session(company, file, customer, client_id, client_secret, token, token_created)
    session.generateToken()

    if metric == 'disconnected':
        print('{}'.format(session.sessions_disconnected()))
    elif metric == 'terminated':
        print('{}'.format(session.sessions_terminated()))
    elif metric == 'active':
        print('{}'.format(session.sessions_active()))