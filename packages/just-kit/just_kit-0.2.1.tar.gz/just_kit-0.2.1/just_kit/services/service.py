from just_kit.auth import Authenticator
import logging
from just_kit.utils import *

class ServieProvider:
    def __init__(self,auth:Authenticator,service=''):
        self.auth = auth
        self.session = auth.session
        self.logger = logging.getLogger(__name__)
        self.service = service
        self.headers = {
            "Host": get_host_from_url(self.service),
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        }
    
    def check(self):
        """
        检查登录是否失效
        :return: 如果登录有效返回True,否则返回False
        """
        res = self.session.get(
            self.service,
            allow_redirects=False,
        )
        if res.status_code == 302:
            return False
        else:
            return True

    def service_url(self)->str:
        """
        获取服务地址
        """
        pass