import requests
from IPython.display import display, Image
from shapely import wkt
from shapely.affinity import scale
import cv2
import numpy as np

BASE_URL = 'https://api.qumranica.org/v1/'

# Get your Auth Token and put it into a headers object
r = requests.post(f"{BASE_URL}users/login", json={'email': 'sirkinolya@gmail.com', 'password': 'password'})
response = r.json()
token = response['token']
headers = {"Authorization": f"Bearer {token}"}


