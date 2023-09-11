import os
import psutil
import pyudev
import re

from subprocess import run


# Is target a substring of any candidate strings or vice versa?
def do_any_contain(candidates, target):
    for candidate in candidates:
        if target in candidate or candidate in target:
            return True
    return False


class StorageConfig:

    def __init__(self):
        pass


    def get_disks(self):
        # categorize partitions and get their mount points
        ignore_list = [] # an array of device/partition names which should be ignored
        good_parts = {} # a map of mount points indexed by partition name
        for part in psutil.disk_partitions():
            if part.mountpoint in [ "/", "/boot", "/boot/efi", "/boot/grub" ]: # exclude system partitions
                ignore_list.append(part.device)
            else:
                good_parts[part.device] = part.mountpoint

        # get device details
        devices = []
        context = pyudev.Context()
        for device in context.list_devices(subsystem="block"):
            props = dict(device.items())
            name = props.get('DEVNAME')
            is_allowed = props.get('DEVTYPE') == 'disk' or props.get('DEVTYPE') == 'partition' or props.get('ID_TYPE') == 'disk' or props.get('ID_DRIVE_FLASH_SD') == '1' or props.get('ID_DRIVE_MEDIA_FLASH_SD') == '1'
            is_ignored = props.get('DEVTYPE') == 'disk' and (props.get('UDISKS_IGNORE') == '1' or props.get('UDISKS_PRESENTATION_HIDE') == '1') # only ignore/hide entire disks, not individual partitions

            if not is_allowed or is_ignored:
                ignore_list.append(name)
                continue

            if do_any_contain(ignore_list, name):
                continue

            devices.append({
                'name'        : name,
                'device_type' : device.device_type,
                'mount_point' : good_parts[name] if name in good_parts else None,
                'model'       : props.get('ID_MODEL') or props.get('ID_NAME'),
                'uuid'        : props.get('ID_FS_UUID'),
                'fstype'      : props.get('ID_FS_TYPE'),
            })

        return devices

    # format the device
    def format_disk(self, disk):
        return run(['/usr/bin/shadowblip/format-media', '--full', '--device', disk], capture_output=True, text=True)

    # adds disk for use as Steam storage
    def add_disk(self, disk):
        return run(['/usr/bin/shadowblip/init-media', disk], capture_output=True, text=True)
