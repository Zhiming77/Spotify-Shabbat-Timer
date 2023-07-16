import time
import spotipy
from spotipy import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth
from telegram.ext import Updater, CommandHandler, filters, MessageHandler, Filters
from config import auth
from config import config as config_file
import logging
import json
import os
#import telegram
#from telegram import Chat

#Spotify API credentials
#config_file = config_file

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',level=logging.INFO
)

logger = logging.getLogger(__name__)



#get Credentials
def get_credentials():
    config = configparser.ConfigParser()
    config_file = config.read('config.ini')


client_id = config_file['spotify']['client_id']
client_secret = config_file['spotify']['client_secret']
redirect_uri = config_file['spotify']['redirect_uri']
spotify_token_info = config_file['spotify']['token_info']

#Telegram Bot Token
bot_token = config_file['telegram']['telegram_bot_token']

#initialize the Updater with your bot token
updater = Updater(token=bot_token, use_context=True)

#Sleep timer duration in seconds
sleep_duration = 5400

#Spotify playlist or track URI to play during the sleep timer
#_playlist =  'https://open.spotify.com/playlist/2Apr16RNdnx9lKeBTYyHTw?si=63af20ea464a4c18'
#playlist_uri = _playlist

# Authenticate with Spotify API
scope = "playlist-read-private, user-modify-playback-state"
token_info=json.loads(spotify_token_info)
_scope = token_info["scope"]
logging.warning(f"token scope is {_scope}")
#MemoryCacheHandler = MemoryCacheHandler(token_info=token_info)

sp = spotipy.Spotify(
    oauth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        #cache_path=".cache",
        show_dialog=False,
        open_browser=False,
        cache_handler=MemoryCacheHandler(token_info=token_info)
        )
)

MemoryCacheHandler.save_token_to_cache(self=sp, token_info=token_info)
logging.warning(f"sp is {sp}")
# Get user's playlists

playlists = sp.current_user_playlists()

#create a global variable to store the start time of the timer
start_time = None

#create a global variable for notificataion timing
time_to_display = None

# Prepare a list of available playlists
available_playlists = []
for playlist in playlists['items']:
    playlist_name = playlist['name']
    playlist_uri = playlist['uri']
    available_playlists.append((playlist_name, playlist_uri))

#get user's playlists
def get_user_playlist():
    playlists = sp.current_user_playlists()
    return playlists

#Print playlist names and URIs
def print_playlists(playlists):
    for playlist in playlists['items']:
        print('Playlist: ', playlist['name'])
        print('URI: ', playlist['uri'])
        print()

#Call Functions
#user_playlists = get_user_playlist()
#print_playlists(user_playlists)

# Define the /start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Shalom I am the Shabbos Sleep Timer Bot. My Name is Miriam!")


# Define the /setplaylist command handler
def show_playlists(update, context):
    user_id = update.message.from_user.id



    #create a string with the available playlists for user selection
    playlist_options = '\n'.join([f'{i+1}. {playlist[0]}' for i, playlist in enumerate(available_playlists)])

    #Send message to user to choose a playlist
    context.bot.send_message(chat_id=user_id,
                             text="Please choose a shabbos playlist:\n"+ playlist_options)

    #Store the available playlists in the user's context for later retrieval
    context.user_data['available_playlists'] = available_playlists


# Define the /selectplaylist command handler
def select_playlist(update, context):
    user_id = update.message.from_user.id
    selected_index = int(context.args[0]) - 1

    #Retrieve the available playlists from the user's context
    available_playlists = context.user_data.get('available_playlists')

    if available_playlists and 0 <= selected_index < len(available_playlists):
        selected_playlist_name = available_playlists[selected_index][0]
        #Store the selected playlist URI as the sleep timer playlist
        global playlist_uri
        playlist_uri = available_playlists[selected_index][1]

        context.bot.send_message(chat_id=user_id,
                                 text=f"Playlist set to: {selected_playlist_name}")

    else:
        context.bot.send_message(chat_id=user_id,
                                 text="Invalid playlist selection")

# Define the /setduration command handler
def set_duration(update, context):
    global sleep_duration
    sleep_duration = float(context.args[0])*60
    global time_to_display
    time_to_display = round(sleep_duration/60)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Sleep duration set to: {time_to_display} minute(s)")

# Define the /timer command handler

def start_timer(update, context):

    global start_time

    if playlist_uri is None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                text="Please set the playlist using /setplaylist command first.")

        return

    if start_time is None:
        start_time = time.time()

    # Start playback

    sp.start_playback(context_uri=playlist_uri)


    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Shabbos Sleep Timer Beginning Now!")

    # timer update functionality
    '''context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"time is now{start_time}")'''

    remaining_time = sleep_duration - (time.time() - start_time)
    logging.warning(f"remaing time is {remaining_time}")

    while remaining_time > 60:
        # Caluclate time remaining
        minutes_remaining = (remaining_time // 60)

        # Send update every 5 minute if the timer is set to at least 10 minutes

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Time remaining on sleep timer: {minutes_remaining}")
        remaining_time = sleep_duration - (time.time() - start_time)
        logging.warning(f"remaing time is {remaining_time}")
        # sleep for 1 minute
        time.sleep(60)

    # Wait for the specified sleep duration
    time.sleep(sleep_duration)

    # Pause playback
    sp.pause_playback()

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Shabbos Sleep Timer Completed!")



# Get the dispatcher to  register handlers
#dispatcher = updater.dispatcher

#Register the command handlers
start_handler = CommandHandler('start', start)
show_playlists_handler = CommandHandler('showplaylists', show_playlists)
select_playlist_handler = CommandHandler('selectplaylist', select_playlist)
set_duration_handler = CommandHandler('setduration', set_duration)
timer_handler = CommandHandler('starttimer', start_timer)
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(show_playlists_handler)
updater.dispatcher.add_handler(set_duration_handler)
updater.dispatcher.add_handler(timer_handler)
updater.dispatcher.add_handler(select_playlist_handler)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I did not understand that command.")


unknown_handler = MessageHandler(Filters.command, unknown)
updater.dispatcher.add_handler(unknown_handler)

PORT = int(os.environ.get('PORT',5000))

# Start the bot

#updater.start_polling()

def startBot():
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=auth['telegram_bot_token'])
    updater.bot.setWebhook('https://spotify-shabbos-bot-4d92d71fce44.herokuapp.com/' + auth['telegram_bot_token'])


def stopBot():
    updater.stop()
