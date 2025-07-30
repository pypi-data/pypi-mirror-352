# just-kit

江苏科技大学信息门户工具包，用于获取和操作学校信息门户上的各种数据。

## 功能特性

- 宿舍电量查询
- 校园卡余额查询
- 校车信息查询
- 更多功能开发中...

## 安装

```bash
pip install just-kit
```

## 使用方法

### 登入
默认使用信息门户作为登入服务
```python
from just_kit.auth import Authenticator
import os
from dotenv import load_dotenv
# 读取.env
load_dotenv()
# 读取账户以及密码
username = os.getenv('USER')
password = os.getenv('PASSWORD')
# 初始化认证器
authenticator = Authenticator()
authenticator.login(username,password)
```

### 服务:Epay
epay服务用于获取宿舍电费、用户校园卡余额和浴室专款
```python
from just_kit.services import *
# 认证器作为构造参数
epay = EpayServiceProvider(authenticator)
# 通过oauth登入epay的服务
epay.login()
# 获取本账户校园卡余额与浴室专款
epay.query_account_bill()
```


### 服务:HealthCheck
宿舍卫生检查分数查询服务
```python
import os
from just_kit.auth import Authenticator

import dotenv
dotenv.load_dotenv()

auther = Authenticator(vpn=True) #开启VPN模式

auther.login(
    account=os.getenv("USER"),
    password=os.getenv("PASSWORD"))

from just_kit.services import HealthCheckService
service = HealthCheckService(auther)
service.login()
# 获取最近宿舍卫生检查分数
service.get_health_check_data()
# 获取 [HealthCheckData]
# 包含socre和date属性
```

## 开发说明

本项目使用Python 3.11开发，主要依赖：
- requests：用于发送HTTP请求
- beautifulsoup4：用于解析HTML

## 许可证

本项目采用MIT许可证。