import pytest
from just_kit.auth import Authenticator
import os
from dotenv import load_dotenv

load_dotenv()

encrypted_password = "60eef716064e948fbd32633c6c4832ea7728c2d82d5cfbf88d1d0265170e3e5ee5fb4da9de1726482d15b9905036b8f8f58dd21406ccfcbda5ddd87e46919a34aefb29841b4de1ab098f19a4fa479653336f2f169543fa68a3e4f507f7663b47c27b1b37b1368f5585ea156ad81deb92f19641b54cd0cf243644ede0fc696223"

@pytest.fixture
def auth():
    # 创建一个测试用的Authenticator实例
    return Authenticator("http://test.service.com")

def test_encryption_consistency(auth):
    """测试两种加密方法的结果是否一致"""


    py_result = auth.encrypt_with_js(os.environ.get('PASSWORD'))

    # 确保两个函数都返回了非None的结果
    assert py_result is not None, f"Python encryption failed for password: {password}"

    # 比较两种加密方法的结果是否一致
    assert encrypted_password == py_result, \
        f"Encryption results differ for password: {password}\n" \
        f"Python result: {py_result}"
