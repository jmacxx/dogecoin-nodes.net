#!/usr/bin/env python

"""encode/decode base58 in the same way that Bitcoin does"""

from Crypto.Hash import SHA256
import hashlib
#import hmac
import binascii
import struct
import codecs


__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
  """ encode v, which is a string of bytes, to base58.    
  """
  long_value = 0
  for (i, c) in enumerate(v[::-1]):
    long_value += (256**i) * c

  result = ''
  while long_value >= __b58base:
    div, mod = divmod(long_value, __b58base)
    result = __b58chars[mod] + result
    long_value = div
  result = __b58chars[long_value] + result

  # Bitcoin does a little leading-zero-compression:
  # leading 0-bytes in the input become leading-1s
  nPad = 0
  for c in v:
    if c == 0: nPad += 1
    else: break

  return (__b58chars[0]*nPad) + result

def b58decode(v, length):
  """ decode v into a string of len bytes
  """
  long_value = 0
  for (i, c) in enumerate(v[::-1]):
    long_value += __b58chars.find(c) * (__b58base**i)

  result = b''
  while long_value >= 256:
    div, mod = divmod(long_value, 256)
    result = struct.pack('<B', int(mod)) + result
    long_value = div
  result = struct.pack('<B', int(long_value)) + result

  nPad = 0
  for c in v:
    if c == __b58chars[0]: nPad += 1
    else: break

  #result = chr(0)*nPad + result
  result = bytes(nPad) + result     # JMC
  if length is not None and len(result) != length:
    return None

  return result    # JMC convert the string formatted hexadecimal numbers to raw bytes

def getNewRIPEMD160ByHashlib(public_key=""):
  newRIPEMD160 = hashlib.new('ripemd160')
  bytes_key = public_key
  if type(public_key) is str:
    bytes_key = public_key.encode('utf-8')
  newRIPEMD160.update(bytes_key)
  return newRIPEMD160

def doublesha256(data):
  return SHA256.new(SHA256.new(data).digest()).digest()

def singlesha256(data):
  return SHA256.new(data).digest()

def hash_160(public_key):
  h1 = singlesha256(public_key)
  h2 = getNewRIPEMD160ByHashlib(h1).digest()
  return h2

def public_key_to_bc_address(magic1, public_key):
  h160 = hash_160(public_key)
  return hash_160_to_bc_address(magic1, h160)

def hash_160_to_bc_address(magic1, h160):
  vh160 = codecs.decode(magic1, 'hex_codec')+h160  # b"\x00"=bitcoin  b"\x1e"=Dogecoin  b"\x05"=segwit
  h3=doublesha256(vh160)
  addr=vh160+h3[0:4]
  return b58encode(addr)

def privkeyToWif(magic2, priv):
  vpriv = codecs.decode(magic2, 'hex_codec')+priv+b"\x01"  # \x9e is version Dogecoin, 01 is compressed key
  h3=doublesha256(vpriv)
  return b58encode(vpriv+h3[0:4])

def wifToPrivkey(wif):
  tmp = b58decode(wif, None)
  PRIVATE_KEY = tmp[1:-5]
  return PRIVATE_KEY

def bc_address_to_hash_160(addr):
  bytes = b58decode(addr, 25)
  return bytes[1:21]

def addressValidate(addr):
  bytes = b58decode(addr, 25)
  front = bytes[0:21]
  back = binascii.hexlify(bytes[21:25])
  checksum = binascii.hexlify(doublesha256(front)[0:4])
  if checksum == back:
    return True
  return False


if __name__ == '__main__':

    x = bytes.fromhex('005cc87f4a3fdfe3a2346b6953267ca867282630d3f9b78e64')
    encoded = b58encode(x)
    print(encoded, '19TbMSWwHvnxAKy12iNm3KdbGfzfaMFViT');

    #print(b58decode(encoded, len(x)).encode('hex_codec'), x.encode('hex_codec'));
    y = b58decode(encoded, len(x))
    print(binascii.hexlify(y), binascii.hexlify(x))

