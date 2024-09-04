import os
from dotenv import load_dotenv
import base64

load_dotenv()

username = os.getenv('MEDELEMENT_USERNAME')
password = os.getenv('MEDELEMENT_PASSWORD')

base64_string = f'{username}:{password}'.encode('ascii')
base64_credentials = base64.b64encode(base64_string).decode('ascii')
headers = {
    'Authorization': f'Basic {base64_credentials}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
