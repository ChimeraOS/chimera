import os
from bottle import route, request, static_file, run

@route('/')
def root():
	return static_file('shortcuts.html', root='.')

@route('/shortcuts', method='POST')
def do_upload():
	name = request.forms.get('name')
	platform = request.forms.get('platform')
	hidden = request.forms.get('hidden')
	banner = request.files.get('banner')
	content = request.files.get('content')

	print(platform)
	
	if banner:
		dir_path = "/tmp/banners/{platform}".format(platform=platform)
		os.makedirs(dir_path)
		banner.save("{dir_path}/{filename}".format(dir_path=dir_path, filename=banner.filename))
	
	if content:
		dir_path = "/tmp/content/{platform}".format(platform=platform)
		os.makedirs(dir_path)
		content.save("{dir_path}/{filename}".format(dir_path=dir_path, filename=content.filename))
	
	return 'Shortcut added'

if __name__ == '__main__':
	run(host='localhost', port=8080)
