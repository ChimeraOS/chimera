import os
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
from chimera_app.config import STREAMING_HANDLER
from chimera_app.config import MANGOHUD_HANDLER
from chimera_app.compat_tools import OFFICIAL_COMPAT_TOOLS
from chimera_app.compat_tools import OfficialCompatTool
from chimera_app.utils import sanitize
from chimera_app.utils import upsert_file
from chimera_app.utils import delete_file
from chimera_app.file_utils import ensure_directory_for_file
from chimera_app.auth_decorator import authenticate
from chimera_app.platforms.epic_store import EpicStore
from chimera_app.platforms.flathub import Flathub
from chimera_app.platforms.gog import GOG
from chimera_app.shortcuts import PlatformShortcutsFile


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
    return template('actions.tpl', audio=get_audio(), bare=True)


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
                platformName=PLATFORMS[platform]
            )
        else:
            return template('custom_login',
                            platform=platform,
                            platformName=PLATFORMS[platform])

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
        data.append({'hidden': hidden,
                     'filename': filename,
                     'banner': banner,
                     'name': shortcut['name']})

    return template('platform.tpl',
                    shortcuts=data,
                    platform=platform,
                    platformName=PLATFORMS[platform])


@route('/library/<platform>/authenticate', method='POST')
@authenticate
def platform_authenticate(platform):
    if platform not in PLATFORM_HANDLERS:
        return

    password = request.forms.get('password')
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
    if platform in PLATFORM_HANDLERS:
        if not authenticate_platform(platform):
            return

        return template(
            'custom',
            app_list=PLATFORM_HANDLERS[platform].get_available_content(request.query.showAll),
            showAll=request.query.showAll,
            isInstalledOverview=False,
            isNew=True,
            platform=platform,
            platformName=PLATFORMS[platform]
        )
    return template('new.tpl',
                    isNew=True,
                    isEditing=False,
                    platform=platform,
                    platformName=PLATFORMS[platform],
                    name='',
                    hidden=''
                    )


@route('/library/<platform>/edit/<name>')
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

    shortcuts = PlatformShortcutsFile(platform)
    shortcut = shortcuts.get_shortcut_match(name)

    return template('new.tpl',
                    isEditing=True,
                    platform=platform,
                    platformName=PLATFORMS[platform],
                    name=name,
                    hidden=shortcut['hidden']
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
        redirect(f'/library/{platform}/new')
        return

    name = name.strip()

    shortcuts = PlatformShortcutsFile(platform)

    if shortcuts.get_shortcut_match(name):
        return 'Shortcut already exists'

    banner_path = None
    if banner:
        (banner_src_path, banner_dst_name) = tmpfiles[banner]
        del tmpfiles[banner]
        banner_path = upsert_file(banner_src_path,
                                  BANNER_DIR + '/banner',
                                  platform,
                                  name,
                                  banner_dst_name)
    else:
        banner_path = os.path.join(BANNER_DIR, 'banner', platform, f"{name}.png")
        ensure_directory_for_file(banner_path)
        if banner_url:
            download = requests.get(banner_url)
            with open(banner_path, "wb") as banner_file:
                banner_file.write(download.content)

    shortcut = {
        'name': name,
        'cmd': platform,
        'hidden': hidden == 'on',
        'banner': banner_path,
        'tags': [PLATFORMS[platform]]
    }

    if content:
        (content_src_path, content_dst_name) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path,
                                   CONTENT_DIR,
                                   platform,
                                   name,
                                   content_dst_name)
        shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
        shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    shortcuts.add_shortcut(shortcut)
    shortcuts.save()

    redirect(f'/library/{platform}')


@route('/shortcuts/edit', method='POST')
@authenticate
def shortcut_update():
    # do not allow editing name
    name = sanitize(request.forms.get('original_name'))
    platform = sanitize(request.forms.get('platform'))
    hidden = sanitize(request.forms.get('hidden'))
    banner_url = request.forms.get('banner-url')
    banner = request.forms.get('banner')
    content = request.forms.get('content')

    shortcuts = PlatformShortcutsFile(platform)
    shortcut = shortcuts.get_shortcut_match(name)

    banner_path = None
    if banner:
        (banner_src_path, banner_dst_name) = tmpfiles[banner]
        del tmpfiles[banner]
        banner_path = upsert_file(banner_src_path,
                                  BANNER_DIR + '/banner',
                                  platform,
                                  name,
                                  banner_dst_name)
    elif banner_url:
        banner_path = os.path.join(BANNER_DIR, 'banner',  platform, f"{name}.png")
        ensure_directory_for_file(banner_path)
        download = requests.get(banner_url)
        with open(banner_path, "wb") as banner_file:
            banner_file.write(download.content)

    shortcut['name'] = name
    shortcut['cmd'] = shortcut['cmd'] or platform
    shortcut['hidden'] = hidden == 'on'
    if banner or banner_url:
        shortcut['banner'] = banner_path
    if content:
        (content_src_path, content_dst_name) = tmpfiles[content]
        del tmpfiles[content]
        content_path = upsert_file(content_src_path,
                                   CONTENT_DIR,
                                   platform,
                                   name,
                                   content_dst_name)
        shortcut['dir'] = '"' + os.path.dirname(content_path) + '"'
        shortcut['params'] = '"' + os.path.basename(content_path) + '"'

    shortcuts.save()

    redirect(f'/library/{platform}')


@route('/shortcuts/delete', method='POST')
@authenticate
def shortcut_delete():
    name = sanitize(request.forms.get('name'))
    platform = sanitize(request.forms.get('platform'))

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
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
    if not content:
        abort(404, 'Content not found')

    PLATFORM_HANDLERS[platform].install_content(content)

    shortcuts = PlatformShortcutsFile(platform)
    shortcut = PLATFORM_HANDLERS[platform].get_shortcut(content)
    shortcuts.add_shortcut(shortcut)
    shortcuts.save()

    PLATFORM_HANDLERS[platform].download_images(content)

    if ('compat_tool' in shortcut
            and shortcut['compat_tool'] in OFFICIAL_COMPAT_TOOLS):
        name = shortcut['compat_tool']
        tool_id = OFFICIAL_COMPAT_TOOLS[name]
        compat_tool = OfficialCompatTool(name, tool_id)
        try:
            compat_tool.install()
        except Exception as e:
            print(e)

    redirect(f'/library/{platform}/edit/{content_id}')


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
    content = PLATFORM_HANDLERS[platform].get_content(content_id)
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


@route('/system/reset_mangohud', method='POST')
@authenticate
def mangohud_reset():
    MANGOHUD_HANDLER.reset_config()
    redirect('/system')


@route('/actions/steam/restart')
@authenticate
def steam_restart():
    try:
        subprocess.call(["pkill", "steamos-session"])
    finally:
        redirect('/actions')


@route('/actions/steam/compositor')
@authenticate
def steam_compositor():
    try:
        subprocess.call(["bin/toggle-steamos-compositor"])
    finally:
        redirect('/actions')


@route('/actions/steam/overlay')
@authenticate
def steam_overlay():
    try:
        subprocess.call(["xdotool", "key", "shift+Tab"])
    finally:
        redirect('/actions')


@route('/actions/mangohud')
@authenticate
def mangohud():
    key = MANGOHUD_HANDLER.get_toggle_hud_key()
    try:
        subprocess.call(["xdotool", "key", key])
    finally:
        redirect('/actions')


@route('/streaming')
@authenticate
def streaming_control():
    is_streaming = STREAMING_HANDLER.is_streaming()
    is_recording = STREAMING_HANDLER.is_recording()
    return template('streaming_control.tpl',
                    streaming=is_streaming,
                    recording=is_recording)


@route('/streaming/config')
@authenticate
def streaming_config():
    current_inputs = SETTINGS_HANDLER.get_setting("ffmpeg_inputs")
    current_vcodecs = SETTINGS_HANDLER.get_setting("ffmpeg_vcodec")
    current_acodecs = SETTINGS_HANDLER.get_setting("ffmpeg_acodec")
    if type(current_inputs) is not list and current_inputs:
        current_inputs = [current_inputs]
    if type(current_vcodecs) is not list and current_vcodecs:
        current_vcodecs = [current_vcodecs]
    if type(current_acodecs) is not list and current_acodecs:
        current_acodecs = [current_acodecs]
    return template('streaming_config.tpl',
                    inputs=current_inputs,
                    vcodecs=current_vcodecs,
                    acodecs=current_acodecs)


@route('/streaming/add_input', method='POST')
@authenticate
def streaming_add_input():
    current_input = SETTINGS_HANDLER.get_setting("ffmpeg_inputs")
    new_input = request.forms.get('new_input')
    if type(current_input) is list:
        current_input.append(new_input)
    elif type(current_input) is str:
        if current_input.strip():
            current_input = [current_input].append(new_input)
        else:
            current_input = new_input
    SETTINGS_HANDLER.set_setting("ffmpeg_inputs", current_input)
    redirect('/streaming/config')


@route('/streaming/remove_input/<input_id:int>', method='POST')
@authenticate
def streaming_remove_input(input_id):
    current_input = SETTINGS_HANDLER.get_setting("ffmpeg_inputs")
    if type(current_input) is list:
        del current_input[input_id]
    else:
        current_input = ''
    SETTINGS_HANDLER.set_setting("ffmpeg_inputs", current_input)
    redirect('/streaming/config')


@route('/streaming/add_vcodec', method='POST')
@authenticate
def streaming_add_vcodec():
    current_vcodec = SETTINGS_HANDLER.get_setting("ffmpeg_vcodec")
    new_vcodec = request.forms.get('new_vcodec')
    if type(current_vcodec) is list:
        current_vcodec.append(new_vcodec)
    elif type(current_vcodec) is str:
        if current_vcodec.strip():
            current_vcodec = [current_vcodec].append(new_vcodec)
        else:
            current_vcodec = new_vcodec

    SETTINGS_HANDLER.set_setting("ffmpeg_vcodec", current_vcodec)
    redirect('/streaming/config')


@route('/streaming/remove_vcodec/<vcodec_id:int>', method='POST')
@authenticate
def streaming_remove_vcodec(vcodec_id):
    current_vcodec = SETTINGS_HANDLER.get_setting("ffmpeg_vcodec")
    if type(current_vcodec) is list:
        del current_vcodec[vcodec_id]
    else:
        current_vcodec = ''
    SETTINGS_HANDLER.set_setting("ffmpeg_vcodec", current_vcodec)
    redirect('/streaming/config')


@route('/streaming/add_acodec', method='POST')
@authenticate
def streaming_add_acodec():
    current_acodec = SETTINGS_HANDLER.get_setting("ffmpeg_acodec")
    new_acodec = request.forms.get('new_acodec')
    if type(current_acodec) is list:
        current_acodec.append(new_acodec)
    elif type(current_acodec) is str:
        if current_acodec.strip():
            current_acodec = [current_acodec].append(new_acodec)
        else:
            current_acodec = new_acodec
    SETTINGS_HANDLER.set_setting("ffmpeg_acodec", current_acodec)
    redirect('/streaming/config')


@route('/streaming/remove_acodec/<acodec_id:int>', method='POST')
@authenticate
def streaming_remove_acodec(acodec_id):
    current_acodec = SETTINGS_HANDLER.get_setting("ffmpeg_acodec")
    if type(current_acodec) is list:
        del current_acodec[acodec_id]
    else:
        current_acodec = ''
    SETTINGS_HANDLER.set_setting("ffmpeg_acodec", current_acodec)
    redirect('/streaming/config')


@route('/streaming/net/start')
@authenticate
def streaming_net_start():
    STREAMING_HANDLER.stream_to_lan()
    return template('success.tpl')


@route('/streaming/net/stop')
@authenticate
def streaming_stop():
    STREAMING_HANDLER.stop_stream()
    return template('success.tpl')


@route('/record/start')
@authenticate
def record_start():
    STREAMING_HANDLER.record_screen()
    return template('success.tpl')


@route('/record/stop')
@authenticate
def record_stop():
    STREAMING_HANDLER.stop_record()
    return template('success.tpl')


@route('/system/mangohud/save_config', method='POST')
@authenticate
def mangohud_save_config():
    new_content = request.forms.get('new_content')
    MANGOHUD_HANDLER.save_config(new_content)
    redirect('/system')


@route('/system/mangohud/edit_config')
@authenticate
def mangohud_edit():
    current_content = MANGOHUD_HANDLER.get_current_config()
    return template('mangohud_edit.tpl', file_content=current_content)


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


@route('/virtual_keyboard')
@authenticate
def virtual_keyboard():
    return template('virtual_keyboard.tpl')


@route('/virtual_keyboard/string', method='POST')
@authenticate
def virtual_keyboard_string():
    string = request.forms.get('str')
    string_without_controlcharacters = "".join(c for c in string if unicodedata.category(c) != "Cc")
    try:
        subprocess.call(["xdotool", "type", "--", string_without_controlcharacters])
    finally:
        redirect('/virtual_keyboard')


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


@route('/system/storage',method='GET')
@authenticate
def storage_display():
    disks = STORAGE_HANDLER.get_disks()
    return template('storage.tpl', disks=disks)


@route('/system/storage/format', method='POST')
@authenticate
def storage_format():
    disk = request.POST.get("disk")
    proc = STORAGE_HANDLER.format_disk(disk)
    if proc.returncode == 0:
        log = proc.stdout
    else:
        log = proc.stderr
    return template('format_status.tpl', log=log)


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


@route('/actions/audio/toggle_mute')
@authenticate
def toggle_mute():
    try:
        subprocess.call(["ponymix", "toggle"])
    finally:
        redirect('/actions')


@route('/actions/audio/volume_up')
@authenticate
def volume_up():
    try:
        subprocess.call(["ponymix", "increase", "10"])
    finally:
        redirect('/actions')


@route('/actions/audio/volume_down')
@authenticate
def volume_down():
    try:
        subprocess.call(["ponymix", "decrease", "10"])
    finally:
        redirect('/actions')


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
    redirect('/login')


@route('/steamgrid/search/<search_string>')
def steamgrid_search(search_string):
    return STEAMGRID_HANDLER.search_games(search_string)


@route('/steamgrid/images/<game_id>')
def steamgrid_get_images(game_id):
    return STEAMGRID_HANDLER.get_images(game_id)
