import os
import yaml
from bottle import route, request, static_file, run

BASE_DIR='/home/alesh/.local/share'
DATA_DIR=BASE_DIR + '/prom'

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

	shortcuts = []
	shortcuts_dir = "{data_dir}/steam-shortcuts".format(data_dir=BASE_DIR)
	if not os.path.exists(shortcuts_dir):
		os.makedirs(shortcuts_dir)
	shortcuts_file = "{shortcuts_dir}/prom.{platform}.yaml".format(shortcuts_dir=shortcuts_dir, platform=platform)
	if os.path.isfile(shortcuts_file):
		shortcuts = yaml.load(open(shortcuts_file), Loader=yaml.FullLoader)

	if not shortcuts:
		shortcuts = []

	matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
	if len(matches) > 0:
		return 'Shortcut already exists'
	
	if banner:
		dir_path = "{data_dir}/banners/{platform}".format(data_dir=DATA_DIR, platform=platform)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
		banner_path = "{dir_path}/{filename}".format(dir_path=dir_path, filename=banner.filename)
		if os.path.exists(banner_path):
			os.remove(banner_path)
		banner.save(banner_path)
	
	if content:
		dir_path = "{data_dir}/content/{platform}".format(data_dir=DATA_DIR, platform=platform)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
		content_path = "{dir_path}/{filename}".format(dir_path=dir_path, filename=content.filename)
		if os.path.exists(content_path):
			os.remove(content_path)
		content.save(content_path)


	saves_dir = "{data_dir}/saves/{platform}".format(data_dir=DATA_DIR, platform=platform)
	if not os.path.exists(saves_dir):
		os.makedirs(saves_dir)



	shortcut = {}
	shortcut['name'] = name
	shortcut['cmd'] = platform
	shortcut['hidden'] = hidden == 'on'
	shortcut['dir'] = "{data_dir}/saves/{platform}".format(data_dir=DATA_DIR, platform=platform)
	if banner:
		shortcut['image'] = banner_path
	if content:
		shortcut['params'] = content_path

	shortcuts.append(shortcut)
	yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)	

	return 'Shortcut added'

if __name__ == '__main__':
	run(host='localhost', port=8080)
