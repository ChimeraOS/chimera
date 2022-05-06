import os
import psutil
import pyudev
import re

from subprocess import Popen, PIPE, run

class StorageConfig:


    def __init__(self):
        pass 


    # Modified from https://www.programcreek.com/python/example/98337/pyudev.Context
    def get_disks(self):
        disks = []
        context = pyudev.Context()
        for device in context.list_devices(subsystem="block"):
            if device.device_type == "disk":
                property_dict = dict(device.items())
                name = property_dict.get('DEVNAME', "Unknown").split('/')[-1]
                if "loop" in name:
                    break
                partitions = self.get_partitions(name)
                is_sys_dev=False
                # Make sure we don't list the system drive.
                for part in psutil.disk_partitions():
                    for part_dict in partitions:
                        # part.device is full path, partitions is truncated partition name.
                        strip_path = part.device.replace("/dev/", "") 
                        if strip_path in part_dict["name"]:
                            if part.mountpoint in ["/", "/boot", "/boot/efi", "/boot/grub"]:
                                is_sys_dev=True
                                break
                            else:
                                part_dict["mount_point"] = part.mountpoint

                # Append the disk to the list.
                if not is_sys_dev:
                    disks.append(
                    {
                        'name':     name,	    	
                        'model':	property_dict.get('ID_MODEL', "Unknown"),
                        'partitions': partitions
			        })
        return disks 


    def get_partitions(self, disk):
        partitions = []
        context = pyudev.Context()
        for device in context.list_devices(subsystem="block"):
            if device.device_type == "partition":
                property_dict = dict(device.items())
                name = property_dict.get('DEVNAME', "Unknown").split('/')[-1]
                uuid = property_dict.get('ID_FS_UUID',"Unkown")
                fstype = property_dict.get('ID_FS_TYPE',"Unkown")
                if disk in name:
                    partitions.append({"name": name, "mount_point": "", "uuid": uuid, "fstype": fstype})
        return partitions


    def format_disk(self, disk):
        return run(['sudo', '/usr/lib/media-support/format-media.sh', disk], capture_output=True, text=True, input="y")
        # Streamable output version, needs websocket connection and JS to stream to page.
        #process = Popen(['/usr/lib/media-support/format-media.sh', disk], stdout=PIPE, stdin=PIPE, shell=True)
        #process.communicate(b'y')
        #return process
