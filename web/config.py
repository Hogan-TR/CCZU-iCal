import os


RUN_HOST = '127.0.0.1'
RUN_PORT = '6161'

BASE_HOST = "ical.minitr.tech" # Change IP with real ip or domain name

SECRET_KEY = os.urandom(24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

