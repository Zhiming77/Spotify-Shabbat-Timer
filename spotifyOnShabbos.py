from spotify import app
from spotify import sleep
from spotify.sleep import updater
from datetime import datetime


#start_time = datetime.utcnow()
sleep.startBot()

updater.idle()



if __name__ == "__main__":
    app.run(debug=True)
