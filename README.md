## About Homor

A light asynchronous web server.<br>Feature: <br>Especially easy to suspend request tasks.<br>Can print sitemap

**Update**

---

2018-6-12:new:

- SSL link avaliable

2018-6-11 

Code Refactored 

 - Separate worker pool
 - Separate URL Index
 - Delete a control layer
 - Make the code easier to be understand

Maybe next update:

- flex pack length
- static file
- configuration module

**Usage**

---

Start :arrow_down_small:

```python
# Python 3
# only need threading, time, datetime, socket, re
from Homer import Homer
Site = Homer()
```
Register a url :arrow_down_small:
>About user callback standered:<br>prefer the decorator like flask, <br>but cuz I didn't make the Global var routing<br>just take a easier way to pass the params
```python
Site = Request_handler()
@Site.register('/a/<b>/c',methods=['GET'])
def home(**kw):  # '**xxx' <-here we don't use global var, but need an entrance
	method = kw['method']	#Request method 	str
	args = kw['args']	#GET data	dict
	data = kw['data']	#POST data	dict
	req_headers = kw['request_headers']	#request headers	dict
	url_params = kw['url_params']	#Params bind like <p>	dict
	#... (working code)
	resp = {#headers, status_code, status_msg are not necessary
		'headers':{'User-Agent':'xxxxx',
					...					},
		'text':'xxxxxxxxxxxx'
		}
	return resp
```
- Example

```python
@Site.register('/test/<p1>/<p2>/aaa')
def home_page(**kw):
	method = kw['method']
	args = kw['args']
	data = kw['data']
	req_headers = kw['request_headers']
	url_params = kw['url_params']
	text = str(method)+'\n'+str(args)+'\n'+str(data)+'\n'+str(req_headers)+'\n'+str(url_params)
	return {'text':text}
```
​How async works? :arrow_down_small:

>Just open two pages at the same time<br>127.0.0.1:9000/hang/10/Hello<br>127.0.0.1:9000/hang/15/World

```python
import time
from threading import Thread
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
```
Other :arrow_down_small:

If a URL's callback wasn't registered, it'll automatically redirect it to /404

```python
@Site.register('/404')
def home_page(**kw):
	return {'text':'Just 404'}
	
if __name__ == '__main__':
	Site.run(host='127.0.0.1',port=9000)
```



**Suspend it up**

---

Each request will trigger an `Instant_task`.<br>But, u can take the socket acception out in a 'Message Waiting Queue'<br>Then retuen `None` to skip the rest of callback<br>

For example:
request for new msg from a friend

1. If you have it now, just return it.

2. If not, use `kw['get_sock']()` in callback so that this can free current worker. 
  When you got the new msg, put `{'sock':...,'headers':{...},'text':'...'}` 
  ('status_code' & 'status_msg' in resp are also avaliable)
  ```python
  saved_sockets = {}
  @Site.register('/test/<p1>/<p2>/aaa')
  def home_page(**kw):
      saved_sockets['ZIM7KASD22SD'] = kw['get_sock']() 
      return
  
  Site.put_resp(	
  		saved_sockets['ZIM7KASD22SD'],		#sock
  		{								#info
  		'headers': #not necessary
  			{
  				'Server':'Python'
  			},
  		'text':'Hello, world!'
  		}	
  	)
  ```
  Then it will be in queue and taken by a worker as a Response_task soon

**Something more**

---

- [ ] about favicon.ico
- [ ] about static files
- [ ] about free protocol feature (maybe not only a http server)
- [ ] about 404
- [ ] about redirect
- [x] about file stream
- [ ] why not split cookies?
- [ ] localproxy
- [ ] index page of files "http://aaaa/bbbb/"  -- index "http://aaa/bbb" -- page
- [x] ssl support
- [x] register api function, not wrapper
- [ ] Create web app from a CONF file
- [ ] More reliable worker pool
- [ ] service states
- [ ] debug mode （Debugger）
- [ ] exceptions
- [ ] log module
