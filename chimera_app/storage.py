import os
import psutil
import pyudev
import re

from subprocess import run


# Is target a substring of any candidate strings?
def do_any_contain(candidates, target):
    for candidate in candidates:
        if target in candidate:
            return True
    return False


class StorageConfig:

    def __init__(self):
        pass


    def get_disks(self):
        # categorize partitions and get their mount points
        bad_parts_list = [] # an array of partition names which should be ignored
        good_parts = {} # a map of mount points indexed by partition name
        for part in psutil.disk_partitions():
            if part.mountpoint in [ "/", "/boot", "/boot/efi", "/boot/grub" ]: # exclude system partitions
                bad_parts_list.append(part.device)
            else:
                good_parts[part.device] = part.mountpoint

        # get device details
        devices = []
        context = pyudev.Context()
        for device in context.list_devices(subsystem="block"):
            props = dict(device.items())
            name = props.get('DEVNAME')
            media_type = props.get('ID_TYPE')

            if media_type != 'disk' or do_any_contain(bad_parts_list, name):
                continue

            devices.append({
                'name'        : name,
                'device_type' : device.device_type,
                'mount_point' : good_parts[name] if name in good_parts else None,
                'model'       : props.get('ID_MODEL'),
                'uuid'        : props.get('ID_FS_UUID'),
                'fstype'      : props.get('ID_FS_TYPE'),
            })

        return devices


    def format_disk(self, disk):
        return run(['/usr/bin/shadowblip/format-media', '--full', '--device', disk], capture_output=True, text=True)
