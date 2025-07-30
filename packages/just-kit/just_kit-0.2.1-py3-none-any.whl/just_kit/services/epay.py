from typing import Optional

import requests
from bs4 import BeautifulSoup

from .service import ServieProvider
from ..auth import Authenticator


class EpayServiceProvider(ServieProvider):
    """
    用于查询账单信息的类
    """
    SERVICE_URL = "http://202.195.206.214/epay/"
    SERVICE_URL_VPN = "https://client.v.just.edu.cn/http/webvpn90bb547feb721c9a7d03a4a9a66062f4/epay/"

    def __init__(self, auth:Authenticator):
        """
        初始化查询类
        :param auth: Authenticator实例
        """
        super().__init__(auth)

    def service_url(self) -> str:
        return self.SERVICE_URL_VPN if self.auth.vpn else self.SERVICE_URL

    def login(self):
        self.session.get(self.service_url())

    def query_electric_bill(self, room_no: int =4372, sys_id: int = 2, 
                          elc_area: int = 2, elc_buis: int = 4355) -> Optional[float]:
        """
        查询电费
        :param room_no: 房间号
        :param sys_id: 系统ID
        :param elc_area: 电力区域
        :param elc_buis: 电力业务ID
        :return: 剩余电量,查询失败返回None
        """
        url = f"{self.service_url()}/electric/queryelectricbill"
        
        data = {
            "sysid": sys_id,
            "roomNo": room_no,
            "elcarea": elc_area,
            "elcbuis": elc_buis
        }
        
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("retcode") == 0:
                rest_degree = result.get("restElecDegree", 0)
                self.logger.info(f"房间 {room_no} 剩余电量: {rest_degree} 度")
                return rest_degree
            else:
                self.logger.error(f"查询失败: {result.get('message', '未知错误')}")
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            return None
        except ValueError as e:
            self.logger.error(f"解析响应失败: {e}")
            return None

    def query_account_bill(self)->tuple[Optional[float],Optional[float]]:

        '''
        查询账户余额和浴室专款
        :return: 账户余额,浴室专款
        '''
        html_content= self.auth.session.get(f"{self.service_url()}/myepay/index").text

        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 定位账户信息所在的<dd>标签
        dd_tag = soup.find('section', id='content').find('dd')

        # 提取所有<p>标签内容
        p_tags = dd_tag.find_all('p')

        account_balance = None
        bathroom_funds = None

        for p in p_tags:
            text = p.get_text(strip=True)
            if '账户余额' in text:
                account_balance = float(text.split('：')[1].replace('元', ''))
            elif '浴室专款' in text:
                bathroom_funds = float(text.split('：')[1].replace('元', ''))

        return account_balance, bathroom_funds