import re
import os
import shutil
import yaml
from steam_buddy.config import SHORTCUT_DIR


def sanitize(string):
    if isinstance(string, str):
        return string.replace('\n', '_').replace('\r', '_').replace('/', '_').replace('\\', '_').replace('\0', '_').replace('"', '')

    return string


def load_shortcuts(platform):
    shortcuts = []
    if not os.path.exists(SHORTCUT_DIR):
        os.makedirs(SHORTCUT_DIR)
    shortcuts_file = "{shortcuts_dir}/steam-buddy.{platform}.yaml".format(shortcuts_dir=SHORTCUT_DIR, platform=platform)
    if os.path.isfile(shortcuts_file):
        shortcuts = yaml.load(open(shortcuts_file), Loader=yaml.Loader)

    if not shortcuts:
        shortcuts = []

    return shortcuts


def delete_file_link(base_dir, platform, name):
    e = re.escape(name) + r"\.[^.]+$"
    d = os.path.join(base_dir, platform)
    links = []
    if os.path.isdir(d):
        links = [os.path.join(d, l) for l in os.listdir(d) if re.match(e, l)]

    if len(links) < 1:
        return

    for link in links:
        if os.path.islink(link) or os.path.exists(link):
            os.remove(link)


def upsert_file(src_path, base_dir, platform, name, dst_name):
    if not src_path:
        return

    filename = sanitize(dst_name)
    file_dir = "{base_dir}/{platform}/.{name}".format(base_dir=base_dir, platform=platform, name=name)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_path = "{file_dir}/{filename}".format(file_dir=file_dir, filename=filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    shutil.move(src_path, file_path)

    _, ext = os.path.splitext(filename)
    dst = "{base_dir}/{platform}/{name}{ext}".format(base_dir=base_dir, platform=platform, name=name, ext=ext)

    delete_file_link(base_dir, platform, name)
    os.symlink(file_path, dst)

    # mame requires ROM files to have a specific name, so launch original file directly
    if platform == "arcade" and os.path.basename(base_dir) == "content":
        return file_path

    return dst


def delete_file(base_dir, platform, name):
    file_dir = "{base_dir}/{platform}/.{name}".format(base_dir=base_dir, platform=platform, name=name)

    if os.path.exists(file_dir):
        shutil.rmtree(file_dir)

    delete_file_link(base_dir, platform, name)
