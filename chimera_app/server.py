# type: ignore

import os
import sys
import pwd
import subprocess
import socket
import tempfile
import json
import html
import bcrypt
import requests
import shutil
import unicodedata
import string
import secrets
import threading
from urllib.parse import quote
from urllib.parse import unquote
from bottle import abort
from bottle import app
from bottle import redirect
from bottle import request
from bottle import response
from bottle import route
from bottle import template
from bottle import static_file
from beaker.middleware import SessionMiddleware
from chimera_app.config import PLATFORMS
from chimera_app.config import SSH_KEY_HANDLER
from chimera_app.config import AUTHENTICATOR
from chimera_app.config import SETTINGS_HANDLER
from chimera_app.config import STEAMGRID_HANDLER
from chimera_app.config import FTP_SERVER
from chimera_app.config import RESOURCE_DIR
from chimera_app.config import BANNER_DIR
from chimera_app.config import CONTENT_DIR
from chimera_app.config import UPLOADS_DIR
from chimera_app.config import SESSION_OPTIONS
from chimera_app.config import STORAGE_HANDLER
from chimera_app.compat_tools import OFFICIAL_COMPAT_TOOLS
from chimera_app.compat_tools import OfficialCompatTool
from chimera_app.utils import sanitize
from chimera_app.utils import upsert_file
from chimera_app.utils import delete_file
from chimera_app.utils import is_direct
from chimera_app.file_utils import ensure_directory_for_file
from chimera_app.auth_decorator import authenticate
from chimera_app.platforms.epic_store import EpicStore
from chimera_app.platforms.flathub import Flathub
from chimera_app.platforms.gog import GOG
from chimera_app.platforms.chimera_remote import ChimeraRemote
from chimera_app.shortcuts import PlatformShortcutsFile
from chimera_app.shortcuts import get_bpmbanner_id
import chimera_app.power as power


server = SessionMiddleware(app(), SESSION_OPTIONS)


tmpfiles = {}

storage_operation_type = None
storage_operation_device = None
storage_operation_status = None
storage_operation_log = None


PLATFORM_HANDLERS = {
    "epic-store": EpicStore(),
    "flathub": Flathub(),
    "gog": GOG(),
}

REMOTE_HANDLERS = {}


def refresh_local_password():
    password = ''.join((secrets.choice(string.ascii_letters + string.digits) for i in range(100)))
    f = open('/tmp/chimera-local-password', 'w')
    f.write(password)
    return password

LOCAL_PASSWORD = refresh_local_password()

def authenticate_platform(selected_platform):
    if selected_platform in PLATFORM_HANDLERS:
        if not PLATFORM_HANDLERS[selected_platform].is_authenticated():
            redirect(f'/library/{selected_platform}')
            return False
    return True


@route('/')
@authenticate
def root():
    redirect('/library')

@route('/actions')
@authenticate
def actions():
    return template('actions.tpl', audio=get_audio(), tdp=power.get_tdp(), bare=True)

@route('/emulators')
@authenticate
def emulators():
    return template('emulators.tpl', bare=True)

@route('/library')
@authenticate
def platforms():
    return template('platforms.tpl', platforms=PLATFORMS)


@route('/library/<platform>')
@authenticate
def platform_page(platform):
    if platform in PLATFORM_HANDLERS:
        if PLATFORM_HANDLERS[platform].is_authenticated():
            return template(
                'custom',
                app_list=PLATFORM_HANDLERS[platform].get_installed_content(),
                showAll=False,
                isInstalledOverview=True,
                platform=platform,
                platformName=PLATFORMS[platform]['name'],
                remote=False,
            )
        else:
            return template('custom_login',
                            platform=platform,
                            platformName=PLATFORMS[platform]['name'])

    shortcut_file = PlatformShortcutsFile(platform)
    shortcuts = sorted(shortcut_file.get_shortcuts_data(),
                       key=lambda s: s['name'])
    data = []
    for shortcut in shortcuts:
        filename = None
        banner = None
        hidden = ('hidden'
                  if 'hidden' in shortcut and shortcut['hidden']
                  else '')
        if 'banner' in shortcut:
            filename = os.path.basename(shortcut['banner'])
            banner = f'/images/banner/{platform}/{filename}'
        if 'deleted' not in shortcut or shortcut['deleted'] != True:
            data.append({'hidden': hidden,
                         'filename': filename,
                         'banner': banner,
                         'name': shortcut['name']})

    return template('platform.tpl',
                    shortcuts=data,
                    platform=platform,
                    platformName=PLATFORMS[platform]['name'],
                    remoteConnected=bool(REMOTE_HANDLERS))


@route('/library/<platform>/authenticate', method='POST')
@authenticate
def platform_authenticate(platform):
    if platform not in PLATFORM_HANDLERS:
        return

    password = request.forms.get('password')
    if not password:
        redirect(f'/library/{platform}')

    PLATFORM_HANDLERS[platform].authenticate(password)
    redirect(f'/library/{platform}')


@route('/images/banner/<platform>/<filename>')
@authenticate
def banners(platform, filename):
    base = f'{BANNER_DIR}/banner/{platform}'
    return static_file(filename, root='{base}'.format(base=base))


@route('/library/<platform>/new')
@authenticate
def new(platform):
    handler = None
    showAll = False
    remote = False
    if platform in PLATFORM_HANDLERS:
        handler = PLATFORM_HANDLERS[platform]
        showAll = request.query.showAll
    elif request.query.remote == 'true':
        handler = REMOTE_HANDLERS[platform]
        showAll = True
        remote = True

    if handler:
        if not authenticate_platform(platform):
            return

        try:
            app_list = handler.get_available_content(showAll)
        except Exception as err:
            print(err)
            if remote:
                return '<p>Remote server was disconnected and cannot be found</p>'
            else:
                return '<p>Failed to get list of available content</p>'

        return template(
            'custom',
            app_list=app_list,
            showAll=showAll,
            isInstalledOverview=False,
            isNew=True,
            platform=platform,
            platformName=PLATFORMS[platform]['name'],
            remote=remote,
        )
    return template('new.tpl',
                    isNew=True,
                    isEditing=False,
                    platform=platform,
                    platformName=PLATFORMS[platform]['name'],
                    name='',
                    hidden='',
                    steamShortcutID=None
                    )


@route('/library/<platform>/edit/<name>')
@authenticate
def edit(platform, name):
    remoteLaunchEnabled = SETTINGS_HANDLER.get_setting('enable_remote_launch')

    handler = None
    remote = False
    if platform in PLATFORM_HANDLERS:
        handler = PLATFORM_HANDLERS[platform]
    elif request.query.remote == 'true':
        handler = REMOTE_HANDLERS[platform]
        remote = True

    if handler:
        if not authenticate_platform(platform):
            return

        content_id = name
        content = handler.get_content(content_id)
        shortcut = handler.get_shortcut(content)
        if content:
            return template(
                'custom_edit',
                app=content,
                platform=platform,
                platformName=PLATFORMS[platform]['name'],
                name=content_id,
                steamShortcutID=(get_bpmbanner_id(shortcut['cmd'], shortcut['name']) if remoteLaunchEnabled else None),
                remote=remote,
            )
        else:
            abort(404, 'Content not found')

    shortcuts = PlatformShortcutsFile(platform)
    shortcut = shortcuts.get_shortcut_match(name)

    return template('new.tpl',
                    isEditing=True,
                    platform=platform,
                    platformName=PLATFORMS[platform]['name'],
                    name=name,
                    hidden=shortcut['hidden'],
                    steamShortcutID=(get_bpmbanner_id(platform, name) if remoteLaunchEnabled else None),
                    )


@route('/images/flathub/<content_id>')
@authenticate
def flathub_images(content_id):
    path = PLATFORM_HANDLERS['flathub'].get_image_file_base_dir(content_id)
    return static_file(content_id + '.png', root=path)


@route('/images/<filename>')
def images(filename):
    if os.path.isfile(os.path.join(RESOURCE_DIR, 'images', filename)):
        return static_file(filename, root=os.path.join(RESOURCE_DIR, 'images'))
    else:
        return static_file(filename, root=os.path.join(BANNER_DIR, 'banner'))

@route('/public/<filename>')
def public(filename):
    return static_file(filename, root='public')


def get_ext(url):
    url_noquery = url.split('?')[0]
    ext = os.path.splitext(url_noquery)[1]

    if not ext:
        ext = '.png'

    return ext

@route('/shortcuts/new', method='POST')
@authenticate
def shortcut_create():
    image_urls = {}
    image_paths = {}
    name = sanitize(request.forms.get('name'))
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    image_urls['banner'] = request.forms.get('image-url-banner')
    image_urls['poster'] = request.forms.get('image-url-poster')
    image_urls['background'] = request.forms.get('image-url-background')
    image_urls['logo'] = request.forms.get('image-url-logo')
    image_urls['icon'] = request.forms.get('image-url-icon')
    content = request.forms.get('content')

    if not name or name.strip() == '':
        redirect(f'/library/{platform}/new')
        return

    name = name.strip()

    shortcuts = PlatformShortcutsFile(platform)

    existing_shortcut = shortcuts.get_shortcut_match(name)
    is_existing_shortcut_marked_deleted = 'deleted' in existing_shortcut and existing_shortcut['deleted'] == True
    if existing_shortcut and not is_existing_shortcut_marked_deleted:
        return 'Shortcut already exists'

    for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
        if not image_urls[img_type]:
            continue
        ext = get_ext(image_urls[img_type])
        image_paths[img_type] = os.path.join(BANNER_DIR, img_type, platform, f"{name}{ext}")
        ensure_directory_for_file(image_paths[img_type])
        download = requests.get(image_urls[img_type], timeout=20)
        with open(image_paths[img_type], "wb") as image_file:
            image_file.write(download.content)

    shortcut = {
        'name': name,
        'cmd': PLATFORMS[platform]['cmd'],
        'hidden': hidden == 'on',
        'tags': [PLATFORMS[platform]['name']]
    }

    for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
        if img_type in image_paths:
            shortcut[img_type] = image_paths[img_type]

    if content:
        (content_src_path, content_dst_name) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path,
                                   CONTENT_DIR,
                                   platform,
                                   name,
                                   content_dst_name)
        if content_path:
            shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
            shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    shortcuts.add_shortcut(shortcut)
    shortcuts.save()

    redirect(f'/library/{platform}')


@route('/shortcuts/edit', method='POST')
@authenticate
def shortcut_update():
    image_urls = {}
    image_paths = {}
    name = sanitize(request.forms.get('original_name')) # do not allow editing name
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    image_urls['banner'] = request.forms.get('image-url-banner')
    image_urls['poster'] = request.forms.get('image-url-poster')
    image_urls['background'] = request.forms.get('image-url-background')
    image_urls['logo'] = request.forms.get('image-url-logo')
    image_urls['icon'] = request.forms.get('image-url-icon')
    content = request.forms.get('content')

    shortcuts = PlatformShortcutsFile(platform)
    shortcut = shortcuts.get_shortcut_match(name)

    for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
        if not image_urls[img_type]:
            continue
        ext = get_ext(image_urls[img_type])
        image_paths[img_type] = os.path.join(BANNER_DIR, img_type, platform, f"{name}{ext}")
        ensure_directory_for_file(image_paths[img_type])
        download = requests.get(image_urls[img_type], timeout=20)
        with open(image_paths[img_type], "wb") as image_file:
            image_file.write(download.content)

    shortcut['name'] = name
    shortcut['cmd'] = shortcut['cmd'] or platform
    shortcut['hidden'] = hidden == 'on'

    for img_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
        if img_type in image_paths:
            shortcut[img_type] = image_paths[img_type]

    if content:
        (content_src_path, content_dst_name) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path,
                                   CONTENT_DIR,
                                   platform,
                                   name,
                                   content_dst_name)
        if content_path:
            shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
            shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    shortcuts.save()

    redirect(f'/library/{platform}')


@route('/shortcuts/delete', method='POST')
@authenticate
def shortcut_delete():
    name = sanitize(request.forms.name)
    platform = sanitize(request.forms.platform)

    shortcuts = PlatformShortcutsFile(platform)
    shortcuts.remove_shortcut(name)
    shortcuts.save()

    delete_file(CONTENT_DIR, platform, name)
    delete_file(BANNER_DIR + '/banner', platform, name)

    redirect(f'/library/{platform}')


@route('/shortcuts/file-upload', method='POST')
@authenticate
def start_file_upload():
    file_name = None
    file_data = request.files.get('banner') or request.files.get('content')

    if file_data:
        file_name = sanitize(file_data.filename)

    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    (_, path) = tempfile.mkstemp(dir=UPLOADS_DIR)
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
    handler = None
    redirect_url = f'/library/{platform}/edit/{content_id}'
    if platform in PLATFORM_HANDLERS:
        handler = PLATFORM_HANDLERS[platform]
    else:
        handler = REMOTE_HANDLERS[platform]
        redirect_url = f'/library/{platform}/edit/{content_id}?remote=true'

    content = handler.get_content(content_id)
    if not content:
        abort(404, 'Content not found')

    handler.install_content(content)

    shortcuts = PlatformShortcutsFile(platform)
    shortcut = handler.get_shortcut(content)
    shortcuts.add_shortcut(shortcut)
    shortcuts.save()

    handler.download_images(content)

    if ('compat_tool' in shortcut
            and shortcut['compat_tool'] in OFFICIAL_COMPAT_TOOLS):
        name = shortcut['compat_tool']
        tool_id = OFFICIAL_COMPAT_TOOLS[name]
        compat_tool = OfficialCompatTool(name, tool_id)
        try:
            compat_tool.install()
        except Exception as e:
            print(e)

    redirect(redirect_url)


@route('/<platform>/uninstall/<content_id>')
@authenticate
def uninstall(platform, content_id):
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, 'Content not found')
    PLATFORM_HANDLERS[platform].uninstall_content(content_id)

    shortcut = PLATFORM_HANDLERS[platform].get_shortcut(content)

    shortcuts = PlatformShortcutsFile(platform)
    shortcuts.remove_shortcut(content.name)
    shortcuts.save()

    redirect(f'/library/{platform}/edit/{content_id}')


@route('/<platform>/update/<content_id>')
@authenticate
def content_update(platform, content_id):
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, 'Content not found')
    PLATFORM_HANDLERS[platform].update_content(content_id)

    redirect(f'/library/{platform}/edit/{content_id}')


@route('/<platform>/progress/<content_id>')
@authenticate
def install_progress(platform, content_id):
    handler = None
    if platform in PLATFORM_HANDLERS:
        handler = PLATFORM_HANDLERS[platform]
    else:
        handler = REMOTE_HANDLERS[platform]

    content = handler.get_content(content_id)
    if not content:
        abort(404, '{} not found'.format(content_id))

    response.content_type = 'application/json'
    values = {
        "operation": content.operation,
        "progress": content.progress,
    }

    return json.dumps(values)


@route('/status-info')
@authenticate
def status_info():
    return template('status_info.tpl')


@route('/system')
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


@route('/system/update', method='POST')
@authenticate
def settings_update():
    SETTINGS_HANDLER.set_setting("enable_ftp_server", sanitize(request.forms.get('enable_ftp_server')) == 'on')
    SETTINGS_HANDLER.set_setting("enable_remote_launch", sanitize(request.forms.get('enable_remote_launch')) == 'on')
    SETTINGS_HANDLER.set_setting("enable_content_sharing", sanitize(request.forms.get('enable_content_sharing')) == 'on')

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

    redirect('/system')



@route('/actions/steam/restart')
@authenticate
def steam_restart():
    try:
        subprocess.call(["steam", "-shutdown"])
    finally:
        redirect('/actions')


@route('/actions/mangohud')
@authenticate
def mangohud():
    try:
        subprocess.call(["mangohudctl", "toggle", "no_display"])
    finally:
        redirect('/actions')


def retroarch_cmd(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(msg, "utf-8"), ('127.0.0.1', 55355))


@route('/actions/retroarch/load_state')
@authenticate
def retro_load_state():
    try:
        retroarch_cmd('LOAD_STATE')
    finally:
        redirect('/actions')


@route('/actions/retroarch/save_state')
@authenticate
def retro_save_state():
    try:
        retroarch_cmd('SAVE_STATE')
    finally:
        redirect('/actions')


@route('/actions/reboot')
@authenticate
def reboot_system():
    try:
        os.system('reboot')
    finally:
        redirect('/actions')


@route('/actions/poweroff')
@authenticate
def poweroff_system():
    try:
        os.system('poweroff')
    finally:
        redirect('/actions')


@route('/actions/suspend')
@authenticate
def suspend_system():
    try:
        os.system('systemctl suspend')
    finally:
        redirect('/actions')


@route('/system/storage', method='GET')
@authenticate
def storage_page():
    return template('storage.tpl')


def operation_status():
    global storage_operation_type
    global storage_operation_status
    global storage_operation_device
    global storage_operation_log

    return {
        'type' : storage_operation_type,
        'options' : {
            'device' : storage_operation_device
        },
        'status' : storage_operation_status,
        'log' : storage_operation_log
    }

# {
#     devices : [
#         {
#             name,
#             model,
#             device_type,  # 'disk' or 'partition'
#             uuid,
#             mount_point,
#             fstype,
#         },
#     ],
#     operation : {
#         type : 'format',
#         options : {
#             device : '/dev/sda'
#         }
#         status : 'in-progress'
#         log : '...'
#     },
# }
@route('/api/storage', method='GET')
@authenticate
def storage_display():
    devices = STORAGE_HANDLER.get_disks()
    response.content_type = 'application/json'
    return {
        'devices' : devices,
        'operation' : operation_status()
    }

# {
#     operation : 'format',
#     options: {
#         device : '/dev/sda'
#     }
# }
@route('/api/storage', method='POST')
@authenticate
def storage_operation():
    global storage_operation_type
    global storage_operation_status
    global storage_operation_device
    global storage_operation_log

    if storage_operation_status == 'in-progress':
        return

    data = request.json
    operation = data['operation']

    if operation == 'reset':
        storage_operation_type   = None
        storage_operation_status = None
        storage_operation_device = None
        storage_operation_log    = None
        return

    if operation == 'format':
        func = STORAGE_HANDLER.format_disk
    elif operation == 'add':
        func = STORAGE_HANDLER.add_disk
    else:
        return

    storage_operation_type = operation

    device = data['options']['device']
    thread = threading.Thread(target=storage_task,
                                args=[device, func])

    storage_operation_status = 'in-progress'
    storage_operation_device = device
    storage_operation_log    = None

    thread.start()

    response.content_type = 'application/json'
    return {
        'operation' : operation_status()
    }

def storage_task(device, func):
    global storage_operation_status
    global storage_operation_device
    global storage_operation_log

    proc = func(device)
    if proc.returncode == 0:
        storage_operation_log = proc.stdout
        storage_operation_status = 'success'
    else:
        storage_operation_log = proc.stderr
        storage_operation_status = 'fail'


def get_audio():
    if not shutil.which('wpctl'):
        return None

    try:
        volume_raw = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]).decode('utf8')
        volume = int(float(volume_raw.split(':')[1].split('[')[0].strip()) * 100)

        return {
            'volume': volume,
            'muted': '[MUTED]' in volume_raw
        }
    except:
        return None


@route('/actions/audio/toggle_mute')
@authenticate
def toggle_mute():
    try:
        subprocess.call(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
    finally:
        redirect('/actions')


@route('/actions/audio/volume_up')
@authenticate
def volume_up():
    try:
        subprocess.call(["wpctl", "set-volume", "--limit", "1.0", "@DEFAULT_AUDIO_SINK@", "10%+"])
    finally:
        redirect('/actions')


@route('/actions/audio/volume_down')
@authenticate
def volume_down():
    try:
        subprocess.call(["wpctl", "set-volume", "--limit", "1.0", "@DEFAULT_AUDIO_SINK@", "10%-"])
    finally:
        redirect('/actions')


@route('/actions/power/tdp_down')
@authenticate
def tdp_down():
    try:
        tdp = power.get_tdp()
        if tdp:
            power.set_tdp(tdp - 1)
    finally:
        redirect('/actions')

@route('/actions/power/tdp_up')
@authenticate
def tdp_up():
    try:
        tdp = power.get_tdp()
        if tdp:
            power.set_tdp(tdp + 1)
    finally:
        redirect('/actions')

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

@route('/authenticate', method='GET')
def authenticate_get():
    return authenticate_route_handler()

@route('/authenticate', method='POST')
def authenticate_post():
    return authenticate_route_handler()

def authenticate_route_handler():
    global LOCAL_PASSWORD

    AUTHENTICATOR.kill()
    password = request.forms.get('password') or request.query.get('password')
    session = request.environ.get('beaker.session')
    keep_password = SETTINGS_HANDLER.get_setting('keep_password') or False
    stored_hash = SETTINGS_HANDLER.get_setting('password')
    local_password = LOCAL_PASSWORD
    LOCAL_PASSWORD=refresh_local_password()
    if password == local_password or AUTHENTICATOR.matches_password(password.upper()) or (keep_password and stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))):
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
    redirect('/login')


@route('/steamgrid/search/<search_string>')
def steamgrid_search(search_string):
    return STEAMGRID_HANDLER.search_games(search_string)


@route('/steamgrid/images/<game_id>')
def steamgrid_get_images(game_id):
    return STEAMGRID_HANDLER.get_images(game_id, request.query.type)


@route('/launch/<id>')
def launch_game(id):
    enabled = SETTINGS_HANDLER.get_setting('enable_remote_launch')
    if not enabled or not id.isnumeric() or type(id) != str:
        redirect('/')
        return

    subprocess.call(["steam", "steam://rungameid/{}".format(id)])
    return 'Launched {}...'.format(id)



########## Content sharing feature

def find_remote_chimera():
    import socket

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 48844))
    while True:
        data, addr = client.recvfrom(1024)
        if data != b'chimera service v1':
            continue
        for platform in PLATFORMS:
            REMOTE_HANDLERS[platform] = ChimeraRemote(platform, addr[0])
        break

def broadcast_service():
    import socket
    import time

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)
    message = b"chimera service v1"
    while True:
        server.sendto(message, ('<broadcast>', 48844))
        time.sleep(10)


if 'pytest' not in sys.modules: # the threads interfere with tests
    contentSharingEnabled = SETTINGS_HANDLER.get_setting('enable_content_sharing')
    if contentSharingEnabled:
        broadcast_thread = threading.Thread(target=broadcast_service)
        broadcast_thread.start()
    else:
        scan_thread = threading.Thread(target=find_remote_chimera)
        scan_thread.start()

@route('/share/images/<image_type>/<platform>/<filename>')
def download_images(image_type, platform, filename):
    if not contentSharingEnabled:
        abort(404)
    if image_type not in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
        abort(404)
    if platform not in PLATFORMS:
        abort(404)
    root = os.path.join(BANNER_DIR, image_type, platform)
    return static_file(unquote(filename), root)


@route('/share/content/<platform>/<filename>')
def download_content(platform, filename):
    if not contentSharingEnabled:
        abort(404)
    if platform not in PLATFORMS:
        abort(404)
    root = os.path.join(CONTENT_DIR, platform)
    if is_direct(platform, 'content'):
        root = os.path.join(root, f'.{platform}')
    return static_file(unquote(filename), root)


@route('/share/platforms/<platform>', method='GET')
def api_get_platform_content(platform):
    if not contentSharingEnabled:
        abort(404)

    shortcut_file = PlatformShortcutsFile(platform)
    shortcuts = sorted(shortcut_file.get_shortcuts_data(),
                       key=lambda s: s['name'])
    data = []
    for shortcut in shortcuts:
        if 'hidden' in shortcut and shortcut['hidden']:
            continue
        if 'deleted' in shortcut and shortcut['deleted']:
            continue
        if not 'params' in shortcut or not shortcut['params']:
            continue

        content_pretty_filename = os.path.basename(shortcut['params'].strip('"'))
        content_original_filename = content_pretty_filename
        content_path = os.path.join(CONTENT_DIR, platform, content_pretty_filename)
        if os.path.islink(content_path):
            content_original_filename = os.path.basename(os.path.realpath(content_path))

        entry = {
            'name': shortcut['name'],
            'content_filename': content_original_filename,
            'content_download_url': f'/share/content/{platform}/{quote(content_pretty_filename)}'
        }

        for image_type in [ 'banner', 'poster', 'background', 'logo', 'icon' ]:
            if image_type in shortcut:
                filename = os.path.basename(shortcut[image_type])
                entry[image_type] = f'/share/images/{image_type}/{platform}/{quote(filename)}'

        data.append(entry)

    response.content_type = 'application/json'
    return json.dumps(data)
