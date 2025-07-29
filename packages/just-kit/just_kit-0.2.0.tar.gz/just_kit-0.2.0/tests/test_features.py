from just_kit.auth import Authenticator
from just_kit.services import *
from just_kit.utils import decrypt2
import os,json

from dotenv import load_dotenv
load_dotenv()
username = os.getenv('USER')
password = os.getenv('PASSWORD')

auther = Authenticator(vpn=True,auto_login=False)

epay = EpayServiceProvider(auther)
auther.login(username,password)

print(f'auther:{auther.check()}')

epay.login()
print(epay.query_electric_bill())

