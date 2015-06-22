#!/usr/bin/python2
#
# Copyright (C) 2015 Alberto Buitrago <echo YWJiYXJyYXNhQGdtYWlsLmNvbQo= | base64 -d>
#
# This program is free software: you can redistribute it and/or modify
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
# Latest edit: 22 June 2015
# Website: https://github.com/abbarrasa/openbox
#
# A small script to put a logout icon in system tray.
# Based in: <http://crunchbang.com/forums/viewtopic.php?pid=132886>

import gtk
import os


class SystrayIcon:
    def __init__(self):
        self.tray = gtk.StatusIcon()
        self.tray.set_from_stock(gtk.STOCK_QUIT)
        self.tray.set_tooltip('Logout TrayIcon')
        self.tray.connect('activate', self.on_activate)
        self.tray.connect('popup-menu', self.on_popup_menu)

    def on_activate(self, data):
        os.system('oblogout')

    def on_popup_menu(self, status, event_button, event_time):
        menu = gtk.Menu()

        menuitem_about = gtk.MenuItem("About")
        menu.append(menuitem_about)
        menuitem_about.connect(
                "activate", lambda w: self.on_about(self))

        menuitem_quit = gtk.MenuItem("Quit")
        menu.append(menuitem_quit)
        menuitem_quit.connect("activate", lambda w: gtk.main_quit())

        menu.show_all()
        menu.popup(None, None, None, event_button, event_time, self.tray)

    def on_about(self, data):
        dialog = gtk.AboutDialog()
        dialog.set_name('Logout TrayIcon')
        dialog.set_version('0.1')
        dialog.set_comments('A systray logout icon for Openbox desktop')
        dialog.set_website('https://github.com/abbarrasa/openbox')
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    SystrayIcon()
    gtk.main()
