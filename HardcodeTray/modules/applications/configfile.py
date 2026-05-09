"""
Fixes Hardcoded tray icons in Linux.
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : GPL
"""
from os import path, makedirs
from shutil import copyfile
from HardcodeTray.modules.applications.application import Application
from HardcodeTray.utils import execute


class ConfigFileApplication(Application):
    """Application that stores icon paths in a config file."""
    BACKUP_IGNORE = True

    def __init__(self, parser):
        Application.__init__(self, parser)

    def execute(self, action):
        from HardcodeTray.app import App
        from HardcodeTray.enum import Action

        from HardcodeTray.const import USERHOME
        config_file = self.parser.config_file.replace("{userhome}", USERHOME)
        icon_size = App.icon_size()

        with open(config_file, "r") as f:
            content = f.read()

        if action == Action.APPLY:
            output_dir = self.parser.icons_output.replace("{userhome}", USERHOME)
            makedirs(output_dir, exist_ok=True)
            new_content = self._set_key(content, self.parser.default_key, "false")

            for icon in self.icons:
                theme_icon = icon.theme
                icon_ext = icon.theme_ext
                output_icon = path.join(output_dir, icon.original + ".png")

                if icon_ext == "svg":
                    execute(["rsvg-convert", "-w", str(int(icon_size)),
                             "-h", str(int(icon_size)),
                             theme_icon, "-o", output_icon])
                else:
                    copyfile(theme_icon, output_icon)

                new_content = self._set_key(new_content, icon.config_key, output_icon)

            with open(config_file, "w") as f:
                f.write(new_content)

        elif action == Action.REVERT:
            new_content = self._set_key(content, self.parser.default_key, "true")
            for icon in self.icons:
                new_content = self._set_key(new_content, icon.config_key, "")
            with open(config_file, "w") as f:
                f.write(new_content)

    def _set_key(self, content, key, value):
        lines = content.splitlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith(key + "="):
                new_lines.append("{}={}".format(key, value))
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append("{}={}".format(key, value))
        return "\n".join(new_lines) + "\n"
