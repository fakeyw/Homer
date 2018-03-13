from Homor import Request_handler

Site = Request_handler()

@Site.register('/test/<p>/aaa')
def home_page(**kw):
	method = kw['method']				#Request method 		str
	args = kw['args']					#GET data 				dict
	data = kw['data']					#POST data				dict
	req_headers = kw['request_headers']	#request headers		dict
	url_params = kw['url_params']		#Params bind like <p>	dict
	text = str(method)+'\n'+str(args)+'\n'+str(data)+'\n'+str(req_headers)+'\n'+str(url_params)

	return {'text':text}
	
@Site.register('/404')
def home_page(**kw):
	return {'text':'404'}
	
print(Site.site_map())