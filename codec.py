from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

def RSA_encrypt(public_key, message):
    if not globals().get('RSA'):
        return ''
    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_v1_5.new(rsakey)
    encrypted = rsakey.encrypt(message.encode())
    return base64.encodestring(encrypted).decode().replace('\n', '')


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def base36decode(number):
    return int(number, 36)
