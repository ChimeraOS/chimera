import os
import yaml
from bottle import route, request, static_file, run, template, redirect

BASE_DIR='/home/alesh/.local/share'
DATA_DIR=BASE_DIR + '/prom'


def load_shortcuts(platform):
	shortcuts = []
	shortcuts_dir = "{data_dir}/steam-shortcuts".format(data_dir=BASE_DIR)
	if not os.path.exists(shortcuts_dir):
		os.makedirs(shortcuts_dir)
	shortcuts_file = "{shortcuts_dir}/prom.{platform}.yaml".format(shortcuts_dir=shortcuts_dir, platform=platform)
	if os.path.isfile(shortcuts_file):
		shortcuts = yaml.load(open(shortcuts_file), Loader=yaml.FullLoader)

	if not shortcuts:
		shortcuts = []

	return shortcuts

@route('/')
def root():
	return '''
		<style>img { padding : 10px }</style>
		<a href="/platforms/nes"><img src="art/nes.png" alt="Nintendo"></img></a>
		<a href="/platforms/snes"><img src="art/snes.png" alt="Super Nintendo"></img></a>
		<a href="/platforms/genesis"><img src="art/genesis.png" alt="Sega Genesis"></img></a>
	'''

@route('/platforms/<platform>')
def platform(platform):
	shortcuts = load_shortcuts(platform)
	output = '<style>img { padding : 10px }</style>'
	output += '<p><a href="/">Platforms</a>  <a href="/platforms/{platform}/new">Add</a></p>'.format(platform=platform)
	for shortcut in shortcuts:
		filename = os.path.basename(shortcut['image'])
		image = '/banners/{platform}/{filename}'.format(platform=platform, filename=filename)
		output += '<img src="{image}" alt="{name}" title="{name}" width="460" height="215"></img>'.format(image=image, name=shortcut['name'])

	return output

@route('/banners/<platform>/<filename>')
def banners(platform, filename):
	base = "{data_dir}/banners/{platform}".format(data_dir=DATA_DIR, platform=platform)
	return static_file(filename, root='{base}'.format(base=base))

@route('/platforms/<platform>/new')
def new(platform):
	return template('new.tpl', platform=platform)
	#return static_file('shortcuts.html', root='.')

@route('/art/<filename>')
def art(filename):
	return static_file('art/' + filename, root='.')

@route('/shortcuts', method='POST')
def shortcuts():
	name = request.forms.get('name')
	platform = request.forms.get('platform')
	hidden = request.forms.get('hidden')
	banner = request.files.get('banner')
	content = request.files.get('content')

	shortcuts_dir = "{data_dir}/steam-shortcuts".format(data_dir=BASE_DIR)
	shortcuts_file = "{shortcuts_dir}/prom.{platform}.yaml".format(shortcuts_dir=shortcuts_dir, platform=platform)
	shortcuts = load_shortcuts(platform)

	matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
	if len(matches) > 0:
		return 'Shortcut already exists'
	
	if banner:
		_, ext = os.path.splitext(banner.filename)
		dir_path = "{data_dir}/banners/{platform}".format(data_dir=DATA_DIR, platform=platform)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
		banner_path = "{dir_path}/{filename}{ext}".format(dir_path=dir_path, filename=name, ext=ext)
		if os.path.exists(banner_path):
			os.remove(banner_path)
		banner.save(banner_path)
	
	if content:
		_, ext = os.path.splitext(content.filename)
		dir_path = "{data_dir}/content/{platform}".format(data_dir=DATA_DIR, platform=platform)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
		content_path = "{dir_path}/{filename}{ext}".format(dir_path=dir_path, filename=name, ext=ext)
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

	#return 'Shortcut added'
	redirect('/platforms/{platform}'.format(platform=platform))

if __name__ == '__main__':
	#run(host='0.0.0.0', port=8080)
	run(host='localhost', port=8080)
