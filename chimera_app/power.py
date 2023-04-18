import os
from subprocess import run
from chimera_app.config import BIN_PATH


POWER_TOOL_PATH = os.path.join(BIN_PATH, 'power-tool')


DEVICE_DB = {
    'AYANEO::AYANEO 2' : {
        'tdp_min' : 15,
        'tdp_max' : 28,
    }
}


def get_device_info():
    product_name = open('/sys/devices/virtual/dmi/id/product_name', 'r').read().strip()
    vendor_name = open('/sys/devices/virtual/dmi/id/sys_vendor', 'r').read().strip()

    key = vendor_name + '::' + product_name

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

    if new_tdp < device['tdp_min'] or new_tdp > device['tdp_max']:
        return

    run([ 'sudo', '--non-interactive', POWER_TOOL_PATH, 'set-tdp', str(new_tdp) ])
