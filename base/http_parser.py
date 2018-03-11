import re
from base.Standered_time import Std_time

Stime = Std_time()
pattern = r'(.*?) (/[^?]*)[\?]*(.*) (.*/.*)\n([\s\S]*)'
compiler = re.compile(pattern)
'''Basic parser '''
class Http_parser(object):
	def __init__(self):
		pass
	
	#request
	def parse(self,raw_text):
		method = ""
		url = ""
		version = ""
		headers = dict()
		args = dict()
		data = dict()
		
		try:
			front,raw_data = raw_text.split('\n\n')
			for i in raw_data.split('&'):
				k,v = i.split('=')
				data[k] = v
		except ValueError as e: #no post data
			front = raw_text
		request_method,url,raw_args,version,raw_headers,= compiler.findall(front)[0]
		for i in raw_args.split('&'):
			k,v = i.split('=')
			args[k] = v
		for i in raw_headers.split('\n'):
			k,v = re.findall(r'(.*): (.*)',i)[0]
			headers[k] = v
			
		info = {
			'method':method,
			'url':url,
			'version':version,
			'headers':headers,
			'args':args,
			'data':data
			}
			
		return info
	
	#response
	#headers : dict()
	def pack(self,status_code='200',status_msg='OK',headers=dict(),text=''):
		
		#check some headers
		headers_list = [ x.upper() for (x,_) in list(headers.items())]
		if 'DATE' not in headers_list:
			headers['Date'] = Stime.http_time()
		if 'CONTENT-TYPE' not in headers_list:
			headers['Content-Type']	= 'text/plain'
		if 'SERVER' not in headers_list:
			headers['Server'] = 'Unknown server'
		if 'CONNECTION' not in headers_list:
			headers['Connection'] = 'keep-alive'
		
		status_line = 'HTTP/1.1 {code} {msg}\n'.format(code=status_code,msg=status_msg)
		head_info = ''.join([ '%s: %s\n' % (x,y) for (x,y) in list(headers.items())])
		data = '\n\n'+text
		
		resp = status_line+head_info+data
		return resp
		
	def url_split(self,url):
		return [ x for x in url.split('/') if x != '']
		
		
		
		
		
		