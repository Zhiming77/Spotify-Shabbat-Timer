import configparser
import os
from decouple import config


auth = {}

auth['telegram_bot_token']=os.environ.get('BOT_TOKEN')
auth['spotify_client_id']=os.environ.get('SPOTIFY_CLIENT_ID')
auth['spotify_client_secret']=os.environ.get('SPOTIFY_CLIENT_SECRET')
auth['spotify_redirect_uri']=os.environ.get('SPOTIFY_REDIRECT_URI')
auth['token_info']=os.environ.get('TOKEN_INFO')



if auth['telegram_bot_token'] == None:
    if config('telegram_bot_token')!="":
        auth['telegram_bot_token'] = config('telegram_bot_token')
    else:
        raise RuntimeError('telegram bot token not found 🙁! Put bot token🔐 in environmental variables!')

if auth['spotify_client_id']==None:
    if config('spotify_client_id')!="":
        auth['spotify_client_id'] = config('spotify_client_id')
    else:
        raise RuntimeError('spotify client ID not found 🙁! Put API in environmental variables!')

if auth['spotify_client_secret']==None:
    if config('spotify_client_secret')!="":
        auth['spotify_client_secret'] = config('spotify_client_secret')
    else:
        raise RuntimeError('spotify client secret not found 🙁! Put API in environmental variables!')

if auth['token_info']==None:
    if config('token_info')!="":
        auth['token_info'] = config('token')
    else:
        raise RuntimeError('token info not found 🙁! Put API in environmental variables!')

if auth['spotify_redirect_uri']==None:
    if config('spotify_redirect_uri')!="":
        auth['spotify_redirect_uri'] = config('spotify_redirect_uri')
    else:
        raise RuntimeError('redirect uri not found 🙁! Put API in environmental variables!')


config = configparser.ConfigParser()
config['spotify']={}
#spotify_client_id = auth['spotify_client_id']
#spotify_client_secret = auth['spotify_client_secret']
config['spotify']['client_id']= fr"{auth['spotify_client_id']}"
config['spotify']['client_secret']= fr"{auth['spotify_client_secret']}"
config['spotify']['redirect_uri']= fr"{auth['spotify_redirect_uri']}"
config['spotify']['token_info']= fr"{auth['token_info']}"


config['telegram']={}
config['telegram']['telegram_bot_token']=fr"{auth['telegram_bot_token']}"

with open('config.ini', 'w') as configfile:
    config.write(configfile)
