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
# Date: 13 Oct 2017
# Latest edit: 12 Oct 2017
# Website: https://github.com/abbarrasa/openbox
#
# A review of Weatherboy to migrate this application to QT5 and
# Python3.
#
# Weatherboy is a weather tray application written in Python, perfect
# for lightweight environments (like OpenBox, Awesome, etc.). More
# on <https://github.com/decayofmind/weatherboy>
#
# Example of use: python3 weatherboy-qt.py -l 751846 -u c -d 30 -a

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSystemTrayIcon, QGridLayout, QMenu, QAction, QStyle, qApp, QLabel, QLineEdit, QPushButton, QDialog, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout
from argparse import ArgumentParser
import urllib.request
import urllib.parse
import json
import webbrowser
from decimal import Decimal
from datetime import datetime, time

# Yahoo! Weather YQL API
WEATHER_WEBSITE = 'https://www.yahoo.com/news/weather'
PUBLIC_API_URL  = 'http://query.yahooapis.com/v1/public/yql'
YQL_FORECAST_BY_WOEID = "select * from weather.forecast where woeid='%s' and u='%s'"

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
        QSystemTrayIcon.__init__(self, QtGui.QIcon.fromTheme("guake"), parent)

        # Menu actions
        refresh_action = QAction(self.tr('&Refresh'), self)
        refresh_action.triggered.connect(parent.on_refresh)
        overview_action = QAction(self.tr('&Show overview'), self)
        overview_action.triggered.connect(parent.on_show_overview)
        open_action = QAction(self.tr('&Open website'), self)
        open_action.triggered.connect(parent.on_open_website)
        quit_action = QAction(self.tr('&Exit'), self)
        quit_action.triggered.connect(parent.on_quit)

        traymenu = QMenu()
        traymenu.addAction(refresh_action)
        traymenu.addAction(overview_action)
        traymenu.addAction(open_action)
        traymenu.addAction(quit_action)        

        self.setContextMenu(traymenu)
        self.activated.connect(parent.on_show_overview)
        self.show()

    def update(self, data):
        icon = QtGui.QIcon.fromTheme(data['current']['icon'])
#        pixmap = icon.pixmap(22, 22)
#        pt = QtGui.QPainter(pixmap)
#        font = QtGui.QFont('Ubuntu', 9)
#        font.setStyle(QtGui.QFont.StyleNormal)
#        font.setWeight(QtGui.QFont.Bold)
#        pt.setFont(font)
#        pt.setRenderHint(QtGui.QPainter.Antialiasing)
#        pt.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, str(data['current']['temp']))
#        pt.end()
#        self.setIcon(QtGui.QIcon(pixmap))
        tooltip_text = '{0} / {1}'.format(data['current']['temp'], data['current']['text'])
        self.setIcon(icon)
        self.setToolTip(tooltip_text)

class MainApp(QMainWindow):
    def __init__(self, args, parent=None):
        super(MainApp, self).__init__(parent)

        self.args = args
        self.api = YahooAPI()
        self.trayicon = SystemTrayIcon(self)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()

    def on_refresh(self, widget):
        self.refresh()

    def on_open_website(self, widget):
        webbrowser.open(WEATHER_WEBSITE)

    def on_quit(self, widget):
        qApp.quit()

    def on_show_overview(self, widget):
        print("Opening a new popup window...")
        try:
            data = self.get_data()

            dialog = QDialog(self)
            dialog.setWindowTitle('Weather status')
            dialog.setGeometry(300, 300, 640, 480)

            icon = QtGui.QIcon.fromTheme(data['current']['icon'])
            pixmap = icon.pixmap(128, 128)
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)

            conditions_layout = QVBoxLayout()
            weather = QLabel('<font size="4"><b>{0} / {1}</b></font>'.format(data['current']['temp'], data['current']['text']))
            wind = QLabel('<font size="2"><b>Wind:</b> {0} {1}</font>'.format(data['extra']['wind']['speed'], data['extra']['wind']['direction']))
            humidity = QLabel('<font size="2"><b>Humidity:</b> {0}</font>'.format(data['extra']['atmosphere']['humidity']))
            visibility = QLabel('<font size="2"><b>Visibility:</b> {0}</font>'.format(data['extra']['atmosphere']['visibility']))
            pressure = QLabel('<font size="2"><b>Pressure:</b> {0}</font>'.format(data['extra']['atmosphere']['pressure']))
            sunrise = QLabel('<font size="2"><b>Sunrise:</b> {0}</font>'.format(data['extra']['astronomy']['sunrise']))
            sunset = QLabel('<font size="2"><b>Sunset:</b> {0}</font>'.format(data['extra']['astronomy']['sunset']))
            conditions_layout.addWidget(weather)
            conditions_layout.addWidget(wind)
            conditions_layout.addWidget(humidity)
            conditions_layout.addWidget(visibility)
            conditions_layout.addWidget(pressure)
            conditions_layout.addWidget(sunrise)
            conditions_layout.addWidget(sunset)
            conditions_layout.addStretch()

            today_layout = QHBoxLayout()
            today_layout.addWidget(icon_label)
            today_layout.addLayout(conditions_layout)

            forecast_layout = QGridLayout()
            column = 0
            for item in data['forecast']:
                dateforecast_layout = QVBoxLayout()
                icon = QtGui.QIcon.fromTheme(ICON_NAMES.get(item['code']))
                pixmap = icon.pixmap(48, 48)
                icon_label = QLabel()
                icon_label.setPixmap(pixmap)                
                date = QLabel('<font size="2"><b>{0}, {1}</b></font>'.format(item['day'], item['date']))
                text = QLabel('<font size="2">{0}</font>'.format(item['text']))
                high = QLabel(u'<font size="2"><b>Max:</b> {0}\u00B0 {1}</font>'.format(item['high'], data['units']['temperature']))
                low = QLabel(u'<font size="2"><b>Min:</b> {0}\u00B0 {1}</font>'.format(item['low'], data['units']['temperature']))
                dateforecast_layout.addWidget(icon_label)
                dateforecast_layout.addWidget(date)
                dateforecast_layout.addWidget(text)
                dateforecast_layout.addWidget(high)
                dateforecast_layout.addWidget(low)
                dateforecast_layout.addStretch()
                if column < 5:
                    row = 0
                else:
                    row = 1
                forecast_layout.addLayout(dateforecast_layout, row, column % 5)
                column = column + 1

            city_label = QLabel('<font size="5"><b>{0}, {1}</b></font>'.format(data['location']['city'], data['location']['country']))
            lastchecked_label = QLabel('<small><i>Last checked at: {0}</i></small>'.format(data['timestamp']))

            layout = QVBoxLayout()
            layout.addWidget(city_label)
            layout.addLayout(today_layout)
            layout.addLayout(forecast_layout)
            layout.addWidget(lastchecked_label)
            dialog.setLayout(layout)

            dialog.show()
        except Exception as e:
            print(str(e))
            self.trayicon.setToolTip(str(e))

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
            self.trayicon.setToolTip(str(e))

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
