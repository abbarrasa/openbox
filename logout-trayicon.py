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
# A small script to put a logout icon in system tray.
# Based in: <http://crunchbang.com/forums/viewtopic.php?pid=132886>

import gtk
import os
import base64

from gtk import gdk


class SystrayIcon:
    def __init__(self):
        self._APPNAME = 'Logout TrayIcon'
        self._VERSION = '0.3'

        self.tray = gtk.StatusIcon()
        self.tray.set_from_stock(gtk.STOCK_QUIT)
        self.tray.set_tooltip(self._APPNAME)
        self.tray.connect('activate', self.on_activate)
        self.tray.connect('popup-menu', self.on_popup_menu)

    def on_activate(self, status_icon):
        os.system('oblogout')

    def on_popup_menu(self, status_icon, event_button, event_time):
        menu = gtk.Menu()

        # add item to show about dialog
        item_about = gtk.MenuItem('About')
        menu.append(item_about)
        item_about.connect(
                'activate', lambda w: self.show_about_dialog())

        # add quit item
        item_quit = gtk.MenuItem('Quit')
        menu.append(item_quit)
        item_quit.connect('activate', lambda w: gtk.main_quit())

        menu.show_all()
        menu.popup(None, None, None, event_button, event_time, self.tray)

    def show_about_dialog(self):
        about_dialog = gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_program_name(self._APPNAME)
        about_dialog.set_logo(
            gdk.pixbuf_new_from_file(
                gtk.icon_theme_get_default().lookup_icon(
                    'system-shutdown', 48, 0).get_filename()))
        about_dialog.set_icon(
            about_dialog.render_icon(
                gtk.STOCK_ABOUT, gtk.ICON_SIZE_SMALL_TOOLBAR))
        about_dialog.set_version(self._VERSION)
        about_dialog.set_copyright("Copyright \xc2\xa9 2015 Alberto Buitrago")
        about_dialog.set_comments("A systray logout icon for Openbox desktop")
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

if __name__ == "__main__":
    SystrayIcon()
    gtk.main()
