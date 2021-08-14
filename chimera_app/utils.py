"""Utilities for the chimera_app tools"""
import os
import re
import shutil
import subprocess
from datetime import datetime
import psutil
from PIL import Image, ImageFont, ImageDraw
import chimera_app.context as context
import chimera_app.shortcuts as shortcuts


def ensure_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory, mode=0o755, exist_ok=True)


def ensure_directory_for_file(file):
    d = os.path.dirname(file)
    ensure_directory(d)


def yearsago(years):
    from_date = datetime.now().date()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        return from_date.replace(month=2, day=28, year=from_date.year - years)


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def sanitize(string):
    if isinstance(string, str):
        retval = string
        for r in ['\n', '\r', '/', '\\', '\0']:
            retval = retval.replace(r, '_')
        retval.replace('"', '')
        return retval
    return string


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


def is_direct(platform, content_type):
    return ((platform == "arcade" or platform == "neo-geo") and
            content_type == "content")


def upsert_file(src_path, base_dir, platform, name, dst_name):
    if not src_path:
        return

    content_type = os.path.basename(base_dir)
    filename = sanitize(dst_name)
    file_dir = f"{base_dir}/{platform}/.{name}"

    # mame ROM files have dependencies on each other,
    # so store them all in a single directory
    if is_direct(platform, content_type):
        file_dir = f"{base_dir}/{platform}/.{platform}"

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_path = f"{file_dir}/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)

    shutil.move(src_path, file_path)

    _, ext = os.path.splitext(filename)
    dst = f"{base_dir}/{platform}/{name}{ext}"

    delete_file_link(base_dir, platform, name)
    os.symlink(file_path, dst)

    # mame requires ROM files to have a specific name,
    # so launch original file directly
    if is_direct(platform, content_type):
        return file_path

    return dst


def strip(string):
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    return string


def delete_file(base_dir, platform, name):
    if is_direct(platform, os.path.basename(base_dir)):
        shortcuts_file = shortcuts.PlatformShortcutsFile(platform)
        shortcuts_file.load_data()
        shortcut = shortcuts_file.get_shortcut_match(name, platform)
        if 'dir' in shortcut and 'params' in shortcut:
            file_path = os.path.join(strip(shortcut['dir']),
                                     strip(shortcut['params']))
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        file_dir = f"{base_dir}/{platform}/.{name}"
        if os.path.exists(file_dir):
            shutil.rmtree(file_dir)

    delete_file_link(base_dir, platform, name)


def generate_banner(text, path):
    # The thumbnail size used by Steam is set
    banner_width = 460
    banner_height = 215
    banner = Image.new('RGB', (banner_width, banner_height), color=(0, 0, 0))

    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
                              24)

    text_width, text_height = font.getsize(text)

    # Shorten the text if it doesn't fit on the image
    while text_width > banner_width:
        text = text[:-4] + "..."
        text_width, text_height = font.getsize(text)

    text_x = int(banner_width / 2 - text_width / 2)
    text_y = int(banner_height / 2 - text_height / 2)

    title = ImageDraw.Draw(banner)
    title.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

    banner.save(path)


def client_running() -> False:
    """Check if the Steam client is running"""
    pid_path = os.path.expanduser('~/.steam/steam.pid')
    if not os.path.exists(pid_path):
        return False
    with open(pid_path) as pid_file:
        pid = pid_file.read()
    try:
        maybe_steam = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return False
    return maybe_steam.name() == 'steam'


def install_by_id(steam_id: str) -> None:
    if client_running():
        subprocess.run(['steam', 'steam://install/' + steam_id],
                       check=True)
    else:
        raise Exception('Steam Client is not running')
