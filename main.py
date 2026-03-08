# А если ты хочешь картинку ВНУТРИ самого блокнота (на фоне или кнопке)?
# Тогда схема такая:
# Создаешь в репозитории папку, например, data.
# Кидаешь туда свою картинку (например, bg.png).
# В buildozer.spec находишь строку source.include_exts и проверяешь, чтобы там было написано png (через запятую).
# В коде Python путь будет: source = "data/bg.png"

# 1. Куда класть?
# Создаешь в своем репозитории папку data и закидываешь туда все свои fon.png, button.png и прочее.
# 2. Нужно ли указывать путь в buildozer.spec?
# НЕТ! В этом и есть магия. Твой Buildozer настроен так:
# source.dir = . (брать всё из текущей папки).
# Поскольку папка data лежит внутри, он увидит её, заглянет внутрь, найдет там файлы .png (которые ты разрешил через запятую) и целиком заберет всю папку в твой APK. 📦🚀
# 3. Как вызвать картинку в коде Python? 🐍
# Вот тут внимание! Теперь ты должен указывать путь относительно твоего main.py:
# python
# # Если картинка просто в корне:
# source = "icon.png"

# # Если картинка в папке data:
# source = "data/icon.png"
# Используйте код с осторожностью.

# Чтобы твой Android 13 точно не потерял путь (иногда системы капризничают с косой чертой /), лучше писать путь вот так:
# python
# import os
# # Получаем путь к папке, где лежит сам скрипт
# base_path = os.path.dirname(__file__)
# # Соединяем его с папкой data и файлом
# image_path = os.path.join(base_path, "data", "icon.png")

# # И используем в кнопке:
# btn = Button(background_normal=image_path)


# Когда стоит делать «чистую» пересборку?
# Иногда бывает, что ты поменял картинку или иконку, а в приложении она осталась старой. В Buildozer для этого используют команду полной очистки перед запуском:
# bash
# buildozer android clean
# buildozer android debug
import os
from kivy.app import App
import sqlite3, os, sys
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import Color, RoundedRectangle


def resource_path(relative_path):
    """Получает абсолютный путь к ресурсам (нужно для PyInstaller --onefile)"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


if getattr(sys, "frozen", False):
    # Если это EXE
    basedir = os.path.dirname(sys.executable)
else:
    # Если это обычный запуск .py
    basedir = os.path.dirname(os.path.abspath(__file__))


class NotesApp(App):
    def build(self):
        self.icon = resource_path("icon.png")
        self.file_path = os.path.join(self.user_data_dir, "notes.txt")
        self.title = "Заметки"
        # Главный фон приложения (темно-серый для контраста)

        self.main_layout = BoxLayout(orientation="vertical", padding=0, spacing=15)

        # 2. ДОБАВЛЯЕМ ФОН ПРИЛОЖЕНИЯ
        with self.main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # ТЕМНО-СЕРЫЙ (почти черный) фон
            self.rect_bg = Rectangle(
                pos=self.main_layout.pos, size=self.main_layout.size
            )

        self.header = Label(
            text="ЗАМЕТКИ",
            size_hint_y=None,
            height=60,
            font_size="20sp",
            bold=True,
            color=(1, 1, 1, 1),  # Белый текст
            halign="center",
            valign="middle",
        )
        # Делаем фон для заголовка (например, синий или темно-серый)
        with self.header.canvas.before:
            Color(0.2, 0.4, 0.8, 1)  # Цвет панели
            self.header_bg = Rectangle(pos=self.header.pos, size=self.header.size)
        self.header.bind(pos=self.update_header_bg, size=self.update_header_bg)
        self.main_layout.add_widget(self.header)

        # Привязываем обновление фона заголовка

        # 3. Привязываем обновление фона к изменению размера окна
        self.main_layout.bind(pos=self.update_bg, size=self.update_bg)
        self.input = TextInput(
            hint_text="Заметка...",
            size_hint_y=None,
            height=200,
            font_size="18sp",
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_active="",
            background_color=(
                0,
                0,
                0,
                0,
            ),  # Делаем прозрачным, чтобы видеть наш серый фон
            # multiline=False,
            padding=(20, 45, 20, 0),  # 45 пикселей сверху центрируют текст по вертикали
            foreground_color=(0, 0, 0, 1),  # Черный цвет текста
            hint_text_color=(0.8, 0.8, 0.9, 1),
        )
        # self.input.bind(pos=self.update_input_rect, size=self.update_input_rect)

        self.main_layout.add_widget(self.input)

        add_btn = Button(
            text="СОХРАНИТЬ",
            size_hint_y=None,
            height=90,
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5},
            background_color=(0, 0, 0, 0),
        )
        add_btn.bind(on_press=self.add_note)
        self.main_layout.add_widget(add_btn)
        add_btn.bind(
            pos=self.update_button_bg, 
            size=self.update_button_bg,
            state=self.update_button_bg)
        self.notes_list = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=10
        )
        self.notes_list.bind(minimum_height=self.notes_list.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.notes_list)
        self.main_layout.add_widget(scroll)

        self.load_notes()
        return self.main_layout

    def update_rect(self, instance, *args):
        # Обновляем белый фон при изменении размера или позиции заметки
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)  # Белый цвет фона
            # Rectangle(pos=instance.pos, size=instance.size)
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[
                    10,
                ],
            )

    def update_input_rect(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Светло-серый фон поля
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[
                    15,
                ],
            )

    def update_button_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            if instance.state == 'down':
                Color(0.1, 0.4, 0.8, 1)  # Темно-синий (эффект нажатия)
            else:
                Color(0.2, 0.6, 1, 1)  # Твой стандартный голубой
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[
                    15,
                ],  # Скругление чуть больше, чем у заметок
            )

    def display_note(self, text):
        # 1. Создаем общий контейнер для всей заметки
        row = BoxLayout(
            size_hint_y=None,
            spacing=0,
            padding=(0, 5),
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5},
        )

        # 2. Рисуем белый фон под ВСЕМ контейнером row
        with row.canvas.before:
            Color(1, 1, 1, 1)  # Белый

            # self.rect = Rectangle(pos=row.pos, size=row.size)
            RoundedRectangle(
                pos=row.pos,
                size=row.size,
                radius=[
                    20,
                ],
            )
        row.bind(pos=self.update_rect, size=self.update_rect)

        # 3. Текст заметки (черный)
        lbl = Label(
            text=text,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            padding=(15, 15),
            font_size="16sp",
            size_hint=(1, None),  # Занимает всю ширину, высота по тексту
        )

        # Настройка авто-высоты текста
        lbl.bind(width=lambda s, w: s.setter("text_size")(s, (w, None)))
        lbl.bind(texture_size=lambda s, z: s.setter("height")(s, z[1]))

        # Привязываем высоту белого фона (row) к высоте текста
        lbl.bind(height=lambda s, h: row.setter("height")(row, max(h, 80)))

        # 4. Кнопка удаления (Фиксированная внутри белого прямоугольника)
        # Помещаем её в отдельный контейнер, чтобы она не растягивалась
        btn_container = AnchorLayout(
            size_hint=(None, 1), width=70, padding=(5, 10), anchor_y="center"
        )

        del_btn = Button(
            text="X",
            size_hint=(None, None),
            size=(50, 50),  # ФИКСИРОВАННЫЙ РАЗМЕР
            background_normal="",  # Убираем серый градиент Kivy
            background_color=(0, 0, 0, 0),  # Красный
            color=(1, 1, 1, 1),  # Белый крестик
        )
        del_btn.bind(pos=self.update_btn_rect, size=self.update_btn_rect)
        del_btn.bind(on_press=lambda btn: self.delete_note(row, text))

        btn_container.add_widget(del_btn)

        # Собираем всё вместе
        row.add_widget(lbl)
        row.add_widget(btn_container)

        self.notes_list.add_widget(row, index=len(self.notes_list.children))

    def update_btn_rect(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.9, 0.2, 0.2, 1)  # Красный фон
            # Используем instance.pos и instance.size самой кнопки
            # radius=[instance.height / 2] сделает кнопку круглой
            RoundedRectangle(
                pos=instance.pos, size=instance.size, radius=[instance.height / 2]
            )

    def update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size

    def load_notes(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.display_note(line.strip())

    def update_bg(self, instance, value):
        self.rect_bg.pos = instance.pos
        self.rect_bg.size = instance.size

    def add_note(self, instance):
        text = self.input.text.strip()
        if text:
            self.display_note(text)
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            self.input.text = ""

    def delete_note(self, row_widget, text_to_remove):

        self.notes_list.remove_widget(row_widget)
        Clock.schedule_once(
            lambda dt: self._slow_delete_from_file(text_to_remove), 0.05
        )

    def _slow_delete_from_file(self, text_to_remove):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(self.file_path, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip() != text_to_remove.strip():
                        f.write(line)


if __name__ == "__main__":
    NotesApp().run()
