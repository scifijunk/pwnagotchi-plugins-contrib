import pwnagotchi.plugins as plugins
import logging
import subprocess
import os
import shutil

class AircrackOnly(plugins.Plugin):
    __author__ = 'pwnagotchi [at] rossmarks [dot] uk'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'Confirm pcap contains a handshake/PMKID and copy it to a directory'

    def __init__(self):
        self.directory = '/home/scifijunkie'

    def on_loaded(self):
        logging.info("AircrackOnly plugin loaded")
        aircrack_installed = self.check_aircrack_installed()
        if aircrack_installed:
            logging.info(f"AircrackOnly: Found {aircrack_installed}")
        else:
            logging.warning("Aircrack-ng is not installed!")

    def check_aircrack_installed(self):
        check = subprocess.run(
            '/usr/bin/dpkg -l aircrack-ng | grep aircrack-ng | awk \'{print $2, $3}\'',
            shell=True,
            stdout=subprocess.PIPE,
            text=True
        )
        return check.stdout.strip()

    def is_handshake_present(self, filename, keyword):
        result = subprocess.run(
            f'/usr/bin/aircrack-ng {filename} | grep "{keyword}"',
            shell=True,
            stdout=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0

    def on_handshake(self, agent, filename, access_point, client_station):
        handshake_found = self.is_handshake_present(filename, "WPA (1 handshake)")
        pmkid_found = self.is_handshake_present(filename, "WPA (1 handshake, with PMKID)")

        if handshake_found or pmkid_found:
            new_file = os.path.join(self.directory, os.path.basename(filename))
            shutil.copy(filename, new_file)
            logging.info(f"AircrackOnly: Copied {filename} to {new_file}")

    def on_options_update(self, agent, interface, options):
        self.directory = options.get('directory', self.directory)
        logging.info(f"AircrackOnly: Using directory: {self.directory}")
