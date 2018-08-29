#coding=utf-8
from cryptography.fernet import Fernet

##  key = base64.urlsafe_b64encode(os.urandom(32))  生成key

class prpcrypt():
    def __init__(self):
        self.key = 'Ow2Qd11KeZS_ahNOMicpWUr3nu3RjOUYa0_GEuMDlOc='

    def encrypt(self, password):
        f = Fernet(self.key)
        passwd_encode = password.encode()
        token = f.encrypt(passwd_encode)
        return token.decode()

    def decrypt(self, password):
        f = Fernet(self.key)
        passwd_encode = password.encode()
        token = f.decrypt(passwd_encode)
        return token.decode()
