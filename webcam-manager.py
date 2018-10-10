#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# License: GPLv3
# Date: 9 Oct 2018
# Latest edit: 10 Oct 2018
# Website: https://github.com/abbarrasa/openbox
#
# A system tray icon application written in Python and Qt5 used to
# enable/disable webcams.
#
# Based in https://extensions.gnome.org/extension/1477/webcam-manager/

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import (qApp, QApplication, QMainWindow,
    QSystemTrayIcon, QMenu, QAction, QDialog, QDialogButtonBox,
    QLabel, QTabWidget, QTextBrowser, QHBoxLayout, QVBoxLayout)
import notify2
import base64
import subprocess
import distutils.spawn


# Application version
VERSION = 1.1

class MainApp(QMainWindow):
    tray_icon = None
    active = False

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)

        # Init notification
        notify2.init('webcam-manager')
        
        # Init tray icon
        self.tray_icon = QSystemTrayIcon(QIcon.fromTheme('camera-web'), parent)        
        self.initTrayIcon()
        self.tray_icon.show()        
        
    def initTrayIcon(self):
        # Menu actions
        toogle_action = QAction(self.tr('&Toogle'), self)
        toogle_action.triggered.connect(self.onToogle)
        about_action = QAction(self.tr('&About'), self)
        about_action.setIcon(QIcon.fromTheme("help-about"))
        about_action.triggered.connect(self.onAbout)
        quit_action = QAction(self.tr('&Exit'), self)
        quit_action.setIcon(QIcon.fromTheme("application-exit"))
        quit_action.triggered.connect(self.onQuit)

        tray_menu = QMenu()
        tray_menu.addAction(toogle_action)
        tray_menu.addSeparator()
        tray_menu.addAction(about_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.onToogle)   
        output = int(self.execCommand('lsmod | grep uvcvideo | wc -l').split()[0])
        if output > 0:
            self.updateTrayIcon(True)
        else:
            self.updateTrayIcon(False)        

    def onToogle(self, widget):
        if self.active:
            self.disable()
        else:
            self.enable()

    def onQuit(self, widget):
        qApp.quit()

    def onAbout(self, widget):
        dialog = QDialog(self)
        aboutText = self.tr("""<p>A simple applet for enable/disable webcams.</p>
            <p>Website: <a href="https://github.com/abbarrasa/openbox">
            https://github.com/abbarrasa/openbox</a></p>
            <p>Based in <a href="https://extensions.gnome.org/extension/1477/webcam-manager/">Webcam Manager</a>.</p>
            <p>If you want to report a dysfunction or a suggestion,
            feel free to open an issue in <a href="https://github.com/abbarrasa/openbox/issues">
            github</a>.""")
        creditsText = self.tr("""(c) 2018 Alberto Buitrago <%s>""") % base64.b64decode('YWJiYXJyYXNhQGdtYWlsLmNvbQ==').decode('utf-8')
        licenseText = self.tr("""<p>This program is free software: you
            can redistribute it and/or modify it under the terms of the
            GNU General Public License as published by the Free Software
            Foundation, either version 3 of the License, or (at your
            option) any later version.</p>
            <p>This program is distributed in the hope that it will be
            useful, but WITHOUT ANY WARRANTY; without even the implied
            warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
            PURPOSE. See the GNU General Public License for more
            details.</p>
            <p>You should have received a copy of the GNU General Public
            License along with this program. If not, see
            <a href="https://www.gnu.org/licenses/gpl-3.0.html">
            GNU General Public License version 3</a>.</p>""")
        layout = QVBoxLayout()
        titleLayout = QHBoxLayout()
        titleLabel = QLabel('<font size="4"><b>{0} {1}</b></font>'.format('Webcam Manager', VERSION))

        contentsLayout = QHBoxLayout()
        aboutBrowser = QTextBrowser()
        aboutBrowser.append(aboutText)
        aboutBrowser.setOpenExternalLinks(True)

        creditsBrowser = QTextBrowser()
        creditsBrowser.append(creditsText)
        creditsBrowser.setOpenExternalLinks(True)

        licenseBrowser = QTextBrowser()
        licenseBrowser.append(licenseText)
        licenseBrowser.setOpenExternalLinks(True)

        TabWidget = QTabWidget()
        TabWidget.addTab(aboutBrowser, self.tr('About'))
        TabWidget.addTab(creditsBrowser, self.tr('Contributors'))
        TabWidget.addTab(licenseBrowser, self.tr('License'))

        aboutBrowser.moveCursor(QTextCursor.Start)
        creditsBrowser.moveCursor(QTextCursor.Start)
        licenseBrowser.moveCursor(QTextCursor.Start)

        icon = QIcon.fromTheme('camera-web')
        pixmap = icon.pixmap(QSize(64, 64))
        imageLabel = QLabel()
        imageLabel.setPixmap(pixmap)
        titleLayout.addWidget(imageLabel)
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()
        contentsLayout.addWidget(TabWidget)
        buttonLayout = QHBoxLayout()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonLayout.addWidget(buttonBox)
        layout.addLayout(titleLayout)
        layout.addLayout(contentsLayout)
        layout.addLayout(buttonLayout)
        buttonBox.clicked.connect(dialog.accept)

        dialog.setLayout(layout)
        dialog.setMinimumSize(QSize(480, 400))
        dialog.setWindowTitle(self.tr('About Webcam Manager'))
        dialog.setWindowIcon(QIcon.fromTheme('help-about'))

        dialog.show()
        
    def enable(self):
        tool = self.getGUISudo()
        cmd = '%s modprobe -a uvcvideo' % tool
        self.execCommand(cmd)
        output = int(self.execCommand('lsmod | grep uvcvideo | wc -l').split()[0])
        if output > 0:
            self.updateTrayIcon(True)
            self.showNotification('Webcam enabled!', 'Webcam is turned on and ready to use')
        
    def disable(self):
        tool = self.getGUISudo()
        cmd = '%s modprobe -r uvcvideo' % tool
        self.execCommand(cmd)
        output = int(self.execCommand('lsmod | grep uvcvideo | wc -l').split()[0])
        if output == 0:
            self.updateTrayIcon(False)
            self.showNotification('Webcam disabled!', 'Webcam is turned off')
        
    def getGUISudo(self):
        tools = ['kdesu', 'lxqt-sudo', 'gksu', 'gksudo', 'pkexec', 'sudo']
        for tool in tools:
            if distutils.spawn.find_executable(tool) is not None:
                return tool
                
    def execCommand(self, cmd):
        try:
            output = subprocess.check_output(cmd, shell=True)
            return output
        except subprocess.CalledProcessError as e:
            self.showNotification('Error!', e.output)
            
    def updateTrayIcon(self, active):
        self.active = active
        if self.active:
            self.tray_icon.setIcon(QIcon.fromTheme('camera-on'))
            self.tray_icon.setToolTip('Webcam is enabled')
        else:
            self.tray_icon.setIcon(QIcon.fromTheme('camera-off'))
            self.tray_icon.setToolTip('Webcam is disabled')            
            
    def showNotification(self, title, message):
        n = notify2.Notification(title, message, 'camera-web')
        n.show()
                


if __name__ == "__main__":
    import sys
    try:
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)      
        mw = MainApp()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        pass
   
