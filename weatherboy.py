#!/usr/bin/env python2
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
# Date: 13 May 2016
# Latest edit: 20 Sep 2016
# Website: https://github.com/abbarrasa/openbox
#
# A review of Weatherboy to integrate this application with the new
# Yahoo! Weather API.
#
# Weatherboy is a weather tray application written in Python, perfect
# for lightweight environments (like OpenBox, Awesome, etc.). More
# on <https://github.com/decayofmind/weatherboy>
#
# Example of use: python weatherboy.py -l 22664159 -u c -d 30 -a

from argparse import ArgumentParser
import gobject
import gtk
import json
import urllib
import urllib2
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
    def __init__(self):
        self.website = WEATHER_WEBSITE
        
    def yql_query(self, yql):
        try:
            url = PUBLIC_API_URL + '?' + urllib.urlencode({'q': yql, 'format': 'json'})
            response = urllib2.urlopen(url).read()
            data = json.loads(response)
            return data	
        except:
            raise Exception("Connection error!")

	  
class MainApp:
    def __init__(self, args):
        self.args = args
        self.weather = None
        self.tooltip = None
        self.tray = gtk.StatusIcon()
        self.tray.connect('popup-menu', self.on_right_click)
        self.tray.connect('activate', self.on_left_click)
        self.tray.set_has_tooltip(True)
        self.tray.connect('query-tooltip', self.on_tooltip_advanced)	
        self.api = YahooAPI()
        self.timer_id = -1
        self.update_tray()
        self.set_timer()	

    def get_data(self):
        yql = YQL_FORECAST_BY_WOEID % (self.args.location, self.args.units)
        data = self.api.yql_query(yql)
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
                    'sunrise': u'\u2600 {0:%R}'.format(self.to_time(astronomy['sunrise'])),
                    'sunset': u'\u263E {0:%R}'.format(self.to_time(astronomy['sunset']))                    
                }
            },
            'forecast': forecast,
            'location': {
                'city': location['city'],
                'country': location['country']
            },
            'timeStamp': datetime.today().strftime('%Y-%m-%d %H:%M')
        }		

    def update_tray(self):
        try:
            self.weather = self.get_data()
            self.tray.set_from_icon_name(self.weather['current']['icon'])
        except Exception as e:
            self.tray.set_tooltip_text(str(e))
            self.tray.set_from_stock('gtk-dialog-error')
	  
        return True	
	
    def on_refresh(self, widget):
        self.update_tray()
        self.set_timer()

    def on_right_click(self, icon, event_button, event_time):
        menu = gtk.Menu()
        refresh = gtk.MenuItem('Refresh')
        refresh.show()
        refresh.connect('activate', self.on_refresh)
        quit = gtk.MenuItem('Quit')
        quit.show()
        quit.connect('activate', gtk.main_quit)
        menu.append(refresh)
        menu.append(quit)
        menu.popup(None, None, gtk.status_icon_position_menu,
                   event_button, event_time, self.tray)

    def on_left_click(self, widget):
        webbrowser.open(self.api.website)

    def set_timer(self):
        self.remove_timer()
        self.timer_id = gobject.timeout_add_seconds(self.args.delta * 60, self.update_tray)

    def remove_timer(self):
        if self.timer_id > 0:
            gobject.source_remove(self.timer_id)
            self.timer_id = -1	
			
    def on_tooltip_advanced(self, widget, x, y, keyboard_mode, tooltip):
        if not self.args.advanced:
            tooltip_text = '{0} / {1}'.format(self.weather['current_temp'], self.weather['current_condition'])
            tooltip.set_tooltip_markup(tooltip_text)
        else:
            tooltip_text = '{0}\n{1}'.format(self.weather['current']['temp'], self.weather['current']['text'])		
            vbox = gtk.VBox()
            header = gtk.Label()
            header.set_markup(
                              '<span size="12000"><b>{0}, {1}</b></span>'.format(self.weather['location']['city'], self.weather['location']['country']))
            header.set_alignment(0.9, 0.5)
            footer = gtk.Label()
            footer.set_markup('<small><i>Last checked: {0}</i></small>'.format(self.weather['timeStamp']))
            hbox = gtk.HBox()
            now_icon = self.get_image_by_icon(self.weather['current']['icon'])
            now_label = gtk.Label()
            now_label.set_markup('<b>{0}</b>'.format(tooltip_text))
            now_label.set_padding(5, 5)
            table = gtk.Table(columns=2, homogeneous=False)
            u = 0
            l = 1
            for k, v in self.weather['extra'].items():
                h_label = gtk.Label()
                h_label.set_markup('<b>{0}</b>'.format(k))
                h_label.set_alignment(0.0, 0.5)
                h_label.set_padding(5, 5)
                table.attach(h_label, 0, 1, u, l)
                for i, j in sorted(v.items()):
                    u += 1
                    l += 1
                    k_label = gtk.Label(i)
                    k_label.set_alignment(0.0, 0.5)
                    v_label = gtk.Label(j)
                    v_label.set_alignment(0.0, 0.5)
                    table.attach(k_label, 0, 1, u, l)
                    table.attach(v_label, 1, 2, u, l)
                    u += 1
                    l += 1

            hbox.pack_start(now_icon, False, False, 0)
            hbox.pack_start(now_label, False, False, 0)
            vbox.pack_start(header, True, False, 0)
            vbox.pack_start(hbox, False, False, 0)
            vbox.pack_start(table, False, False, 0)
            vbox.pack_start(gtk.HSeparator(), False, False, 5)            
            vbox.pack_start(footer, False, False, 3)
            vbox.show_all()
            tooltip.set_custom(vbox)
		
            return True
	
    def get_image_by_icon(self, icon):
        image = gtk.Image()
        image.set_padding(0, 5)
        image.set_pixel_size(48)
        image.set_from_icon_name(icon, 48)
        return image
	  
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

    def  to_time(self, value):
        t, p = value.split(' ')
        h, m = map(int, t.split(':'))
        if p.lower() == 'pm':
            h +=12
        return time(h, m)
	

if __name__ == "__main__":
    try:
        args = parse_arguments()
        MainApp(args)
        gtk.main()
    except KeyboardInterrupt:
        pass
	
