from just_kit.auth import Authenticator
from just_kit.services import *
from just_kit.utils import decrypt2
import os,json

from dotenv import load_dotenv
load_dotenv()
username = os.getenv('USER')
password = os.getenv('PASSWORD')

auther = Authenticator()
yjskb = GraduateServiceProvider(auther)
epay = EpayServiceProvider(auther)
auther.login(username,password)

yjskb.login()
term = yjskb.terms()[0]['termcode']
print('---------------')
courses = yjskb.courses(term)
print('---------------')
print(json.dumps(courses,ensure_ascii=False))
print('---------------')
epay.login()
print(epay.query_account_bill())

