import  secrets
import secretss
from oauthlib.oauth2 import WebApplicationClient
import json
import urllib
import requests
#Documentation: https://myanimelist.net/apiconfig/references/api/v2

#test authorization to MAL
# WebApplicationClient implements web application flow
client = WebApplicationClient(secretss.Client_ID)

#methods to act on this client

# 1. Generate a new Code Verifier / Code Challenge.
def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]

# prepare the URL for authorization
# GET request
def prepare_authorization_url(code_challenge: str):
    authorization_url = 'https://myanimelist.net/v1/oauth2/authorize'
    url = client.prepare_request_uri(
        authorization_url,
        #redirect_uri= 'http://127.0.0.1:5000',
        state= 'ID40',
        code_challenge= code_challenge
    )
    print(url)


# Method for generating a new token 
def generate_new_token(authorization_code: str, code_verifier: str) -> dict:
    data = client.prepare_request_body(
    code_verifier = code_verifier,
    code = authorization_code,
    redirect_uri ='http://127.0.0.1:5000',
    client_id = secretss.Client_ID,
    client_secret = secretss.Client_Secret,
    )

    # Library isn't made for this type of url, so we have to change to dictionary
    body =urllib.parse.parse_qsl(data)
    token_url = 'https://myanimelist.net/v1/oauth2/token'
    response = requests.post(token_url,body)
    print(response.content)
    # Check for any errors
    response.raise_for_status()
    response.close()
    client.parse_request_body_response(response.text)
    # Dump dictionary info into a json file, and return it
    with open('token.json', 'w') as file:
        json.dump(client.token, file, indent = 4)
        print('Token saved in "token.json"')
    
    return client.token

# Testing the API with newly recieved token
def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"\n>>> Greetings {user['name']}! <<<")
# Main
if __name__ == '__main__': 
    code_verifier = code_challenge = get_new_code_verifier()
    prepare_authorization_url(code_challenge)
    #authorisation_code = input('Copy-paste the Authorisation Code: ').strip()\
    authorization_code = requests.args.get('code')
    token = generate_new_token(authorization_code, code_verifier)
    print_user_info(token['access_token'])