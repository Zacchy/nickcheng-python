def mbi_encrypt(pToken, nonce):
	'''abcd
	efgh'''
	import struct
	from base64 import standard_b64encode, standard_b64decode
	from Crypto.Hash import HMAC, SHA
	from Crypto.Cipher import DES3
	from Crypto.Util import randpool
	
	CRYPT_MODE_CBC	= 1
	CALC_3DES		= 0x6603
	CALG_SHA1		= 0x8004
	
	def derive_key(key, magic):
		hash1	= HMAC.new(key, magic, SHA).digest()
		
		hash2	= HMAC.new(key, hash1 + magic, SHA).digest()
		hash3	= HMAC.new(key, hash1, SHA).digest()
		
		hash4	= HMAC.new(key, hash3 + magic, SHA).digest()
		
		return hash2 + hash4[0:4]
	
	#
	# Read key and generate two derived keys
	#
	key1	= standard_b64decode(pToken)
	key2	= derive_key(key1, 'WS-SecureConversationSESSION KEY HASH')
	key3	= derive_key(key1, 'WS-SecureConversationSESSION KEY ENCRYPTION')
	
	#
	# Create a HMAC-SHA-1 hash of nonce using key2
	#
	hash	= HMAC.new(key2, nonce, SHA).digest()
	
	#
	# Encrypt nonce with DES3 using key3
	#
	
	# IV: 8 bytes of random data
	iv 		= randpool.KeyboardRandomPool().get_bytes(8)
	obj		= DES3.new(key3, DES3.MODE_CBC, iv)
	
	# XXX: win32's Crypt API seems to pad the input with 0x08 bytes to align on 72/36/18/9 boundary
	ciph	= obj.encrypt(nonce + "\x08\x08\x08\x08\x08\x08\x08\x08")
	
	#
	# Generate the blob
	#
	blob	= struct.pack("<LLLLLLL", 28, CRYPT_MODE_CBC, CALC_3DES, CALG_SHA1, len(iv), len(hash), len(ciph))
	blob	+= iv + hash + ciph
	
	return standard_b64encode(blob)

print mbi_encrypt('W4N4RZdCDDv4TpaabA7C3pwPLngHWQmp', 'AxJSpdLe8vDCK+XzhzyoCaVCYIKspt4yO0QOr1i5oVT30JRYbxh8ory1kFGuszmN')
