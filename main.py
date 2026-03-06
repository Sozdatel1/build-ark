import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import Color, RoundedRectangle


class NotesApp(App):
    def build(self):
        self.file_path = os.path.join(self.user_data_dir, "notes.txt")

        # Главный фон приложения (темно-серый для контраста)

        self.main_layout = BoxLayout(orientation="vertical", padding=15, spacing=15)

        # 2. ДОБАВЛЯЕМ ФОН ПРИЛОЖЕНИЯ
        with self.main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # ТЕМНО-СЕРЫЙ (почти черный) фон
            self.rect_bg = Rectangle(
                pos=self.main_layout.pos, size=self.main_layout.size
            )

        # 3. Привязываем обновление фона к изменению размера окна
        self.main_layout.bind(pos=self.update_bg, size=self.update_bg)
        self.input = TextInput(
            hint_text="Заметка...",
            size_hint_y=None,
            height=120,
            font_size="18sp",
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
            height=50,
            background_color=(0, 0.7, 0.3, 1),
        )
        add_btn.bind(on_press=self.add_note)
        self.main_layout.add_widget(add_btn)

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

    def display_note(self, text):
        # 1. Создаем общий контейнер для всей заметки
        row = BoxLayout(size_hint_y=None, spacing=0, padding=(0, 5))

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
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(self.file_path, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip() != text_to_remove:
                        f.write(line)


if __name__ == "__main__":
    NotesApp().run()
