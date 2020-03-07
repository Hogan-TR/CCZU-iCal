import os


RUN_HOST = '0.0.0.0'
RUN_PORT = '5000'

BASE_HOST = "ical.hogantr.me" # Change IP with real ip or domain name

SECRET_KEY = os.urandom(24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

