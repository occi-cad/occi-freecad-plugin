# Installation

At this time, the OCCI plugin cannot be installed via the addon manager in FreeCAD. It must be downloaded and manually copied to your FreeCAD installation's `Mod` directory. The location of this directory varies depending on the operating system and how FreeCAD is installed. The official FreeCAD documentation has some locations [here](https://wiki.freecadweb.org/Installing_more_workbenches), and below are a few other examples for a single user installation.

## Linux Mod Locations

* `~/.local/share/FreeCAD/Mod/` - If FreeCAD was installed through a package manager
* `~/snap/freecad/common/Mod/` - If FreeCAD was installed as a Snap

## Windows Mod Locations

* `C:\Users\[YOUR USERNAME]\Appdata\Roaming\FreeCAD\Mod\`

## MacOS Mod Locations

* `/Users/username/Library/Preferences/FreeCAD/Mod/`

## Static Installation

*NOTE:* If you use this method, you will likely have to rename the plugin directory from `occi-freecad-plugin-main` to `occi-freecad-plugin` or you will get an error when FreeCAD starts up.

If you do not care about updating the plugin, you can do a static installation. A ZIP file of the plugin can be downloaded [here](https://github.com/occi-cad/occi-freecad-plugin/archive/refs/heads/main.zip). The ZIP archive can be extracted into the `Mod` directory for your FreeCAD installation. FreeCAD should then be restarted so that the plugin will load.

## Updatable Installation

The git repository for this plugin can be cloned into the `Mod` directory for your FreeCAD installation.

```
cd /path/to/your/Mod/
git clone https://github.com/occi-cad/occi-freecad-plugin.git
```
Then whenever you want to pull a new version of the plugin, you can pull new changes.
```
cd /path/to/your/Mod/occi-freecad-plugin
git pull
```