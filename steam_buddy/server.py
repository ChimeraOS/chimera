import os
import subprocess
import json
import yaml
from bottle import Bottle, template, static_file, redirect, abort, request, response
from steam_buddy.config import PLATFORMS, FLATHUB_HANDLER, RESOURCE_DIR, BANNER_DIR, CONTENT_DIR, SHORTCUT_DIR
from steam_buddy.functions import load_shortcuts, sanitize, upsert_file, delete_file

server = Bottle()


@server.route('/')
def root():
    return template('platforms.tpl', platforms=PLATFORMS)


@server.route('/platforms/<platform>')
def platform(platform):
    if platform == "flathub":
        return template('flathub', app_list=FLATHUB_HANDLER.get_installed_applications(), isInstalledOverview=True,
                        platform=platform, platformName=PLATFORMS[platform])
    shortcuts = sorted(load_shortcuts(platform), key=lambda s: s['name'])
    data = []
    for shortcut in shortcuts:
        filename = None
        banner = None
        hidden = 'hidden' if 'hidden' in shortcut and shortcut['hidden'] else ''
        if 'banner' in shortcut:
            filename = os.path.basename(shortcut['banner'])
            banner = '/banners/{platform}/{filename}'.format(platform=platform, name=shortcut['name'],
                                                             filename=filename)
        data.append({'hidden': hidden, 'filename': filename, 'banner': banner, 'name': shortcut['name']})

    return template('platform.tpl', shortcuts=data, platform=platform, platformName=PLATFORMS[platform])


@server.route('/banners/<platform>/<filename>')
def banners(platform, filename):
    base = "{banner_dir}/{platform}".format(banner_dir=BANNER_DIR, platform=platform)
    return static_file(filename, root='{base}'.format(base=base))


@server.route('/platforms/<platform>/new')
def new(platform):
    if platform == "flathub":
        return template('flathub', app_list=FLATHUB_HANDLER.get_available_applications(), isInstalledOverview=False,
                        isNew=True, platform=platform, platformName=PLATFORMS[platform])
    return template('new.tpl', isNew=True, isEditing=False, platform=platform, platformName=PLATFORMS[platform],
                    name='', hidden='')


@server.route('/platforms/<platform>/edit/<name>')
def edit(platform, name):
    if platform == "flathub":
        application = FLATHUB_HANDLER.get_application(name)
        if application:
            return template('flathub_edit', app=application, platform="flathub", platformName="Flathub",
                            name=name, )
        else:
            abort(404, '{} not found in Flathub'.format(name))
    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    shortcut = matches[0]

    return template('new.tpl', isEditing=True, platform=platform, platformName=PLATFORMS[platform], name=name,
                    hidden=shortcut['hidden'])


@server.route('/images/flathub/<filename>')
def flathub_images(filename):
    path = os.path.join(RESOURCE_DIR, 'images/flathub')
    local = os.path.join(BANNER_DIR, 'flathub')
    if os.path.isfile(os.path.join(local, filename)):
        path = local

    return static_file(filename, root=path)


@server.route('/images/<filename>')
def images(filename):
    return static_file(filename, root=os.path.join(RESOURCE_DIR, 'images'))


@server.route('/shortcuts/new', method='POST')
def shortcut_create():
    name = sanitize(request.forms.get('name'))
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    banner = request.files.get('banner')
    content = request.files.get('content')

    if not name or name.strip() == '':
        redirect('/platforms/{platform}/new'.format(platform=platform))
        return

    name = name.strip()

    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    if len(matches) > 0:
        return 'Shortcut already exists'

    banner_path = upsert_file(BANNER_DIR, platform, name, banner)
    content_path = upsert_file(CONTENT_DIR, platform, name, content)

    shortcut = {}
    shortcut['name'] = name
    shortcut['cmd'] = platform
    shortcut['hidden'] = hidden == 'on'
    shortcut['tags'] = [PLATFORMS[platform]]
    if banner:
        shortcut['banner'] = banner_path
    if content:
        shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
        shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    shortcuts.append(shortcut)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}'.format(platform=platform))


@server.route('/shortcuts/edit', method='POST')
def shortcut_update():
    name = sanitize(request.forms.get('original_name'))  # do not allow editing name
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    banner = request.files.get('banner')
    content = request.files.get('content')

    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    shortcut = matches[0]

    banner_path = upsert_file(BANNER_DIR, platform, name, banner)
    content_path = upsert_file(CONTENT_DIR, platform, name, content)

    shortcut['name'] = name
    shortcut['cmd'] = platform
    shortcut['hidden'] = hidden == 'on'
    if banner:
        shortcut['banner'] = banner_path
    if content:
        shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
        shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}'.format(platform=platform))


@server.route('/shortcuts/delete', method='POST')
def shortcut_delete():
    name = sanitize(request.forms.get('name'))
    platform = sanitize(request.forms.get('platform'))

    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    shortcut = matches[0]

    delete_file(CONTENT_DIR, platform, name)
    delete_file(BANNER_DIR, platform, name)

    shortcuts.remove(shortcut)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}'.format(platform=platform))


@server.route('/flathub/install/<flatpak_id>')
def flathub_install(flatpak_id):
    platform = "flathub"
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    if not application:
        abort(404, '{} not found in Flathub'.format(flatpak_id))
    application.install()

    shortcuts = load_shortcuts(platform)
    shortcut = {
        'name': application.name,
        'hidden': False,
        'banner': application.get_image(os.path.join(BANNER_DIR, platform)),
        'params': application.flatpak_id,
        'cmd': "flatpak run",
        'tags': ["Flathub"],
    }
    shortcuts.append(shortcut)
    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}/edit/{name}'.format(platform=platform, name=flatpak_id))


@server.route('/flathub/uninstall/<flatpak_id>')
def flathub_uninstall(flatpak_id):
    platform = "flathub"
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    if not application:
        abort(404, '{} not found in Flathub'.format(flatpak_id))
    application.uninstall()

    shortcuts = load_shortcuts(platform)
    for shortcut in shortcuts:
        if application.name == shortcut['name']:
            shortcuts.remove(shortcut)
            break
    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}/edit/{name}'.format(platform=platform, name=flatpak_id))


@server.route('/flathub/update/<flatpak_id>')
def flathub_update(flatpak_id):
    platform = "flathub"
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    if not application:
        abort(404, '{} not found in Flathub'.format(flatpak_id))
    application.update()

    redirect('/platforms/{platform}/edit/{name}'.format(platform=platform, name=flatpak_id))


@server.route('/flathub/progress/<flatpak_id>')
def flathub_progress(flatpak_id):
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    if not application:
        abort(404, '{} not found in Flathub'.format(flatpak_id))

    response.content_type = 'application/json'
    values = {
        "busy": application.busy,
        "progress": application.progress
    }

    return json.dumps(values)


@server.route('/flathub/description/<flatpak_id>')
def flathub_description(flatpak_id):
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    values = {
        "description": application.get_description()
    }
    return json.dumps(values)


@server.route('/steam/restart')
def steam_restart():
    subprocess.call(["pkill", "steam"])
    redirect('/')


@server.route('/steam/compositor')
def steam_compositor():
    subprocess.call(["toggle-steamos-compositor"])
    redirect('/')
