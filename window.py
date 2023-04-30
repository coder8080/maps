from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import requests

MAP_FILENAME = 'map.png'
types = ['Схема', 'Спутник', 'Гибрид']
types_map = {'Схема': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}

postal_types = ['Показывать почтовый индекс', 'Скрывать почтовый индекс']
postal_types_map = {postal_types[0]: 'on', postal_types[1]: 'off'}


def get_lonlat(search: str, postal_code: bool = True):
    geocoder_apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
    url = f'https://geocode-maps.yandex.ru/1.x?geocode={search}&apikey={geocoder_apikey}&format=json'
    response = requests.get(url)
    json = response.json()
    pos = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    lon, lat = [float(el) for el in pos.split()]
    full_address = json['response']['GeoObjectCollection']['featureMember'][
        0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
    if postal_code == 'on':
        code = json['response']['GeoObjectCollection']['featureMember'][
            0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        full_address += ' ' + code
    return lon, lat, full_address


def download_image(lon: float, lat: float, point_lon: float, point_lat: float, spn: float, type: str):
    map_url = f'http://static-maps.yandex.ru/1.x/?ll={lon},{lat}&spn={spn},{spn}&l={type}'
    if point_lon is not None and point_lat is not None:
        map_url += f'&pt={point_lon},{point_lat},round'
    response = requests.get(map_url)
    with open(MAP_FILENAME, 'wb') as file:
        file.write(response.content)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./main.ui', self)
        self.spn = 0.02
        self.point_lon, self.point_lat, full_address = get_lonlat(
            'Москва')
        self.set_full_address(full_address)
        self.lon, self.lat = self.point_lon, self.point_lat
        self.search_text = 'Москва'

        self.type_box.clear()
        self.type_box.addItems(types)
        self.type_box.setCurrentIndex(0)
        self.type_box.currentTextChanged.connect(self.type_changed)

        self.postal_box.clear()
        self.postal_box.addItems(postal_types)
        self.postal_box.setCurrentIndex(0)
        self.postal_box.currentTextChanged.connect(self.postal_changed)

        self.update_map()
        self.search_button.clicked.connect(self.search)
        self.remove_button.clicked.connect(self.remove_point)

        self.postal_code = 'on'

    def update_map(self):
        type_name = self.type_box.currentText()
        type = types_map.get(type_name, 'map')
        download_image(self.lon, self.lat, self.point_lon,
                       self.point_lat, self.spn, type)
        pixmap = QPixmap(MAP_FILENAME)
        self.image_label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.spn += self.spn / 2
            self.update_map()
        elif event.key() == Qt.Key_PageDown:
            self.spn -= self.spn / 2
            self.spn = max(self.spn, 0.00001)
            self.update_map()
        elif event.key() == Qt.Key_Left:
            self.lon -= self.spn / 4
            self.update_map()
        elif event.key() == Qt.Key_Right:
            self.lon += self.spn / 4
            self.update_map()
        elif event.key() == Qt.Key_Up:
            self.lat += self.spn / 4
            self.update_map()
        elif event.key() == Qt.Key_Down:
            self.lat -= self.spn / 4
            self.update_map()

    def mousePressEvent(self, event):
        try:
            focused_widget = QApplication.focusWidget()
            focused_widget.clearFocus()
        except:
            # пофиг абсолютно
            pass

    def type_changed(self, event):
        self.update_map()

    def search(self, event):
        search_text = self.search_input.text().lower()
        try:
            lon, lat, full_address = get_lonlat(search_text, self.postal_code)
            self.set_full_address(full_address)
            self.search_text = search_text
            self.lon = lon
            self.lat = lat
            self.point_lon = lon
            self.point_lat = lat
            self.spn = 0.02
            self.update_map()
        except Exception:
            # по запросу ничего не нашлось
            pass

    def remove_point(self, event):
        self.point_lat = None
        self.point_lon = None
        self.update_map()
        self.set_full_address('')

    def set_full_address(self, full_address: str):
        self.address_label.setText(full_address)

    def postal_changed(self, event):
        postal_type_text = self.postal_box.currentText()
        self.postal_code = postal_types_map.get(postal_type_text, 'on')
        self.search(None)
