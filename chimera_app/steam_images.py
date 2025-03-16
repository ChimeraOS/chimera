"""Submodule to apply custom Steam images"""

import os
import subprocess
import chimera_app.context as context
from chimera_app.file_utils import ensure_directory

from chimera_app.config import BANNER_DIR, GAMEDB

def get_ext(url):
    url_noquery = url.split('?')[0]
    ext = os.path.splitext(url_noquery)[1]

    if not ext:
        ext = '.jpg'

    return ext

def get_image_path(steamid, img_url, img_type):
    ext = get_ext(img_url)
    base_path = os.path.join(BANNER_DIR, img_type, 'steam')
    ensure_directory(base_path)

    return os.path.join(base_path, steamid + ext)

def download_image(img_url, img_path):
    if img_url and img_url.startswith('http'):
        if not os.path.exists(img_path):
            subprocess.check_output(["curl", img_url, "-o", img_path])

def get_image_id(type, steamid):
    if type == 'banner':
        return steamid
    elif type == 'poster':
        return steamid + 'p'
    elif type == 'background':
        return steamid + '_hero'
    elif type == 'logo':
        return steamid + '_logo'

def apply_image(steamid, img_path, type) -> None:
    if not img_path:
        return

    img_id = get_image_id(type, steamid)
    _, ext = os.path.splitext(img_path)
    for user_dir in context.STEAM_USER_DIRS:
        dst_dir = user_dir + '/config/grid/'
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        dst = dst_dir + str(img_id) + ext
        if os.path.islink(dst) or os.path.isfile(dst):
            continue # do not delete/overwrite user customizations
        os.symlink(img_path, dst)

def apply_custom_steam_images():
    if not GAMEDB or 'steam' not in GAMEDB:
        print('No custom Steam images applied')
        return

    for key in GAMEDB['steam']:
        entry = GAMEDB['steam'][key]
        for img_type in [ 'banner', 'poster', 'background', 'logo' ]:
            img_url = getattr(entry, img_type, None)
            if not img_url:
                continue
            img_path = get_image_path(key, img_url, img_type)
            download_image(img_url, img_path)
            if os.path.isfile(img_path):
                apply_image(key, img_path, img_type)
