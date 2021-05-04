from flask import Flask
from app import db


app = Flask(__name__)
db.init_app(app)

from app import routes