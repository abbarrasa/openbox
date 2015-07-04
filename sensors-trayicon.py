#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Alberto Buitrago <echo YWJiYXJyYXNhQGdtYWlsLmNvbQo= | base64 -d>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# License: GPLv3
# Date: 22 June 2015
# Latest edit: 27 June 2015
# Website: https://github.com/abbarrasa/openbox
#
# A script to put a sensor monitor in system tray.

import gtk
import sensors as pysensors
import psutil
import os
import gobject
import base64

from gtk import gdk
from xdg import BaseDirectory as base_directory


class Sensors:
    def __init__(self):
        self.__FEATURE_TEMP = 2
        self.sensors = {}

    def get_sensors(self):
        self.update_sensors()
        return self.sensors

    def append_sensor(self, sensor, label, format, value, value_alarm):
        self.sensors.update({
            sensor: {
                'label': label,
                'format': format,
                'value': value,
                'value_alarm': value_alarm
            }
        })

    def update_sensors(self):
        # Temperature sensors
        for chip in pysensors.iter_detected_chips():
            for feature in chip:
                if feature.type == self.__FEATURE_TEMP:
                    self.append_sensor(
                        chip.prefix + '_' + feature.name,
                        feature.label,
                        '%.1f ºC',
                        feature.get_value(),
                        100.0)

        # Cpu usage
        self.append_sensor(
            'cpu',
            'CPU usage',
            '%.1f %%',
            psutil.cpu_percent(interval=1),
            95.0)

        # Memory usage
        vmem = psutil.virtual_memory()
        self.append_sensor(
            'memory', 'Memory usage', '%.1f %%', vmem.percent, 95.0)

        # Swap usage
        vswap = psutil.swap_memory()
        self.append_sensor(
            'swap', 'Swap usage', '%.1f %%', vswap.percent, 95.0)


class SystrayIcon:
    def __init__(self):
        self._APPNAME = 'Sensors TrayIcon'
        self._VERSION = '0.1'
        self._CONFIG_DIR = os.path.join(
            base_directory.xdg_config_home, 'sensors-trayicon')

        self.sensors = Sensors()
        self.tray = gtk.StatusIcon()
        self.tray.set_from_file(
            os.path.join(self._CONFIG_DIR, 'themes/default/trayicon.svg'))
        self.tray.set_has_tooltip(True)
        self.tray.set_tooltip(self._APPNAME)
        self.tray.connect('popup-menu', self.on_popup_menu)

        self.build_menu()

        gobject.timeout_add(2000, self.update_menu)

    def add_menu_item(self, title):
        menuitem = gtk.MenuItem()
        menuitem.set_label(title)

        self.menu.append(menuitem)
        self.menu.show_all()
        return menuitem

    def add_separator(self):
        menuitem = gtk.SeparatorMenuItem()
        self.menu.append(menuitem)
        self.menu.show_all()

    def build_menu(self):
        self.menu = gtk.Menu()
        self.items = {}
        mysensors = self.sensors.get_sensors()

        # show settings dialog
        self.items['preferences'] = self.add_menu_item('Preferences')
        self.items['preferences'].connect(
            "activate", lambda w: self.show_preferences_dialog())
        self.add_separator()

        # Add menu items for sensors
        for sensor in mysensors:
            label = '{0}: {1}'.format(
                mysensors[sensor]['label'], mysensors[sensor]['format'])
            self.items[sensor] = self.add_menu_item(
                label % mysensors[sensor]['value'])
        self.add_separator()

        self.items['about'] = self.add_menu_item('About')
        self.items['about'].connect(
            "activate", lambda w: self.show_about_dialog())
        self.add_separator()

        self.items['quit'] = self.add_menu_item('Quit')
        self.items['quit'].connect(
            "activate", lambda w: gtk.main_quit())
        self.add_separator()

    def on_popup_menu(self, status_icon, event_button, event_time):
        self.menu.show_all()
        self.menu.popup(None, None, None, event_button, event_time, self.tray)

    def show_about_dialog(self):
        about_dialog = gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_program_name(self._APPNAME)
        about_dialog.set_logo(
            gdk.pixbuf_new_from_file(
                os.path.join(
                    self._CONFIG_DIR, 'themes/default/sensors-trayicon.svg')))
        about_dialog.set_icon(
            about_dialog.render_icon(
                gtk.STOCK_ABOUT, gtk.ICON_SIZE_DIALOG))
        about_dialog.set_version(self._VERSION)
        about_dialog.set_copyright("Copyright \xc2\xa9 2015 Alberto Buitrago")
        about_dialog.set_comments(
            "A sensor monitor in systray for Openbox desktop")
        about_dialog.set_authors([
            'Alberto Buitrago <%s>' % base64.b64decode(
                'YWJiYXJyYXNhQGdtYWlsLmNvbQ==')])
        about_dialog.set_website('https://github.com/abbarrasa/openbox')
        about_dialog.set_website_label('Project website')
        about_dialog.set_license(
            u"This program is free software; you can redistribute it and/or "
            u"modify it under the terms of the GNU General Public License as "
            u"published by the free Software Foundation, either version 3 of "
            u"the License, or (at your option) any later version.\n"
            u"\n"
            u"This program is distributed in the hope that it will be useful, "
            u"but WITHOUT ANY WARRANTY; without even the implied warranty of "
            u"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
            u"GNU General Public License for more details.\n"
            u"\n"
            u"You should have received a copy of the GNU General Public "
            u"License along with this program. If not, see "
            u"<http://www.gnu.org/licenses/>."
        )
        about_dialog.set_wrap_license(True)
        about_dialog.run()
        about_dialog.destroy()

    def update_menu(self):
        mysensors = self.sensors.get_sensors()
        for sensor in mysensors:
            label = '{0}: {1}'.format(
                mysensors[sensor]['label'], mysensors[sensor]['format'])
            setlabel = label % mysensors[sensor]['value']
            self.items[sensor].set_label(setlabel)

        return True

if __name__ == "__main__":
    pysensors.init()
    try:
        SystrayIcon()
        gtk.main()
    finally:
        pysensors.cleanup()
