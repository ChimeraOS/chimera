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

def get_image_path(steamid, entry, img_type):
    img_url = entry[img_type]
    if not img_url:
        return None

    ext = get_ext(img_url)
    base_path = os.path.join(BANNER_DIR, img_type, 'steam')
    ensure_directory(base_path)

    return os.path.join(base_path, steamid + ext)

def download_image(steamid, entry, img_type):
    img_url = entry[img_type]
    if img_url and img_url.startswith('http'):
        img_path = get_image_path(steamid, entry, img_type)
        if os.path.exists(img_path):
            return
        subprocess.check_output(["curl", img_url, "-o", img_path])
        return img_path

def get_image_id(type, steamid):
    if type == 'banner':
        return steamid
    elif type == 'poster':
        return steamid + 'p'
    elif type == 'background':
        return steamid + '_hero'
    elif type == 'logo':
        return steamid + '_logo'

def create_image(steamid, img_path, type) -> None:
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
            return # do not delete/overwrite user customizations
        os.symlink(img_path, dst)

def apply_custom_steam_images():
    if not GAMEDB or 'steam' not in GAMEDB:
        print('No custom Steam images applied')
        return

    for key in GAMEDB['steam']:
        for img_type in [ 'banner', 'poster', 'background', 'logo' ]:
            if img_type in GAMEDB['steam'][key]:
                img_path = download_image(key, GAMEDB['steam'][key], img_type)
                if img_path:
                    create_image(key, img_path, img_type)
