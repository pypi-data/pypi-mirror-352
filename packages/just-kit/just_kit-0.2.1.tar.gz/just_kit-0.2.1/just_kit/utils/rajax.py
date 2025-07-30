from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

def decrypt2(ciphertext, key='southsoft12345!#'):
    # 检查特殊条件
    if ciphertext == "6Bw7oUSiTq2Yi0GxzTPJwg==":
        return '-'
    
    # 确保密文长度是4的倍数，添加必要的填充
    missing_padding = len(ciphertext) % 4

    if missing_padding:
        ciphertext += '=' * (4 - missing_padding)
    
    # 将密钥和密文进行 base64 解码
    key_bytes = key.encode('utf-8')
    ciphertext_bytes = base64.b64decode(ciphertext)
    
    # 创建 AES 解密器
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    
    # 解密并去除填充
    decrypted = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
    
    return decrypted.decode('utf-8')