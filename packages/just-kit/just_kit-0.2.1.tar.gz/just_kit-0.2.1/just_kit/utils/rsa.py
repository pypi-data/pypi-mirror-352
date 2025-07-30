# -*- coding: utf-8 -*-
# 兼容JS security.js加密流程的RSA加密实现
from Crypto.PublicKey import RSA
import binascii

def js_style_rsa_encrypt(data, modulus_hex, exponent_hex):
    # 1. 转换密钥
    modulus = int(modulus_hex, 16)
    exponent = int(exponent_hex, 16)
    key = RSA.construct((modulus, exponent))
    n_bytes = (key.size_in_bits() + 7) // 8

    # 2. JS chunkSize = 2 * (num_digits - 1)
    # 这里num_digits = biHighIndex(m) + 1，biHighIndex返回最高非零digit下标
    # JS的每digit是16位，所以chunkSize = 2*(n_bytes//2 - 1) = n_bytes - 2
    chunk_size = n_bytes - 2

    # 3. 字符转码 + 0填充
    a = [ord(c) for c in data]
    while len(a) % chunk_size != 0:
        a.append(0)

    result = []
    for i in range(0, len(a), chunk_size):
        block = 0
        # JS每2字节拼成一个16位整数，低位在前
        for j in range(chunk_size // 2):
            lo = a[i + 2*j]
            hi = a[i + 2*j + 1]
            block += ((hi << 8) + lo) << (16 * j)
        # 幂模运算
        crypt = pow(block, exponent, modulus)
        # 转16进制，不足n_bytes*2位补零
        hex_str = hex(crypt)[2:]
        hex_str = hex_str.rjust(n_bytes*2, '0')
        result.append(hex_str)
    # 用空格连接
    return ' '.join(result)

modulus_hex = "008aed7e057fe8f14c73550b0e6467b023616ddc8fa91846d2613cdb7f7621e3cada4cd5d812d627af6b87727ade4e26d26208b7326815941492b2204c3167ab2d53df1e3a2c9153bdb7c8c2e968df97a5e7e01cc410f92c4c2c2fba529b3ee988ebc1fca99ff5119e036d732c368acf8beba01aa2fdafa45b21e4de4928d0d403"
exponent_hex = "010001"

def encrypt(data:str):
    return js_style_rsa_encrypt(data, modulus_hex, exponent_hex)