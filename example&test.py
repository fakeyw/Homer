from Homer import Homer
import time
from threading import Thread

Site = Homer()

@Site.register('/test/<p1>/<p2>/aaa')
def home_page(**kw):
	method = kw['method']				#Request method 		str
	args = kw['args']					#GET data 				dict
	data = kw['data']					#POST data				dict
	req_headers = kw['request_headers']	#request headers		dict
	url_params = kw['url_params']		#Params bind like <p>	dict
	text = str(method)+'\n'+str(args)+'\n'+str(data)+'\n'+str(req_headers)+'\n'+str(url_params)
	return {'text':text}

@Site.register('/hang/<time>/<msg>')	
def hang(**kw):
	pause_time = kw['url_params']['time']
	want_msg = kw['url_params']['msg']
	sock = kw['get_sock']()
	def wait():
		time.sleep(int(pause_time))
		Site.put_resp(sock,{'text':want_msg})
	t = Thread(target=wait,name='wait')
	t.start()
	
@Site.register('/404')
def home_page(**kw):
	return {'text':'Just 404'}
	
if __name__ == '__main__':
	Site.run(host='127.0.0.1',port=9000)
