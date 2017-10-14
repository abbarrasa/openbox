#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# License: GPLv2
# Date: 12 Oct 2017
# Latest edit: 14 Oct 2017
# Website: https://github.com/abbarrasa/openbox
#
# A review of Weatherboy application to migrate to Qt5 and Python3.
#
# Weatherboy is a weather tray application written in Python, perfect
# for lightweight environments (like OpenBox, Awesome, etc.). More
# on <https://github.com/decayofmind/weatherboy>
#
# Example of use: python3 weatherboy-qt.py -l 22664159 -u c -d 30 -a

from PyQt5.QtCore import QSize, QTimer, Qt
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import (qApp, QApplication, QMainWindow,
    QSystemTrayIcon, QMenu, QAction, QDialog, QDialogButtonBox,
    QLabel, QTabWidget, QTextBrowser, QGridLayout, QHBoxLayout,
    QVBoxLayout)
from argparse import ArgumentParser
import urllib.request
import urllib.parse
import json
import webbrowser
import notify2
import base64
from decimal import Decimal
from datetime import datetime, time

# Yahoo! Weather YQL API
WEATHER_WEBSITE = 'https://www.yahoo.com/news/weather/country/state/city-%s'
PUBLIC_API_URL = 'http://query.yahooapis.com/v1/public/yql'
YQL_FORECAST_BY_WOEID = "select * from weather.forecast where woeid='%s' and u='%s'"

# Application version
VERSION = 1.1

# Icon name by Yahoo! Weather code
ICON_NAMES = {
    '0': 'weather-severe-alert',
    '1': 'weather-severe-alert',
    '2': 'weather-severe-alert',
    '3': 'weather-severe-alert',
    '4': 'weather-storm',
    '5': 'weather-snow-rain',
    '6': 'weather-snow-rain',
    '7': 'weather-snow',
    '8': 'weather-freezing-rain',
    '9': 'weather-fog',
    '10': 'weather-freezing-rain',
    '11': 'weather-showers',
    '12': 'weather-showers',
    '13': 'weather-snow',
    '14': 'weather-snow',
    '15': 'weather-snow',
    '16': 'weather-snow',
    '17': 'weather-snow',
    '18': 'weather-snow',
    '19': 'weather-fog',
    '20': 'weather-fog',
    '21': 'weather-fog',
    '22': 'weather-fog',
    '23': 'weather-few-clouds',
    '24': 'weather-few-clouds',
    '25': 'weather-few-clouds',
    '26': 'weather-overcast',
    '27': 'weather-clouds-night',
    '28': 'weather-clouds',
    '29': 'weather-few-clouds-night',
    '30': 'weather-few-clouds',
    '31': 'weather-clear-night',
    '32': 'weather-clear',
    '33': 'weather-clear-night',
    '34': 'weather-clear',
    '35': 'weather-snow-rain',
    '36': 'weather-clear',
    '37': 'weather-storm',
    '38': 'weather-storm',
    '39': 'weather-storm',
    '40': 'weather-showers-scattered',
    '41': 'weather-snow',
    '42': 'weather-snow',
    '43': 'weather-snow',
    '44': 'weather-few-clouds',
    '45': 'weather-storm',
    '46': 'weather-snow',
    '47': 'weather-storm',
    '3200': 'stock-unknown'
}


def parse_arguments():
    parser = ArgumentParser(description='Simple weather applet',
                            epilog='Free software under GPL license.'
                            'Please, report bugs and comments on https://github.com/abbarrasa/openbox')
    parser.add_argument('-l', '--location',
                        required=True,
                        metavar='WOEID',
                        help='location WOEID (more on https://developer.yahoo.com/weather/)')
    parser.add_argument('-u', '--units',
                        choices=['c', 'f'],
                        default='c',
                        metavar='c|f',
                        help='units to display')
    parser.add_argument('-d', '--delta',
                        default='10',
                        type=int,
                        metavar='N',
                        help='timeout in minutes between next weather data query')
    parser.add_argument('-a', '--advanced', action='store_true', default=False, help='Advanced tooltip')
    args = parser.parse_args()
    return args


class YahooAPI(object):
    def query(self, yql):
        try:
            url = PUBLIC_API_URL + '?' + urllib.parse.urlencode({'q': yql, 'format': 'json'})
            response = urllib.request.urlopen(url).read()
            data = json.loads(response.decode('utf-8'))
            return data
        except:
            raise Exception("Connection error!")


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        QSystemTrayIcon.__init__(self, QIcon.fromTheme('stock-dialog-question'), parent)

        # Notification
        notify2.init('weather-qt')

        # Menu actions
        refresh_action = QAction(self.tr('&Refresh'), self)
        refresh_action.triggered.connect(parent.on_refresh)
        overview_action = QAction(self.tr('&Show overview'), self)
        overview_action.triggered.connect(parent.on_show_overview)
        open_action = QAction(self.tr('&Open website'), self)
        open_action.triggered.connect(parent.on_open_website)
        about_action = QAction(self.tr('&About'), self)
        about_action.triggered.connect(parent.on_about)
        quit_action = QAction(self.tr('&Exit'), self)
        quit_action.triggered.connect(parent.on_quit)

        traymenu = QMenu()
        traymenu.addAction(refresh_action)
        traymenu.addAction(overview_action)
        traymenu.addSeparator()
        traymenu.addAction(open_action)
        traymenu.addSeparator()
        traymenu.addAction(about_action)
        traymenu.addAction(quit_action)

        self.setContextMenu(traymenu)
        self.activated.connect(parent.on_show_overview)
        self.show()

    def update(self, data):
        icon = QIcon.fromTheme(data['current']['icon'])
        tooltip_text = '{0} ({1}) in {2}, {3}'.format(data['current']['temp'], data['current']['text'], data['location']['city'], data['location']['country'])
        self.setIcon(icon)
        self.setToolTip(tooltip_text)

    def error(self, e):
        msg = str(e)
        self.setIcon(QIcon.fromTheme('stock-dialog-error'))
        self.setToolTip(msg)

        n = notify2.Notification('Weatherboy-Qt error!', msg, 'stock-dialog-error')
        n.show()


class MainApp(QMainWindow):
    def __init__(self, args, parent=None):
        super(MainApp, self).__init__(parent)

        self.args = args
        self.api = YahooAPI()
        self.trayicon = SystemTrayIcon(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()

    def on_refresh(self, widget):
        self.refresh()

    def on_open_website(self, widget):
        url = WEATHER_WEBSITE % self.args.location
        webbrowser.open(url)

    def on_quit(self, widget):
        qApp.quit()

    def on_show_overview(self, widget):
        print("Opening a new popup window...")
        try:
            data = self.get_data()

            dialog = QDialog(self)
            dialog.setWindowTitle('Weather status')
            dialog.setGeometry(300, 300, 640, 480)
            dialog.setWindowIcon(QIcon.fromTheme('help-about'))

            conditionsLayout = QVBoxLayout()
            weatherLabel = QLabel('<font size="4"><b>{0} ({1})</b></font>'.format(data['current']['temp'], data['current']['text']))
            windLabel = QLabel('<font size="2"><b>Wind:</b> {0} {1}</font>'.format(data['extra']['wind']['speed'], data['extra']['wind']['direction']))
            humidityLabel = QLabel('<font size="2"><b>Humidity:</b> {0}</font>'.format(data['extra']['atmosphere']['humidity']))
            visibilityLabel = QLabel('<font size="2"><b>Visibility:</b> {0}</font>'.format(data['extra']['atmosphere']['visibility']))
            pressureLabel = QLabel('<font size="2"><b>Pressure:</b> {0}</font>'.format(data['extra']['atmosphere']['pressure']))
            sunriseLabel = QLabel('<font size="2"><b>Sunrise:</b> {0}</font>'.format(data['extra']['astronomy']['sunrise']))
            sunsetLabel = QLabel('<font size="2"><b>Sunset:</b> {0}</font>'.format(data['extra']['astronomy']['sunset']))
            conditionsLayout.addWidget(weatherLabel)
            conditionsLayout.addWidget(windLabel)
            conditionsLayout.addWidget(humidityLabel)
            conditionsLayout.addWidget(visibilityLabel)
            conditionsLayout.addWidget(pressureLabel)
            conditionsLayout.addWidget(sunriseLabel)
            conditionsLayout.addWidget(sunsetLabel)

            icon = QIcon.fromTheme(data['current']['icon'])
            pixmap = icon.pixmap(QSize(128, 128))
            iconLabel = QLabel()
            iconLabel.setPixmap(pixmap)

            todayLayout = QHBoxLayout()
            todayLayout.addWidget(iconLabel)
            todayLayout.addLayout(conditionsLayout)

            cityLabel = QLabel('<font size="5"><b>{0}, {1}</b></font>'.format(data['location']['city'], data['location']['country']))

            overviewLayout = QVBoxLayout()
            overviewLayout.setAlignment(Qt.AlignHCenter)
            overviewLayout.setContentsMargins(0, 0, 0, 20)
            overviewLayout.addWidget(cityLabel)
            overviewLayout.addLayout(todayLayout)

            forecastLayout = QGridLayout()
            forecastLayout.setContentsMargins(0, 0, 0, 20)
            column = 0
            for item in data['forecast']:
                dateforecastLayout = QVBoxLayout()
                icon = QIcon.fromTheme(ICON_NAMES.get(item['code']))
                pixmap = icon.pixmap(QSize(48, 48))
                iconLabel = QLabel()
                iconLabel.setAlignment(Qt.AlignCenter)
                iconLabel.setPixmap(pixmap)
                dateLable = QLabel('<font size="2"><b>{0}, {1}</b></font>'.format(item['day'], item['date']))
                textLable = QLabel('<font size="2">{0}</font>'.format(item['text']))
                highLable = QLabel(u'<font size="2"><b>Max:</b> {0}\u00B0 {1}</font>'.format(item['high'], data['units']['temperature']))
                lowLable = QLabel(u'<font size="2"><b>Min:</b> {0}\u00B0 {1}</font>'.format(item['low'], data['units']['temperature']))
                dateforecastLayout.addWidget(iconLabel)
                dateforecastLayout.addWidget(dateLable)
                dateforecastLayout.addWidget(textLable)
                dateforecastLayout.addWidget(highLable)
                dateforecastLayout.addWidget(lowLable)
                if column < 5:
                    row = 0
                else:
                    row = 1
                forecastLayout.addLayout(dateforecastLayout, row, column % 5)
                column = column + 1

            lastupdateLabel = QLabel('<small><i>Last update at: {0}</i></small>'.format(data['timestamp']))

            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, Qt.Horizontal, dialog)
            buttonBox.accepted.connect(dialog.accept)

            layout = QVBoxLayout()
            layout.addLayout(overviewLayout)
            layout.addLayout(forecastLayout)
            layout.addWidget(lastupdateLabel)
            layout.addWidget(buttonBox)
            dialog.setLayout(layout)

            dialog.show()
        except Exception as e:
            print(str(e))
            self.trayicon.error(e)

    def on_about(self, widget):
        dialog = QDialog(self)
        aboutText = self.tr("""<p>A simple weather information applet.</p>
            <p>Website: <a href="https://github.com/abbarrasa/openbox">
            https://github.com/abbarrasa/openbox</a></p>
            <p>Data source: <a href="https://www.yahoo.com/news/weather">
            Yahoo! News</a>.</p>
            <p>Based in <a href="https://github.com/decayofmind/weatherboy">Weatherboy</a>.</p>
            <p>If you want to report a dysfunction or a suggestion,
            feel free to open an issue in <a href="https://github.com/abbarrasa/openbox/issues">
            github</a>.""")
        creditsText = self.tr("""(c) 2017 Alberto Buitrago <%s>""") % base64.b64decode('YWJiYXJyYXNhQGdtYWlsLmNvbQ==').decode('utf-8')
        licenseText = self.tr("""<p>This program is free software; you can
            redistribute it and/or modify it under the terms of the GNU
            General Public License as published by the free Software
            Foundation, either version 2 of the License, or (at your option)
            any later version.</p>
            <p>This program is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
            General Public License for more details.</p>
            <p>You should have received a copy of the GNU General Public
            License along with this program. If not, see
            <a href="http://www.gnu.org/licenses/gpl-2.0.html">GNU General Public
            License version 2</a>.</p>""")

        layout = QVBoxLayout()
        titleLayout = QHBoxLayout()
        titleLabel = QLabel('<font size="4"><b>{0} {1}</b></font>'.format('Weatherboy-qt', VERSION))

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

        icon = QIcon.fromTheme('indicator-weather')
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
        dialog.setWindowTitle(self.tr('About Weatherboy-qt'))
        dialog.setWindowIcon(QIcon.fromTheme('help-about'))

        dialog.show()

    def get_data(self):
        yql = YQL_FORECAST_BY_WOEID % (self.args.location, self.args.units)
        data = self.api.query(yql)
        units = data['query']['results']['channel']['units']
        location = data['query']['results']['channel']['location']
        condition = data['query']['results']['channel']['item']['condition']
        wind = data['query']['results']['channel']['wind']
        atmosphere = data['query']['results']['channel']['atmosphere']
        astronomy = data['query']['results']['channel']['astronomy']
        forecast = data['query']['results']['channel']['item']['forecast']

        return {
            'current': {
                'code': condition['code'],
                'icon': ICON_NAMES.get(condition['code']),
                'text': condition['text'],
                'temp': u'{0}\u00B0 {1}'.format(condition['temp'], units['temperature']),
            },
            'extra': {
                'wind': {
                    'direction': self.conv_direction(wind['direction']),
                    'speed': '{0} {1}'.format(wind['speed'], units['speed'])
                },
                'atmosphere': {
                    'humidity': '{0}%'.format(atmosphere['humidity']),
                    'visibility': '{0} {1}'.format(atmosphere['visibility'], units['distance']),
                    'pressure': '{0} {1}'.format(atmosphere['pressure'], units['pressure'])
                },
                'astronomy': {
                    'sunrise': u'{0:%R} \u2600 '.format(self.to_time(astronomy['sunrise'])),
                    'sunset': u'{0:%R} \u263E '.format(self.to_time(astronomy['sunset']))
                }
            },
            'forecast': forecast,
            'location': {
                'city': location['city'],
                'country': location['country']
            },
            'timestamp': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            'units': units
        }

    def refresh(self):
        try:
            data = self.get_data()
            print('----------------- {0} ---------------'.format(datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
            print(data)
            self.trayicon.update(data)
            self.timer.start(self.args.delta * 60 * 1000)

        except Exception as e:
            print(str(e))
            self.trayicon.error(e)

    def conv_direction(self, value):
        value = Decimal(value)
        if 0 <= value < 22.5:
            return u'\u2193 (N)'
        elif 22.5 <= value < 67.5:
            return u'\u2199 (NE)'
        elif 67.5 <= value < 112.5:
            return u'\u2190 (E)'
        elif 112.5 <= value < 157.5:
            return u'\u2196 (SE)'
        elif 157.5 <= value < 202.5:
            return u'\u2191 (S)'
        elif 202.5 <= value < 247.5:
            return u'\u2197 (SW)'
        elif 247.5 <= value < 292.5:
            return u'\u2192 (W)'
        elif 292.5 <= value < 337.5:
            return u'\u2198 (NW)'
        else:
            return u'\u2193 (N)'

    def to_time(self, value):
        t, p = value.split(' ')
        h, m = map(int, t.split(':'))
        if p.lower() == 'pm':
            h += 12
        return time(h, m)


if __name__ == "__main__":
    import sys
    try:
        args = parse_arguments()
        app = QApplication(sys.argv)
        QApplication.setQuitOnLastWindowClosed(False)

        trayIcon = MainApp(args)

        app.exec_()
    except KeyboardInterrupt:
        pass
