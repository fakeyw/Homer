from Homor import Request_handler

Site = Request_handler()

@Site.register('/')
def home_page(**kw):
	return {'text':'aa'}
	
@Site.register('/404')
def home_page(**kw):
	return {'text':'404'}
	
print(Site.site_map())