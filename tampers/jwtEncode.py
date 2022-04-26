
import jwt

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
						'example_key',\
						# change the algorithm if needed
						algorithm='HS256')
	return payload