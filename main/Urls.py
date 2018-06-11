from main.Index_for_url import Url_index
from base.http_parser import Http_parser
import re

class Url_handler(object):
	def __init__(self):
		self.callback_index = Url_index()
		self.Http_parser = Http_parser()	
		
	def site_map(self):
		return self.callback_index.tree()
		
	def Http_register(self,url,**kw): # Get register params
			pattern = re.compile(r'^<(.*)>$')
			splited_url = self.Http_parser.url_split(url)
			add_param_list = []
		
			for i in splited_url: # record params in url and switch it to '$'
				if pattern.match(i):
					add_param_list.append(i)
					splited_url[splited_url.index(i)] = '$'
	
			def callback_maker(user_callback): # Get user_func and make mixed func
				#'*args','**kw' are for get/post_data,headers,ip,<params> use
				def exposed_callback(*args,**kw):
					do_resp = [True]				#sign, use list so that can change by inner func
					param_list = add_param_list 	#only key
					add_params = kw['url_params'] 	#only value
					param_dict = dict()				#k & v
					for (k,v) in zip(param_list,add_params):
						k = pattern.findall(k)[0]
						param_dict[k] = v

					info_dict = dict(
						method = kw['method'],
						get_sock = kw['get_sock_outer'](do_resp), 
						request_headers = kw['headers'],
						args = kw['args'],
						data = kw['data'],
						url_params = param_dict
					)
					
					resp_info = user_callback(**info_dict)
					
					if resp_info == None:
						resp_info = dict()
					resp_info['do_resp'] = do_resp[0]
					return resp_info
		
				self.callback_index.register(splited_url,exposed_callback)
			return callback_maker
