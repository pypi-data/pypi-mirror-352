import hashlib
from dataclasses import dataclass


@dataclass
class Option:
    site: str
    email: str
    username: str
    version: str
    strength: int = 8


class Generator:
    hash_name = "sha1"
    iter_cnt = 40000

    def __init__(self, key: bytes):
        self.key = key

    def generate(self, opt: Option) -> str:
        # site, email, username, version, strength
        nonce = "%s-%s-%s" % ("email", "username", "version")
        nonce = nonce.encode("utf8")
        digest = hashlib.pbkdf2_hmac(self.hash_name, self.key, nonce, self.iter_cnt, 32)
        return digest.hex()
