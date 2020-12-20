import os
import pwd
import subprocess
import tempfile
import json
import html
import yaml
import bcrypt
import requests
import shutil
from bottle import app, route, template, static_file, redirect, abort, request, response
from beaker.middleware import SessionMiddleware
from steam_buddy.config import PLATFORMS, SSH_KEY_HANDLER, AUTHENTICATOR, SETTINGS_HANDLER, STEAMGRID_HANDLER, FTP_SERVER, RESOURCE_DIR, BANNER_DIR, CONTENT_DIR, SHORTCUT_DIR, SESSION_OPTIONS
from steam_buddy.functions import load_shortcuts, sanitize, upsert_file, delete_file, generate_banner
from steam_buddy.auth_decorator import authenticate
from steam_buddy.platforms.epic_store import EpicStore
from steam_buddy.platforms.flathub import Flathub
from steam_buddy.platforms.gog import GOG

server = SessionMiddleware(app(), SESSION_OPTIONS)

tmpfiles = {}


PLATFORM_HANDLERS = {
    "epic-store": EpicStore(),
    "flathub": Flathub(),
    "gog": GOG(),
}


def authenticate_platform(selected_platform):
    if selected_platform in PLATFORM_HANDLERS:
        if not PLATFORM_HANDLERS[selected_platform].is_authenticated():
            redirect('/platforms/{platform}'.format(platform=selected_platform))
            return False
    return True


@route('/')
@authenticate
def root():
    return template('platforms.tpl', platforms=PLATFORMS, audio=get_audio())


@route('/platforms/<platform>')
@authenticate
def platform_page(platform):
    if platform in PLATFORM_HANDLERS:
        if PLATFORM_HANDLERS[platform].is_authenticated():
            return template(
                'custom',
                app_list=PLATFORM_HANDLERS[platform].get_installed_content(),
                isInstalledOverview=True,
                platform=platform,
                platformName=PLATFORMS[platform]
            )
        else:
            return template('custom_login', platform=platform, platformName=PLATFORMS[platform])

    shortcuts = sorted(load_shortcuts(platform), key=lambda s: s['name'])
    data = []
    for shortcut in shortcuts:
        filename = None
        banner = None
        hidden = 'hidden' if 'hidden' in shortcut and shortcut['hidden'] else ''
        if 'banner' in shortcut:
            filename = os.path.basename(shortcut['banner'])
            banner = '/banners/{platform}/{filename}'.format(platform=platform, filename=filename)
        data.append({'hidden': hidden, 'filename': filename, 'banner': banner, 'name': shortcut['name']})

    return template(
        'platform.tpl', shortcuts=data, platform=platform, platformName=PLATFORMS[platform]
    )


@route('/platforms/<platform>/authenticate', method='POST')
@authenticate
def platform_authenticate(platform):
    if platform not in PLATFORM_HANDLERS:
        return

    password = request.forms.get('password')
    PLATFORM_HANDLERS[platform].authenticate(password)
    redirect('/platforms/{platform}'.format(platform=platform))


@route('/banners/<platform>/<filename>')
@authenticate
def banners(platform, filename):
    base = "{banner_dir}/{platform}".format(banner_dir=BANNER_DIR, platform=platform)
    return static_file(filename, root='{base}'.format(base=base))


@route('/platforms/<platform>/new')
@authenticate
def new(platform):
    if platform in PLATFORM_HANDLERS:
        if not authenticate_platform(platform):
            return

        return template(
            'custom', app_list=PLATFORM_HANDLERS[platform].get_available_content(), isInstalledOverview=False,
            isNew=True, platform=platform, platformName=PLATFORMS[platform]
        )
    return template(
        'new.tpl', isNew=True, isEditing=False, platform=platform,
        platformName=PLATFORMS[platform], name='', hidden=''
    )


@route('/platforms/<platform>/edit/<name>')
@authenticate
def edit(platform, name):
    if platform in PLATFORM_HANDLERS:
        if not authenticate_platform(platform):
            return

        content_id = name
        content = PLATFORM_HANDLERS[platform].get_content(content_id)
        if content:
            return template(
                'custom_edit', app=content, platform=platform,
                platformName=PLATFORMS[platform], name=content_id
            )
        else:
            abort(404, 'Content not found')

    shortcuts = load_shortcuts(platform)

    matches = [e for e in shortcuts if e['name'] == name and e['cmd'] == platform]
    shortcut = matches[0]

    return template('new.tpl', isEditing=True, platform=platform, platformName=PLATFORMS[platform],
                    name=name, hidden=shortcut['hidden'])


@route('/images/flathub/<content_id>')
@authenticate
def flathub_images(content_id):
    path = PLATFORM_HANDLERS['flathub'].get_image_file_base_dir(content_id)
    return static_file(content_id + '.png', root=path)


@route('/images/<filename>')
def images(filename):
    return static_file(filename, root=os.path.join(RESOURCE_DIR, 'images'))


@route('/public/<filename>')
def public(filename):
    return static_file(filename, root='public')


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
        (banner_src_path, banner_dst_name) = tmpfiles[banner]
        del tmpfiles[banner]
        banner_path = upsert_file(banner_src_path, BANNER_DIR, platform, name, banner_dst_name)
    else:
        banner_path = os.path.join(BANNER_DIR, platform, "{}.png".format(name))
        if not os.path.isdir(os.path.dirname(banner_path)):
            os.makedirs(os.path.dirname(banner_path))
        if banner_url:
            download = requests.get(banner_url)
            with open(banner_path, "wb") as banner_file:
                banner_file.write(download.content)
        else:
            generate_banner(name, banner_path)

    shortcut = {
        'name': name, 'cmd': platform, 'hidden': hidden == 'on', 'banner': banner_path, 'tags': [PLATFORMS[platform]]
    }

    if content:
        (content_src_path, content_dst_name) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path, CONTENT_DIR, platform, name, content_dst_name)
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
        (banner_src_path, banner_dst_name) = tmpfiles[banner]
        del tmpfiles[banner]
        banner_path = upsert_file(banner_src_path, BANNER_DIR, platform, name, banner_dst_name)
    elif banner_url:
        banner_path = os.path.join(BANNER_DIR, platform, "{}.png".format(name))
        if not os.path.isdir(os.path.dirname(banner_path)):
            os.makedirs(os.path.dirname(banner_path))
        download = requests.get(banner_url)
        with open(banner_path, "wb") as banner_file:
            banner_file.write(download.content)

    shortcut['name'] = name
    shortcut['cmd'] = platform
    shortcut['hidden'] = hidden == 'on'
    if banner or banner_url:
        shortcut['banner'] = banner_path
    if content:
        (content_src_path, content_dst_name) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path, CONTENT_DIR, platform, name, content_dst_name)
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
    file_name = None
    file_data = request.files.get('banner') or request.files.get('content')

    if file_data:
        file_name = sanitize(file_data.filename)

    (_, path) = tempfile.mkstemp()
    key = os.path.basename(path)
    tmpfiles[key] = (path, file_name)

    if file_data:
        file_data.save(path, True)

    return key


@route('/shortcuts/file-upload', method='PATCH')
@authenticate
def upload_file_chunk():
    key = request.query.get('patch')
    path = tmpfiles[key][0]
    if not path:
        abort(400)

    tmpfiles[key] = (path, sanitize(request.headers.get('Upload-Name')))

    f = open(path, 'ab')
    f.seek(int(request.headers.get('Upload-Offset')))
    f.write(request.body.read())
    f.close()


@route('/shortcuts/file-upload', method='HEAD')
@authenticate
def check_file_upload():
    return 0


@route('/shortcuts/file-upload', method='DELETE')
@authenticate
def delete_file_upload():
    key = request.body.read().decode('utf8')
    path = tmpfiles[key][0]
    if not path:
        abort(400)

    del tmpfiles[key]
    os.remove(path)


@route('/<platform>/install/<content_id>')
@authenticate
def platform_install(platform, content_id):
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, 'Content not found')

    PLATFORM_HANDLERS[platform].install_content(content)

    shortcuts = load_shortcuts(platform)
    shortcut = PLATFORM_HANDLERS[platform].get_shortcut(content)

    shortcuts.append(shortcut)
    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}/edit/{content_id}'.format(platform=platform, content_id=content_id))


@route('/<platform>/uninstall/<content_id>')
@authenticate
def uninstall(platform, content_id):
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, 'Content not found')
    PLATFORM_HANDLERS[platform].uninstall_content(content_id)

    shortcuts = load_shortcuts(platform)
    for shortcut in shortcuts:
        if content.name == shortcut['name']:
            shortcuts.remove(shortcut)
            break
    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    yaml.dump(shortcuts, open(shortcuts_file, 'w'), default_flow_style=False)

    redirect('/platforms/{platform}/edit/{name}'.format(platform=platform, name=content_id))


@route('/<platform>/update/<content_id>')
@authenticate
def content_update(platform, content_id):
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, 'Content not found')
    PLATFORM_HANDLERS[platform].update_content(content_id)

    redirect('/platforms/{platform}/edit/{name}'.format(platform=platform, name=content_id))


@route('/<platform>/progress/<content_id>')
@authenticate
def install_progress(platform, content_id):
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, '{} not found'.format(content_id))

    response.content_type = 'application/json'
    values = {
        "operation": content.operation,
        "progress": content.progress,
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
    username = pwd.getpwuid(os.getuid())[0]
    return template('settings.tpl', settings=current_settings, password_is_set=password_is_set,
                    ssh_key_ids=ssh_key_ids, hostname=hostname, username=username)


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
        subprocess.call(["bin/toggle-steamos-compositor"])
    finally:
        redirect('/')


@route('/steam/overlay')
@authenticate
def steam_overlay():
    try:
        subprocess.call(["xdotool", "key", "shift+Tab"])
    finally:
        redirect('/')


@route('/mangohud')
@authenticate
def mangohud():
    try:
        subprocess.call(["xdotool", "key", "F3"])
    finally:
        redirect('/')


@route('/virtual_keyboard')
@authenticate
def virtual_keyboard():
    return template('virtual_keyboard.tpl')


@route('/virtual_keyboard/string', method='POST')
@authenticate
def virtual_keyboard_string():
    string = sanitize(request.forms.get('str'))
    try:
        subprocess.call(["xdotool", "type", "--", string])
    finally:
        redirect('/virtual_keyboard')


@route('/exit_game')
@authenticate
def exit_game():
    try:
        subprocess.call(["bin/exit-game"])
    finally:
        redirect('/')


def get_audio():
    if not shutil.which('ponymix'):
        return None

    try:
        raw = subprocess.check_output(["ponymix", "list-profiles"])
        entries = raw.decode('utf8').split('\n')

        volume = subprocess.check_output(["ponymix", "get-volume"])
        volume = volume.decode('utf8')

        muted = subprocess.call(["ponymix", "is-muted"])
        print(muted)

        active = None
        grouped = []
        for i in range(0, len(entries), 2):
            if '[active]' in entries[i]:
                active = entries[i].replace(' [active]', '')
                grouped.append((active, entries[i+1].strip()))
            elif entries[i]:
                grouped.append((entries[i], entries[i+1].strip()))

        results = [e for e in grouped if 'input' not in e[0] and e[0] != 'off']

        return {
            'active': active,
            'options': results,
            'volume': volume,
            'muted': muted != 0
        }
    except:
        return None


@route('/audio/toggle_mute')
@authenticate
def toggle_mute():
    try:
        subprocess.call(["ponymix", "toggle"])
    finally:
        redirect('/')


@route('/audio/volume_up')
@authenticate
def volume_up():
    try:
        subprocess.call(["ponymix", "increase", "10"])
    finally:
        redirect('/')


@route('/audio/volume_down')
@authenticate
def volume_down():
    try:
        subprocess.call(["ponymix", "decrease", "10"])
    finally:
        redirect('/')


@route('/audio/<profile>')
@authenticate
def audio(profile):
    try:
        subprocess.call(["ponymix", "set-profile", profile])
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
def authenticate_route_handler():
    AUTHENTICATOR.kill()
    password = request.forms.get('password')
    session = request.environ.get('beaker.session')
    keep_password = SETTINGS_HANDLER.get_setting('keep_password') or False
    stored_hash = SETTINGS_HANDLER.get_setting('password')
    if AUTHENTICATOR.matches_password(password.upper()) or keep_password and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
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
