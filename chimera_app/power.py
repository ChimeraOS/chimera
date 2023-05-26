import os
from subprocess import run
from chimera_app.config import BIN_PATH


POWER_TOOL_PATH = os.path.join(BIN_PATH, 'power-tool')


DEVICE_DB = {
    # Aya Neo 2021
    'AMD Ryzen 5 4500U with Radeon Graphics' : {
        'min_tdp'   : 5,
        'max_tdp'   : 28,
        'max_boost' : 2,
    },
    # Aya Neo Air
    'AMD Ryzen 5 5560U with Radeon Graphics' : {
        'min_tdp'   : 3,
        'max_tdp'   : 28,
        'max_boost' : 2,
    },
    # ONEXPLAYER Mini AMD
    'AMD Ryzen 7 5800U with Radeon Graphics' : {
        'min_tdp'   : 5,
        'max_tdp'   : 33,
        'max_boost' : 5,
    },
    # Aya Neo 2
    # AOKZOE A1
    # Aya Neo Air Plus
    'AMD Ryzen 7 6800U with Radeon Graphics' : {
        'min_tdp'   : 5,
        'max_tdp'   : 33,
        'max_boost' : 5,
    },
}


def get_device_info():
    results = run([ 'bash', '-c', 'lscpu | grep "Model name" | cut -d: -f2' ], capture_output=True, text=True)
    key = results.stdout.strip()

    if not key in DEVICE_DB:
        return None

    return DEVICE_DB[key]


def get_tdp():
    device = get_device_info()
    if not device:
        return

    results = run([ 'sudo', '--non-interactive', POWER_TOOL_PATH, 'get-tdp' ], capture_output=True, text=True)
    lines = results.stdout.splitlines()

    tdp = None
    if len(lines) > 0:
        tdp = results.stdout.splitlines()[0]

    if not tdp:
        return

    return int(tdp)


def set_tdp(new_tdp):
    if type(new_tdp) != int:
        return

    device = get_device_info()
    if not device:
        return

    if new_tdp < device['min_tdp'] or new_tdp > device['max_tdp']:
        return

    run([ 'sudo', '--non-interactive', POWER_TOOL_PATH, 'set-tdp', str(new_tdp), str(device['max_boost']) ])
