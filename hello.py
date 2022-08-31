from flask import Flask
from flask import request
import  secrets
from oauthlib.oauth2 import WebApplicationClient
import json
import urllib
import requests
import sqlite3
import dotenv
import os
import pandas as pd
import numpy as np

#AUTHORIZATION SET UP
dotenv.load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
client = WebApplicationClient(CLIENT_ID)
#methods to act on this client

# 1. Generate a new Code Verifier / Code Challenge.
def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]
# Create the code verfier and challenge
code_verifier = code_challenge = get_new_code_verifier()
# prepare the URL for authorization
# GET request
def prepare_authorization_url(code_challenge: str):
    authorization_url = 'https://myanimelist.net/v1/oauth2/authorize'
    url = client.prepare_request_uri(
        authorization_url,
        redirect_uri= 'http://127.0.0.1:5000/authorization',
        state= 'ID40',
        code_challenge= code_challenge
    )
    return url


# Method for generating a new token 
def generate_new_token(authorization_code: str, code_verifier: str) -> dict:
    data = client.prepare_request_body(
    code_verifier = code_verifier,
    code = authorization_code,
    redirect_uri ='http://127.0.0.1:5000/authorization',
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    )

    # Library isn't made for this type of url, so we have to change to dictionary
    body =urllib.parse.parse_qsl(data)
    token_url = 'https://myanimelist.net/v1/oauth2/token'
    response = requests.post(token_url,body)
    #print(response.content)
    # Check for any errors
    response.raise_for_status()
    response.close()
    client.parse_request_body_response(response.text)
    # Dump dictionary info into a json file, and return it
    with open('token.json', 'w') as file:
        json.dump(client.token, file, indent = 4)
        #print('Token saved in "token.json"')
    
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
# Method to retrieve user's anime list
def get_user_list(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me/animelist?fields=genres,mean&nsfw=1&limit=10&offset=0' 
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })

    response.raise_for_status()
    user_list = response.json()
    response.close()

    return user_list
# Main
   
# Create flask website 
app = Flask(__name__)

# Routes for website
@app.route('/')
def homepage():
    #Perform OAUTH2.0 on main page (Will change the "here" hyperlink to an auth)
    authurl = prepare_authorization_url(code_challenge)
    return """
    Click
    <a href=%s>world</a>
    """%authurl

@app.route('/authorization')
def oauth2():
    # 
    authorisation_code = request.args.get('code')
    token = generate_new_token(authorisation_code, code_verifier)
    # print_user_info(token['access_token'])

    # Obtain the user's list for website
    user_list = get_user_list(token['access_token'])
    
    # initialize dataframe 
    Y = pd.DataFrame()
    #print(len(user_list["data"]))
    big_list = []
    for anime in user_list["data"]:
        genre_list = []
        genres = anime["node"]["genres"]
        for genre in genres:
            genre_list.append(genre["name"])
        big_list.append(genre_list)

    X = pd.DataFrame(big_list)
    print(X)
    #X.append(genre_list)
    # genre_series = pd.Series(genre_list)
    # X.append(genre_series,ignore_index=True)
    # print(X)
    #put shit in dataframe
    return 'redirect link for authorization'