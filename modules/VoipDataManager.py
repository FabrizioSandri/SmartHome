import binascii
import math
import base64
import requests
import re 
import hashlib 
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from datetime import datetime

class VoipDataManager:

    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password

        # Random values
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
        self.aes_key = "1703697166759112"   # Random key
        self.aes_iv = "1703697166759112"    # Random iv

    '''
    RSA encrypts plaintext. TP-Link breaks the plaintext down into 64 byte blocks and concatenates the output
    '''
    def rsa_encrypt(self, e, n, plaintext):
        
        rsa_block_size = 64  # This is set by the router
        # Align the input with the block size since PKCS1 padding is not used
        if len(plaintext) % rsa_block_size != 0:
            plaintext += b"\x00" * (rsa_block_size - (len(plaintext) % rsa_block_size))
        num_blocks = int(len(plaintext) / rsa_block_size)
        ciphertext = bytes()
        block_start = 1
        block_end = rsa_block_size
        for block_itr in range(num_blocks):
            # RSA encrypt manually because the cryptography package does not allow RSA without padding because it's unsafe
            plaintext_num = int.from_bytes(plaintext[block_start - 1:block_end], byteorder="big")
            ciphertext_num = pow(plaintext_num, e, n)
            ciphertext += ciphertext_num.to_bytes(math.ceil(n.bit_length() / 8), byteorder="big")
            block_start += rsa_block_size
            block_end += rsa_block_size
        return ciphertext


    '''
    AES-CBC encrypt with PKCS #7 padding. This matches the AES options on TP-Link routers.
    '''
    def aes_encrypt(self, key, iv, plaintext):
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        plaintext_bytes: bytes = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        return ciphertext


    '''
    Requests the public key and sequence from the router.
    '''
    def get_rsa_public_key(self):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Origin": f"http://{self.address}",
            "Connection": "keep-alive",
            "Referer": f"http://{self.address}",
            "Accept-Language": "en-US,en;q=0.5",
        }

        resp = requests.post(f"http://{self.address}/cgi/getGDPRParm", headers=headers)

        # Get the RSA public key (i.e. n and e values)
        match = re.search("nn=\"(.+)\"", resp.text)
        if not match:
            return None
        n_bytes = match.group(1)
        match = re.search("ee=\"(.+)\"", resp.text)
        if not match:
            return None
        e_bytes = match.group(1)

        # Get the sequence. This is set to sequence += data_len and verified server-side.
        match = re.search("seq=\"(.+)\"", resp.text)
        if not match:
            return None
        seq_bytes = match.group(1)

        e = int(e_bytes, 16)
        n = int(n_bytes, 16)
        seq = int(seq_bytes, 10)

        return e, n, seq

    '''
    Authenticates with the TP-Link router and return the JSESSIONID
    '''
    def get_jsessionid(self, username, password):

        # Get the RSA public key parameters and the sequence
        rsa_vals = self.get_rsa_public_key()
        if rsa_vals is None:
            rsa_vals = self.get_rsa_public_key()
            if rsa_vals is None:
                return "Failed to get RSA public key"

        e, n, seq = rsa_vals

        # Create the data field
        aes_key = self.aes_key.encode("utf-8")
        aes_iv = self.aes_iv.encode("utf-8")

        login_data = '{"data":{"UserName":"%s","Passwd":"%s","stack":"0,0,0,0,0,0","pstack":"0,0,0,0,0,0"},"operation":"cgi","oid":"/cgi/login"}' % (username, base64.b64encode(bytes(password, "utf-8")).decode("utf-8"))
        data_ciphertext = self.aes_encrypt(aes_key, aes_iv, login_data.encode())
        data = base64.b64encode(data_ciphertext).decode()
        
        # Create the sign field
        seq_with_data_len = seq + len(data)
        auth_hash = hashlib.md5(f"{username}{password}".encode()).digest()

        plaintext = f"key={self.aes_key}&iv={self.aes_iv}&h={auth_hash.hex()}&s={seq_with_data_len}"
        sign = self.rsa_encrypt(e, n, plaintext.encode())

        # Send the authentication request
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "text/plain",
            "Accept": "*/*",
            "Origin": f"http://{self.address}",
            "Connection": "keep-alive",
            "Referer": f"http://{self.address}/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        }
        request_data = f"sign={sign.hex()}\r\ndata={data}\r\n"
        resp = requests.post(f"http://{self.address}/cgi_gdpr?9", headers=headers, data=request_data)

        # Get the session cookie
        cookie = resp.headers["Set-Cookie"]
        if cookie is None:
            return "Missing Set-Cookie in the response header"
            
        match = re.search(r"JSESSIONID=([a-z0-9]+)", cookie)
        if not match:            
            return "Could not find the JSESSIONID in the response"

        jsessionid = match.group(1)
        
        return jsessionid

    '''
    Get the list of calls in the log
    '''
    def get_calls(self): 
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "text/plain",
            "Accept": "*/*",
            "Connection": "close",
            "Referer": f"http://{self.address}/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
        }
        # Check that the JSESSIONID token is up to date
        jsessionid = self.get_jsessionid(self.username, self.password)

        cookies = {'JSESSIONID': jsessionid}
        resp = requests.get(f"http://{self.address}/main/voice_calllog.cgi", headers=headers, cookies=cookies)
        
        res = resp.text[15:-2].replace("\\r\\n", "")   # Remove prefix and suffix
        res = re.sub(r',\s*', ',', res)
        splitted = res.split(';')[:-1]

        for i in range(len(splitted)):
            splitted[i] = splitted[i].split(',')
            
            parsed_date = datetime.strptime(splitted[i][0], "%Y-%m-%d %H:%M:%S")
            splitted[i][0] = parsed_date.strftime("%d-%m-%Y %H:%M:%S")

        return splitted


