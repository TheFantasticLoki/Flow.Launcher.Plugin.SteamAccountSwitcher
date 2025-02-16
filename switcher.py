import sys
from pathlib import Path
import json
import logging

plugindir = Path.absolute(Path(__file__).parent)
paths = (".", "lib", "plugin")
sys.path = [str(plugindir / p) for p in paths] + sys.path
logger = logging.getLogger(__name__)

from flox import Flox
import os
import xml.etree.ElementTree as ET
import re
import subprocess


class SteamAccountSwitcher(Flox):

    # query is default function to receive realtime keystrokes from wox launcher
    def query(self, query):
        results = []
        steam_profiles = []
        xml_path = os.path.expandvars(r"%appdata%\TcNo Account Switcher\LoginCache\Steam\VACCache")
        avatar_path = os.path.expandvars(r"%appdata%\TcNo Account Switcher\wwwroot\img\profiles\steam")
        try:
            for file in os.listdir(xml_path):
                if file.endswith(".xml"):
                    file_path = os.path.join(xml_path, file)
                    tree = ET.parse(file_path)
                    profile = tree.getroot()
                    steamId64 = profile.find("steamID64").text
                    steam_profiles.append({
                        "steamId": profile.find("steamID").text,
                        "steamId64": steamId64,
                        "avatarIcon": os.path.join(avatar_path, steamId64 + ".jpg"),
                    })
        except Exception as e:
            self.add_item(
                title="Error",
                subtitle=str(e),
                icon=self.icon,
                method=Utils.copy_to_clipboard(str(e)),
            )
            return
        try:
            profilesStr = ""
            unknown_profiles = 0
            for stm in steam_profiles:
                stm["steamIdType"] = f"{type(stm['steamId'])}"
                profilesStr += f"{stm}, "
                steam_id = "Unknown"
                if isinstance(stm["steamId"], str):
                    if stm["steamId"] != None:
                        steam_id = stm["steamId"]
                else:
                    unknown_profiles += 1
                    stm["steamId"] = "Unknown"+str(unknown_profiles)
                    steam_id = "Unknown"
                if not re.search(query, stm["steamId"], re.IGNORECASE):
                    continue

                self.add_item(
                    title=steam_id,
                    subtitle=stm["steamId64"],
                    icon=stm["avatarIcon"],
                    method=self.switch,
                    parameters=[stm["steamId64"]],
                )
        except Exception as e:
            self.add_item(
                title="Error",
                subtitle=str(e) + " | " + f"steam_profiles: {json.dumps(steam_profiles)}",
                icon=self.icon,
                method=Utils.copy_to_clipboard(f"{str(e)} | steam_profiles: {json.dumps(steam_profiles)}"),
            )
            return
        return results

    def switch(self, steamId64):
        folder = "C:/Program Files/TcNo Account Switcher/"
        exe_path = f"{folder}TcNo-Acc-Switcher.exe"
        cmd = f'powershell -Command "Start-Process \'{exe_path}\' -ArgumentList \'+s:{steamId64}\' -Verb RunAs -WindowStyle Hidden"'
        subprocess.run(cmd, shell=True)
        return None

class Utils:
    @staticmethod
    def copy_to_clipboard(text):
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()

if __name__ == "__main__":
    SteamAccountSwitcher()
