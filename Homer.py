'''
About user callback standered:
I prefer the decorator like flask, 
but cuz this frame supports asynchronous service
there's something different

Site = Request_handler()
@Site.register('/a/<b>/c',methods=['GET'])
def home(**kw):  		# '**xxx' <-here we don't user global var, but need an entrance
	method = kw['method']				#Request method 		str
	args = kw['args']					#GET data 				dict
	data = kw['data']					#POST data				dict
	req_headers = kw['request_headers']	#request headers		dict
	url_params = kw['url_params']		#Params bind like <p>	dict
	...
	...
	resp = {								#headers, status_code, status_msg are not necessary
		'headers':{'User-Agent':'xxxxx',
					...					},
		'text':'xxxxxxxxxxxx'
		}
	return resp
'''

from main.Owner import Homer_owner

'''
Outer sys
may giving statistics
'''
class Homer(object):
	def __init__(self):
		print('Welcome to be with Homor!')
		self.Owner = Homer_owner()
		self.register = self.Owner.register
		self.put_resp = self.Owner.put_resp
		
	def run(self,host='127.0.0.1',port=8989):
		self.Owner.run(host,port)
		print("\nSite map:\n %s" % self.site_map())
		
	def site_map(self):
		return self.Owner.callback_index.tree()
		
	def info(self):
		pass
	
	
	
	
	