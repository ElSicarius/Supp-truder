
import jwt

KEY = "example_key"
ALGO = "HS256"

def process(payload):
	if isinstance(payload, bytes):
		try:
			payload = payload.decode("utf8")
		except UnicodeDecodeError:
			print("Invalid payload {}, skipping".format(payload))
	payload = jwt.encode(\
						# change the json according to your jwt setup
						{"id": "1", "name":"test","description":payload,"email":"thisisatest@test.test"},\
						# Enter your key below
						KEY,\
						# change the algorithm if needed
						algorithm=ALGO)
	return payload

def unprocess(payload):
	if isinstance(payload, bytes):
		try:
			payload = payload.decode("utf8")
		except UnicodeDecodeError:
			print("Invalid payload {}, skipping".format(payload))
	payload = jwt.decode(payload,
						# Enter your key below
						KEY,\
						# change the algorithm if needed
						algorithms=[ALGO])
	return payload