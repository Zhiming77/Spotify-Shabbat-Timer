from flask import Flask

app = Flask(__name__)

from spotify import routes
