import requests
import time
import os.path
import json
import sys

def get_commodities(url, locale, token, file_path: str = ""):
    try:
        if (not os.path.exists(file_path) or
            (time.time() - os.path.getmtime(file_path) > 3600)):
            response = requests.get(
                f'{url}'
                f'auctions/commodities?namespace=dynamic-us'
                f'&locale={locale}',
                headers={"Authorization":f"Bearer {token}"}
            )
            if (response.status_code == 200):
                data = json.loads(response.content)
                return data
            else:
                sys.exit('Authentication failed! '
                     f'Erro HTTP {response.status_code}.')
    except requests.exceptions.ConnectionError as e:
        sys.exit('Conexion failed.')
