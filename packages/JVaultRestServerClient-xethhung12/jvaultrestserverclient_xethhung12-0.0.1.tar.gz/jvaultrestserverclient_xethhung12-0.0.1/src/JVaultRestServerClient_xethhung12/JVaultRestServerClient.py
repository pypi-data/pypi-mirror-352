import os
import requests
import hashlib


class JValueRestServerClient:
    @staticmethod
    def gen_non_secure()->str:
        return f"localhost,7910,false,"

    @staticmethod
    def gen_harden_connection()->str:
        return f"localhost,7910,false,harden"

    @staticmethod
    def gen_non_secure()->str:
        return f"localhost,7910,false,70110b5d-a0f3-4631-b4ae-1ac1d9a6218e"

    def __init__(self):
        j_vault_conf = os.getenv("using-j-vault-rest-server")
        if j_vault_conf is not None:
            host, port, secure_conn, secure_mode = j_vault_conf.split(",")
            self.secure_mode = secure_mode
            self.secure_conn = secure_conn.lower() == "true"
            self.host = host
            self.port = port
            self.load()

    def load(self):
        token = None if self.secure_mode == "" else hashlib.md5(
            f"http://0.0.0.0:{self.port}".encode("utf-8")).hexdigest() if self.secure_mode == "harden" else self.secure_mode

        base_url = f"{'https' if self.secure_conn else 'http'}://{self.host}:{self.port}"
        keys_url = f"{base_url}/kvs{ '' if token is None else f'?token={token}' }"
        rs = requests.get(keys_url).json()
        for key in rs:
            os.environ[key] = rs[key]

if __name__ == '__main__':
    os.environ["using-j-vault-rest-server"]=JValueRestServerClient.gen_harden_connection()
    JValueRestServerClient()