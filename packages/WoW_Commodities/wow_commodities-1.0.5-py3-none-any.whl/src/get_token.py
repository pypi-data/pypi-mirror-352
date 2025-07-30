import requests
import json
import sys

def get_token(id: str, secret: str, region: str) -> str:
    try:
        if region == 'cn':
            URL='https://www.battlenet.com.cn/oauth/token'
        else:
            URL='https://oauth.battle.net/token'

        return json.loads(
            requests.post(
            url=URL,
            auth=(id, secret), # type: ignore
            data={'grant_type': 'client_credentials'},
            ).content
        )['access_token']
    except:
        sys.exit('Authentication failed. '
              'Check your credentials, connection and try again.')