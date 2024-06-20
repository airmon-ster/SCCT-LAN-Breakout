import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import getpass
import requests

def main():
    ip = requests.get('https://api.ipify.org').text.strip()
    print("Your public IP address:", ip)

    password = getpass.getpass('Enter password for lobby: ')
    password = password.encode('utf-8')

    salt = b'\xcdS:\x80\xdc\x8b)\x90IT\xd5\xbb\x93\x80\xc2\xd8'

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(password))

    fernet = Fernet(key)

    encrypted_ip = fernet.encrypt(ip.encode('utf-8'))

    print("Share this string with other players connecting:", encrypted_ip.decode('utf-8'))

if __name__ == '__main__':
    main()
