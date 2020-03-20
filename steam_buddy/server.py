import os
import subprocess
import tempfile
import json
import html
import yaml
import bcrypt
import requests
from bottle import app, route, template, static_file, redirect, abort, request, response
from beaker.middleware import SessionMiddleware
from steam_buddy.config import PLATFORMS, FLATHUB_HANDLER, SSH_KEY_HANDLER, AUTHENTICATOR, SETTINGS_HANDLER, STEAMGRID_HANDLER, FTP_SERVER, RESOURCE_DIR, BANNER_DIR, CONTENT_DIR, SHORTCUT_DIR, SESSION_OPTIONS
from steam_buddy.functions import load_shortcuts, sanitize, upsert_file, delete_file

server = SessionMiddleware(app(), SESSION_OPTIONS)

tmpfiles = {}

def authenticate(func):
    def wrapper(*args, **kwargs):
        authenticated = True
        session = request.environ.get('beaker.session')
        if not session.get('Logged-In') or not session['Logged-In']:
            authenticated = False
            session['Logged-In'] = False
            session.save()
        elif not session.get('User-Agent') or session['User-Agent'] != request.headers.get('User-Agent'):
            session.delete()
            authenticated = False
        if not authenticated:
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper


@route('/')
@authenticate
def root():
    return template('platforms.tpl', platforms=PLATFORMS)


@route('/platforms/<platform>')
@authenticate
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


@route('/banners/<platform>/<filename>')
@authenticate
def banners(platform, filename):
    base = "{banner_dir}/{platform}".format(banner_dir=BANNER_DIR, platform=platform)
    return static_file(filename, root='{base}'.format(base=base))


@route('/platforms/<platform>/new')
@authenticate
def new(platform):
    if platform == "flathub":
        return template('flathub', app_list=FLATHUB_HANDLER.get_available_applications(), isInstalledOverview=False,
                        isNew=True, platform=platform, platformName=PLATFORMS[platform])
    return template('new.tpl', isNew=True, isEditing=False, platform=platform, platformName=PLATFORMS[platform],
                    name='', hidden='')


@route('/platforms/<platform>/edit/<name>')
@authenticate
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


@route('/images/flathub/<filename>')
@authenticate
def flathub_images(filename):
    path = os.path.join(RESOURCE_DIR, 'images/flathub')
    local = os.path.join(BANNER_DIR, 'flathub')
    if os.path.isfile(os.path.join(local, filename)):
        path = local

    return static_file(filename, root=path)


@route('/images/<filename>')
def images(filename):
    return static_file(filename, root=os.path.join(RESOURCE_DIR, 'images'))


@route('/shortcuts/new', method='POST')
@authenticate
def shortcut_create():
    name = sanitize(request.forms.get('name'))
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    banner_url = request.forms.get('banner-url')
    banner = request.forms.get('banner')
    content = request.forms.get('content')

    if not name or name.strip() == '':
        redirect('/platforms/{platform}/new'.format(platform=platform))
        return

    name = name.strip()

    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    if len(matches) > 0:
        return 'Shortcut already exists'

    banner_path = None
    if banner:
        ( banner_src_path, banner_dst_name ) = tmpfiles[banner]
        del tmpfiles[banner]
        banner_path = upsert_file(banner_src_path, BANNER_DIR, platform, name, banner_dst_name)
    elif banner_url:
        banner_path = os.path.join(BANNER_DIR, platform, "{}.png".format(name))
        if not os.path.isdir(os.path.dirname(banner_path)):
            os.makedirs(os.path.dirname(banner_path))
        download = requests.get(banner_url)
        with open(banner_path, "wb") as banner_file:
            banner_file.write(download.content)

    if content:
        ( content_src_path, content_dst_name ) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path, CONTENT_DIR, platform, name, content_dst_name)

    shortcut = {}
    shortcut['name'] = name
    shortcut['cmd'] = platform
    shortcut['hidden'] = hidden == 'on'
    shortcut['tags'] = [PLATFORMS[platform]]
    if banner or banner_url:
        shortcut['banner'] = banner_path
    if content:
        shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
        shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    shortcuts.append(shortcut)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}'.format(platform=platform))


@route('/shortcuts/edit', method='POST')
@authenticate
def shortcut_update():
    name = sanitize(request.forms.get('original_name'))  # do not allow editing name
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    banner_url = request.forms.get('banner-url')
    banner = request.forms.get('banner')
    content = request.forms.get('content')

    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    shortcut = matches[0]

    banner_path = None
    if banner:
        ( banner_src_path, banner_dst_name ) = tmpfiles[banner]
        del tmpfiles[banner]
        banner_path = upsert_file(banner_src_path, BANNER_DIR, platform, name, banner_dst_name)
    elif banner_url:
        banner_path = os.path.join(BANNER_DIR, platform, "{}.png".format(name))
        if not os.path.isdir(os.path.dirname(banner_path)):
            os.makedirs(os.path.dirname(banner_path))
        download = requests.get(banner_url)
        with open(banner_path, "wb") as banner_file:
            banner_file.write(download.content)

    if content:
        ( content_src_path, content_dst_name ) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path, CONTENT_DIR, platform, name, content_dst_name)

    shortcut['name'] = name
    shortcut['cmd'] = platform
    shortcut['hidden'] = hidden == 'on'
    if banner or banner_url:
        shortcut['banner'] = banner_path
    if content:
        shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
        shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}'.format(platform=platform))


@route('/shortcuts/delete', method='POST')
@authenticate
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

@route('/shortcuts/file-upload', method='POST')
@authenticate
def start_file_upload():
    ( _, path ) = tempfile.mkstemp()
    key = os.path.basename(path)
    tmpfiles[key] = ( path, None )
    return key

@route('/shortcuts/file-upload', method='PATCH')
@authenticate
def upload_file_chunk():
    key = request.query.get('patch')
    path = tmpfiles[key][0]
    if not path:
        abort(400)

    tmpfiles[key] = ( path, request.headers.get('Upload-Name') )

    f = open(path, 'ab')
    f.seek(int(request.headers.get('Upload-Offset')))
    f.write(request.body.read())
    f.close()

@route('/shortcuts/file-upload', method='HEAD')
@authenticate
def check_file():
    return 0

@route('/shortcuts/file-upload', method='DELETE')
@authenticate
def delete_file():
    key = request.body.read().decode('utf8')
    path = tmpfiles[key][0]
    if not path:
        abort(400)

    del tmpfiles[key]
    os.remove(path)

@route('/flathub/install/<flatpak_id>')
@authenticate
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


@route('/flathub/uninstall/<flatpak_id>')
@authenticate
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


@route('/flathub/update/<flatpak_id>')
@authenticate
def flathub_update(flatpak_id):
    platform = "flathub"
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    if not application:
        abort(404, '{} not found in Flathub'.format(flatpak_id))
    application.update()

    redirect('/platforms/{platform}/edit/{name}'.format(platform=platform, name=flatpak_id))


@route('/flathub/progress/<flatpak_id>')
@authenticate
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


@route('/flathub/description/<flatpak_id>')
@authenticate
def flathub_description(flatpak_id):
    application = FLATHUB_HANDLER.get_application(flatpak_id)
    values = {
        "description": application.get_description()
    }
    return json.dumps(values)


@route('/settings')
@authenticate
def settings():
    current_settings = SETTINGS_HANDLER.get_settings()
    password_field = SETTINGS_HANDLER.get_setting('password')
    password_is_set = password_field and len(password_field) > 7
    ssh_key_ids = SSH_KEY_HANDLER.get_key_ids()
    hostname = request.environ.get('HTTP_HOST').split(":")[0] or request.environ.get('SERVER_NAME')
    username = os.getlogin()
    return template('settings.tpl', settings=current_settings, password_is_set=password_is_set, ssh_key_ids=ssh_key_ids, hostname=hostname, username=username)


@route('/settings/update', method='POST')
@authenticate
def settings_update():
    SETTINGS_HANDLER.set_setting("enable_ftp_server", sanitize(request.forms.get('enable_ftp_server')) == 'on')

    # Make sure the login password is long enough
    login_password = sanitize(request.forms.get('login_password'))
    if len(login_password) > 7:
        password = bcrypt.hashpw(login_password.encode('utf-8'), bcrypt.gensalt())
        SETTINGS_HANDLER.set_setting("password", password.decode('utf-8'))

    # Only allow enabling keep password if a password is set
    keep_password = sanitize(request.forms.get('generate_password')) != 'on'
    if keep_password and SETTINGS_HANDLER.get_setting('password') or not keep_password:
        SETTINGS_HANDLER.set_setting("keep_password", keep_password)

    # Make sure the FTP username is not set to empty
    ftp_username = sanitize(request.forms.get('ftp_username'))
    if ftp_username:
        SETTINGS_HANDLER.set_setting("ftp_username", ftp_username)

    # Make sure the FTP password is long enough
    ftp_password = sanitize(request.forms.get('ftp_password'))
    if len(ftp_password) > 7:
        SETTINGS_HANDLER.set_setting("ftp_password", ftp_password)

    # port number for FTP server
    ftp_port = int(sanitize(request.forms.get('ftp_port')))
    if ftp_port and 1024 < ftp_port < 65536 and ftp_port != 8844:
        SETTINGS_HANDLER.set_setting("ftp_port", ftp_port)

    # Delete SSH keys if asked
    ssh_key_ids = SSH_KEY_HANDLER.get_key_ids()
    for key_id in ssh_key_ids:
        if sanitize(request.forms.get(html.escape(key_id)) == 'on'):
            SSH_KEY_HANDLER.remove_key(key_id)

    # After we are done deleting the selected ssh keys, add a new key if specified
    # The add_key function makes sanitization not needed
    SSH_KEY_HANDLER.add_key(request.forms.get('ssh_key'))

    FTP_SERVER.reload()

    redirect('/settings')


@route('/steam/restart')
@authenticate
def steam_restart():
    try:
        subprocess.call(["pkill", "steamos-session"])
    finally:
        redirect('/')


@route('/steam/compositor')
@authenticate
def steam_compositor():
    try:
        subprocess.call(["toggle-steamos-compositor"])
    finally:
        redirect('/')


@route('/login')
def login():
    keep_password = SETTINGS_HANDLER.get_setting('keep_password')
    if not keep_password:
        AUTHENTICATOR.reset_password()
        AUTHENTICATOR.launch()
    return template('login', keep_password=keep_password, failed=False)


@route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session.delete()
    return template('logout')


@route('/authenticate', method='POST')
def authenticate():
    AUTHENTICATOR.kill()
    password = request.forms.get('password')
    session = request.environ.get('beaker.session')
    keep_password = SETTINGS_HANDLER.get_setting('keep_password') or False
    stored_hash = SETTINGS_HANDLER.get_setting('password')
    if AUTHENTICATOR.matches_password(password) or keep_password and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        session['User-Agent'] = request.headers.get('User-Agent')
        session['Logged-In'] = True
        session.save()
        redirect('/')
    else:
        if session.get('Logged-In', True):
            session['Logged-In'] = False
            session.save()
        if not keep_password:
            AUTHENTICATOR.reset_password()
            AUTHENTICATOR.launch()
        return template('login', keep_password=keep_password, failed=True)


@route('/forgotpassword')
def forgot_password():
    SETTINGS_HANDLER.set_setting('keep_password', False)
    return redirect('/login')


@route('/steamgrid/search/<search_string>')
def steamgrid_search(search_string):
    return STEAMGRID_HANDLER.search_games(search_string)


@route('/steamgrid/images/<game_id>')
def steamgrid_get_images(game_id):
    return STEAMGRID_HANDLER.get_images(game_id)
