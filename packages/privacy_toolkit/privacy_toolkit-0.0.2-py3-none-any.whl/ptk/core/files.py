from __future__ import annotations

import hashlib
import os
import secrets
import struct
import time
import typing
from pathlib import Path

import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def iter_bytes(rd: typing.BinaryIO, buf_size=2048):
    while True:
        buf = rd.read(buf_size)
        if not buf:
            break
        yield buf


class AbstractCipher:
    ID: int = None

    def __init__(self, passwd: bytes):
        pass

    def encrypt(self, fin: typing.BinaryIO, fout: typing.BinaryIO):
        raise NotImplementedError

    def decrypt(self, fin: typing.BinaryIO, fout: typing.BinaryIO):
        raise NotImplementedError


class ChaChaCipher(AbstractCipher):
    ID = 67  # 'C'

    def __init__(self, passwd: bytes):
        if len(passwd) != 32:
            # all the arguments to pbkdf2_hmac should not be changed,
            # otherwise it won't decrypt previously encrypted files.
            passwd = hashlib.pbkdf2_hmac("sha1", passwd, b"a1ign", 10, 32)

        super().__init__(passwd)
        self.key = passwd

    def make_nonce(self):
        nonce = secrets.token_bytes(8)
        counter = time.time()
        return struct.pack("<d", counter) + nonce

    def make_cipher(self, nonce: bytes) -> Cipher[algorithms.ChaCha20]:
        algorithm = algorithms.ChaCha20(self.key, nonce)
        return Cipher(algorithm, mode=None)

    def encrypt(self, fin: typing.BinaryIO, fout: typing.BinaryIO):
        nonce = self.make_nonce()
        fout.write(nonce)

        cipher = self.make_cipher(nonce)
        encryptor = cipher.encryptor()
        for buf in iter_bytes(fin):
            buf = encryptor.update(buf)
            fout.write(buf)

    def decrypt(self, fin: typing.BinaryIO, fout: typing.BinaryIO):
        nonce = fin.read(16)
        cipher = self.make_cipher(nonce)
        decryptor = cipher.decryptor()
        for buf in iter_bytes(fin):
            buf = decryptor.update(buf)
            fout.write(buf)


class AESCipher(AbstractCipher):
    ID = 65  # 'A'

    def __init__(self, passwd: bytes):
        if len(passwd) != 32:
            # all the arguments to pbkdf2_hmac should not be changed,
            # otherwise it won't decrypt previously encrypted files.
            passwd = hashlib.pbkdf2_hmac("sha1", passwd, b"a1ign", 10, 32)
        super().__init__(passwd)
        self.key = passwd

    def make_cipher(self, iv: bytes) -> Cipher[modes.CTR]:
        return Cipher(algorithms.AES(self.key), modes.CTR(iv))

    def encrypt(self, fin: typing.BinaryIO, fout: typing.BinaryIO):
        iv = secrets.token_bytes(16)
        fout.write(iv)

        cipher = self.make_cipher(iv)
        encryptor = cipher.encryptor()

        for buf in iter_bytes(fin):
            buf = encryptor.update(buf)
            fout.write(buf)
        fout.write(encryptor.finalize())

    def decrypt(self, fin: typing.BinaryIO, fout: typing.BinaryIO):
        iv = fin.read(16)
        cipher = self.make_cipher(iv)
        decryptor = cipher.decryptor()

        for buf in iter_bytes(fin):
            buf = decryptor.update(buf)
            fout.write(buf)
        fout.write(decryptor.finalize())


class FileCryptor:
    cipher_classes: typing.ClassVar = {cls.ID: cls for cls in (ChaChaCipher, AESCipher)}

    def __init__(self, pwd: bytes, default_cipher_cls: type[AbstractCipher]):
        self.pwd = pwd
        self.default_cipher_cls = default_cipher_cls

    def encrypt_stream(
        self,
        fin: typing.BinaryIO,
        fout: typing.BinaryIO,
        cipher_cls: type[AbstractCipher],
    ) -> None:
        if cipher_cls is None:
            cipher_cls = self.default_cipher_cls

        # ver - salt/once - data
        ver = struct.pack("B", cipher_cls.ID)
        fout.write(ver)

        cipher = cipher_cls(self.pwd)
        cipher.encrypt(fin, fout)

    def encrypt(
        self,
        filein: Path | str,
        out: Path | str | typing.BinaryIO,
        cipher_cls: type[AbstractCipher] | None = None,
    ):
        with open(filein, "rb") as fin:
            if isinstance(out, (Path, str)):
                with open(out, "wb") as fout:
                    self.encrypt_stream(fin, fout, cipher_cls)
                return
            self.encrypt_stream(fin, out, cipher_cls)

    def decrypt_stream(self, fin: typing.BinaryIO, fout: typing.BinaryIO) -> None:
        (ver,) = struct.unpack("B", fin.read(1))
        try:
            cipher_cls = self.cipher_classes[ver]
        except KeyError as exc:
            raise ValueError(f"Unsupported cipher version: {ver}") from exc

        cipher = cipher_cls(self.pwd)
        cipher.decrypt(fin, fout)

    def decrypt(self, filein: Path | str, out: Path | str | typing.BinaryIO):
        with open(filein, "rb") as fin:
            if isinstance(out, (Path, str)):
                with open(out, "wb") as fout:
                    self.decrypt_stream(fin, fout)
                return
            self.decrypt_stream(fin, out)


class KeyMan:
    def __init__(self, file: Path = "~/.config/pass"):
        self.file = Path(file).expanduser()

    def load(self) -> None | bytes:
        if not self.file.exists():
            return None
        with open(self.file, "rb") as f:
            return f.read()

    def _ensure_file(self):
        if self.file.exists():
            if not self.file.is_file():
                raise RuntimeError("path %s already exists but is not a file", self.file)
            return

        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, "wb") as f:
            f.write(b"")
            os.fchmod(f.fileno(), 0o600)

    def reset_passwd(self, passwd: bytes) -> bytes:
        key = hashlib.pbkdf2_hmac("sha1", passwd, b"hid3", 480000, 32)
        self._ensure_file()
        with open(self.file, "wb") as f:
            f.write(key)
        return key


class FileFlipper:
    def __init__(self, size: int = 256):
        self.size = size

    def flip(self, filename: Path | str, size: int | None = None):
        if size is None:
            size = self.size

        with open(filename, "r+b") as f:
            buf = f.read(size)
            arr = np.frombuffer(buf, dtype=np.uint8)
            buf = np.bitwise_invert(arr).tobytes()
            f.seek(0, os.SEEK_SET)
            f.write(buf)
