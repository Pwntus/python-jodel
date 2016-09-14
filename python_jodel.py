import sys
import ast
import random
import datetime
import json
import base64
import hmac
from hashlib import sha1
from urllib.parse import urlparse
import requests

# DO NOT EDIT ANY CONFIGS HERE
# READ THE DOCUMENTATION FOUND AT GITHUB
PYTHON_JODEL_CONFIG = {
	'client_id'			: '81e8a76e-1e02-4d17-9ba0-8a7020261b26',
	'api_url'			: 'https://api.go-tellm.com/api',
	'device_uid'		: None,
	'access_token'		: None,
	'expiration_date' 	: None,
	'refresh_token'		: None,
	'distinct_id'		: None,
	'location'			: {
		'lat'			: 69.651996,
		'lng'			: 18.948217,
		'city'			: 'Tromso',
		'country'		: 'NO',
		'name'			: 'Tromso'
	}
}
PYTHON_JODEL_CONFIG_FILE = 'pj_config'
PYTHON_JODEL_HMAC_KEY = bytearray([74, 121, 109, 82, 78, 107, 79, 71, 68, 85, 72, 81, 77, 86, 101, 86, 118, 100, 122, 118, 97, 120, 99, 75, 97, 101, 117, 74, 75, 87, 87, 70, 101, 105, 104, 110, 89, 110, 115, 89])
PYTHON_JODEL_HEADERS = {
	'User-Agent'		: 'Jodel/4.4.9 Dalvik/2.1.0 (Linux; U; Android 5.1.1; )',
	'Accept-Encoding'	:'gzip',
	'Content-Type'		:'application/json; charset=UTF-8'
}

class Client:
	config 		= None
	_loc_str 	= None
	_s 			= None

	def __init__(self, location = None):
		self.config = PYTHON_JODEL_CONFIG
		self._s = requests.Session()

		self._set_loc_str(location)
		self._load_config()

		if location:
			self.update_location(location)

	def _error(self, msg):
		sys.exit('Error: '+ msg)

	def _warning(self, msg):
		print('Warning: '+ msg)

	def _log(self, msg):
		print('Info: '+ msg)

	def _set_loc_str(self, location):
		ref = location if location else PYTHON_JODEL_CONFIG['location']
		self._loc_str = '"location":{"loc_accuracy":1,"city":"%s","loc_coordinates":{"lat":%f,"lng":%f},"country":"%s","name":"%s"}' % (ref['city'], ref['lat'], ref['lng'], ref['country'], ref['name'])

	def _touchopen(self, fn, *args, **kwargs):
		"""
		Creates a file if it doesn't exist.
		Returns the opened file.
		"""
		try:
			open(fn, 'a').close()
		except IOError as e:
			self._error('failed to load config file: '+ e.strerror);

		return open(fn, *args, **kwargs)

	def _load_config(self):
		"""
		Load or create the config file.
		"""
		try:
			with self._touchopen(PYTHON_JODEL_CONFIG_FILE, 'r+') as f:
				try:
					self.config = ast.literal_eval(f.read())
				except:
					self._warning('failed to parse config file, loading defaults')
					self._refresh_tokens()
		except IOError as e:
			self._error('failed to load config file: '+ str(e.strerror));

	def _sign_request(self, method, url, headers, payload = None):
		timestamp = datetime.datetime.utcnow().isoformat()[:-7] +'Z'

		req = [
			method,
			urlparse(url).netloc,
			'443',
			urlparse(url).path,
			self.config['access_token'] if self.config['access_token'] else '',
			timestamp
		]
		req.extend(sorted(urlparse(url).query.replace('=', '%').split('&')))
		req.append(payload if payload else '')
        
		signature = hmac.new(PYTHON_JODEL_HMAC_KEY, '%'.join(req).encode('utf-8'), sha1).hexdigest().upper()

		headers['X-Authorization'] = 'HMAC '+ signature
		headers['X-Client-Type'] = 'android_4.17.1'
		headers['X-Timestamp'] = timestamp
		headers['X-Api-Version'] = '0.2'

	def _send_request(self, method, endpoint, payload = None):
		url = self.config['api_url'] + endpoint
		headers = PYTHON_JODEL_HEADERS

		if self.config['access_token']:
			headers['Authorization'] = 'Bearer '+ self.config['access_token']

		self._sign_request(method, url, headers, payload)
		payload = payload.encode('utf-8') if payload is not None else None

		r = self._s.request(method = method, url = url, data = payload, headers = headers)
		try:
			resp_text = json.loads(r.text, encoding = 'utf-8')
		except:
			resp_text = r.text

		return r.status_code, resp_text

	def _refresh_tokens(self):
		"""
		Gets all tokens needed.
		Equals to creating a new Jodel account.
		"""
		self.config['device_uid'] = ''.join(random.choice('abcdef0123456789') for _ in range(64))

		payload = '{"client_id":"%s","device_uid":"%s",%s}' % (self.config['client_id'], self.config['device_uid'], self._loc_str)

		r = self._send_request('POST', '/v2/users', payload)
		if r[0] == 200:
			self.config['access_token'] 	= r[1]['access_token']
			self.config['expiration_date'] 	= r[1]['expiration_date']
			self.config['refresh_token'] 	= r[1]['refresh_token']
			self.config['distinct_id'] 		= r[1]['distinct_id']
		else:
			self._error('failed to refresh tokens (HTTP code '+ str(r[0]) +')')
		try:
			with open(PYTHON_JODEL_CONFIG_FILE, 'w') as f:
				f.write(str(self.config))
		except IOError as e:
			self._error('failed to write config file: '+ e.strerror)
		self._log('wrote new config file')

		return r