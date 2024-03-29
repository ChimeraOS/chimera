import os
from typing import List


forbidden_strings = [
            "\n",
            "\t",
            "command=",
            "environment=",
            "from=",
            "no-agent-forwarding",
            "no-pty",
            "no-user-rc",
            "no-X11-forwarding",
            "principals=",
            "tunnel=",
            "zos-key-ring-label=",
        ]


class SSHKeyNotValidException(Exception):
    pass


class SSHKeys:
    def __init__(self, keys_file):
        self.keys_file = keys_file
        self.ssh_dir = os.path.dirname(self.keys_file)
        if not os.path.isdir(self.ssh_dir):
            os.mkdir(self.ssh_dir, 0o700)

    def add_key(self, key) -> bool:
        # Make sure the key is valid
        if not key or not self.looks_like_ssh_key(key):
            return False

        # Make sure no key with the current ID exists already
        current_key_id = self.get_key_id(key)
        for key_id in self.get_key_ids():
            if current_key_id == key_id:
                self.remove_key(key_id)

        # Write the key
        self.__write_key(key)
        return True

    def remove_key(self, key_id):
        if not os.path.isfile(self.keys_file):
            return
        with open(self.keys_file, 'r') as file:
            lines = file.readlines()
        with open(self.keys_file, 'w') as file:
            for line in lines:
                try:
                    if key_id != self.get_key_id(line.strip("\n")):
                        file.write(line)
                except SSHKeyNotValidException:
                    file.write(line)

    @staticmethod
    def get_key_id(key):
        if not SSHKeys.looks_like_ssh_key(key):
            raise SSHKeyNotValidException("{} is not written in a support SSH key format".format(key))
        return key.split(' ')[-1]

    def __write_key(self, key):
        if not os.path.isfile(self.keys_file):
            with open(self.keys_file, 'w') as file:
                file.write(key)
            os.chmod(self.keys_file, 0o600)
        else:
            with open(self.keys_file, 'a') as file:
                file.write("\n" + key)

    def get_keys(self) -> List:
        keys = []
        if os.path.isfile(self.keys_file):
            with open(self.keys_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if self.looks_like_ssh_key(line):
                        keys.append(line)
        return keys

    def get_key_ids(self):
        key_ids = []
        for key in self.get_keys():
            key_ids.append(self.get_key_id(key))
        return key_ids

    @staticmethod
    def looks_like_ssh_key(key) -> bool:
        """
        This function does some basic checks
        It will return False if we're sure the line was not added by chimera
        In this case that means if any option was added which chimera wouldn't use
        Besides that it does a small check to see if it is valid
        The key should not contain tabs or newlines
        :param key: an ssh public key
        :return: boolean stating if the key is allowed to be used
        """
        for s in forbidden_strings:
            if s in key:
                return False
        if not key.startswith("ssh-"):
            return False
        if len(key.split(" ")) != 3:
            return False
        return True
