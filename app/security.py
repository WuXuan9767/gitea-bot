import hashlib
import base64
from Crypto.Cipher import AES
from config import Config
import hmac 

def verify_signature(Signature: str, payload: str, Authorization: str) -> bool:

    if not Authorization or Authorization != Config.GITEA_AUTHORIZATION:
        return False
    
    if Signature is None:
        return False

    # 验证签名
    mac = hmac.new(Config.GITEA_SECRET.encode(), msg=payload.encode(), digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()
    result = hmac.compare_digest(Signature, expected_signature)
    return result


class  AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key=hashlib.sha256(AESCipher.str_to_bytes(key)).digest()
    @staticmethod
    def str_to_bytes(data):
        u_type = type(b"".decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data
    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return  self._unpad(cipher.decrypt(enc[AES.block_size:]))
    def decrypt_string(self, enc):
        enc = base64.b64decode(enc)
        return  self.decrypt(enc).decode('utf8')

cipher = AESCipher(Config.LARK_ENCRYPT_KEY)