import time

from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.slider import MDSlider
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer, MDNavigationDrawerMenu
from kivymd.uix.screen import Screen
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.uix.label import Label
import random
from PIL import Image as PILImage
import io
import os
import shutil
from kivy.clock import Clock

# pip install pillow
# Window.size = (1000, 500)
PROJECTS_DIR = r"."
Window.orientation = 'landscape'
# Window.fullscreen = True

# --------------------------------------

from kivy.utils import platform
from kivy.logger import Logger
from plyer import storagepath
import os
from plyer import storagepath

if platform == 'android':
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
downloads_folder = storagepath.get_downloads_dir()
comicsapp_folder = os.path.join(downloads_folder, "COMICSAPP")
if not os.path.exists(comicsapp_folder):
    os.makedirs(comicsapp_folder)
    print(f"Папка '{comicsapp_folder}' успешно создана!")
else:
    print(f"Папка '{comicsapp_folder}' уже существует.")
PROJECTS_DIR = f'{comicsapp_folder}'

# ---------------------------------

KV = '''
ScreenManager:
    Screen:
        name: "start"
        BoxLayout:
            orientation: "vertical"
            spacing: dp(20)
            padding: dp(20)
            height: dp(10)
            MDLabel:
                text: "Выберите проект или создайте новый"
                halign: "center"
                font_style: "H4"
                height: dp(10)  # Устанавливаем явную высоту для MDLabel

            ScrollView:
                GridLayout:
                    id: projects_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
            MDRaisedButton:
                text: "Создать новый проект"
                size_hint: None, None
                size: dp(200), dp(50)
                pos_hint: {"center_x": 0.5}
                on_release: app.create_new_project()
    Screen:
        name: "paint"
        MDNavigationLayout:
            ScreenManager:
                Screen:
                    name: "paint_screen"
                    MDTopAppBar:
                        title: "Paint App"
                        pos_hint: {"top": 1}
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("toggle")]]
                    PaintWidget:
                        id: paint_canvas
                        canvas_color: [1, 1, 1, 1]
                        top_panel_height: dp(65)
                        size_hint: 1, 1
                    MDFloatingActionButton:
                        icon: "content-save"
                        pos_hint: {"left": 0.95, "bottom": 0.05}
                        on_release: app.save_project()
                    MDFloatingActionButton:
                        icon: "plus"
                        size_hint: None, None
                        size: dp(56), dp(56)
                        pos_hint: {"center_x": 0.8, "bottom": 0.05}
                        on_release: app.zoom_in()

                    MDFloatingActionButton:
                        icon: "minus"
                        size_hint: None, None
                        size: dp(56), dp(56)
                        pos_hint: {"center_x": 0.9, "bottom": 0.05}
                        on_release: app.zoom_out()

                    BoxLayout:
                        orientation: 'horizontal'
                        PaintWidget:
                            id: paint_widget
                            size_hint_x: 0.8

                        ScrollView:
                            size_hint_x: 0.2
                            GridLayout:
                                id: pages_list
                                cols: 1
                                size_hint_y: None
                                height: self.minimum_height


            MDNavigationDrawer:
                id: nav_drawer
                enable_swiping: False
                MDNavigationDrawerMenu:
                    OneLineIconListItem:
                        text: "Выбрать цвет"
                        on_release: app.open_color_picker()
                    OneLineIconListItem:
                        text: "Ластик"
                        on_release: app.use_eraser()
                    OneLineIconListItem:
                        text: "Очистить всё"
                        on_release: app.fill_canvas()
                    OneLineIconListItem:
                        text: "Undo"
                        on_release: app.undo()
                    OneLineIconListItem:
                        text: "Redo"
                        on_release: app.redo()
                    OneLineIconListItem:
                        text: "Очистить всё"
                        on_release: app.clear_page()
                    OneLineIconListItem:
                        text: "Карандаш"
                        on_release: app.use_pencil()
                    OneLineIconListItem:
                        text: "Маркер"
                        on_release: app.use_marker()
                    OneLineIconListItem:
                        text: "Добавить макет"
                        on_release: app.open_layout_chooser()
                    OneLineIconListItem:
                        text: "Добавить диалоговое окно"
                        on_release: app.open_dialog_chooser()
                    OneLineIconListItem:
                        text: "Добавить изображение"
                        on_release: app.open_file_chooser()
                    OneLineIconListItem:
                        text: "Толщина линии"
                    MDSlider:
                        id: slider
                        min: 1
                        max: 10
                        value: 2
                        on_value_normalized: app.set_line_width(self.value)
                        size_hint_x: 0.9
                        size_hint_y: None
                        height: dp(48)
                    OneLineIconListItem:
                        text: "Прозрачность"
                    MDSlider:
                        id: alpha_slider
                        min: 0.1
                        max: 1
                        value: 1
                        on_value_normalized: app.set_opacity(self.value)
                        size_hint_x: 0.9
                        size_hint_y: None
                        height: dp(48)

'''


class PaintWidget(Widget):
    line_width = 2
    current_color = [0, 0, 0, 1]
    top_panel_height = dp(64)
    undo_stack = []
    redo_stack = []
    is_marker = False
    opacity = 1.0
    image_scatter = None  # Для хранения загруженного изображения

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_image = None
        self.pages = []  # Хранилище страниц
        self.canvas_color = [1, 1, 1, 1]  # Белый цвет фона по умолчанию
        self.current_color = [0, 0, 0, 1]  # Черный цвет по умолчанию
        self.page_names = {}  # Словарь для хранения номеров страниц
        self.line_width = 2
        self.page_counter = 1  # Счётчик страниц
        self.layout_image = None  # Для хранения макета
        self.dialog_image = None  # Для хранения диалогового окна
        self.current_page = None
        self.create_new_page()
        with self.canvas:
            Color(*self.canvas_color)
            Rectangle(pos=(0, 0), size=(self.width, self.height - self.top_panel_height))

    def create_new_page(self):
        """Создаёт новую страницу без потери предыдущих."""
        new_canvas = []
        self.pages.append(new_canvas)  # Добавляем страницу в список
        self.page_names[len(self.pages) - 1] = len(self.pages)  # Добавляем ключ в словарь
        self.switch_to_page(len(self.pages) - 1)  # Переключаемся на неё

    def switch_to_page(self, index):
        """Переключение между страницами, учитывая возможные удалённые индексы."""
        if index < 0 or index >= len(self.pages):
            return  # Проверяем, что индекс в пределах допустимого

        if self.current_page is not None:
            self.pages[self.current_page] = self.canvas.children[:]

        self.canvas.clear()
        self.current_page = index

        # Восстанавливаем содержимое выбранной страницы
        for obj in self.pages[index]:
            self.canvas.add(obj)

    def delete_page(self, index):
        """Удаляет страницу и корректно обновляет текущий холст."""
        if len(self.pages) > 1:
            # Сохраняем текущее содержимое перед удалением
            if self.current_page is not None:
                self.pages[self.current_page] = list(self.canvas.children)

            # Определяем новую страницу для переключения
            new_index = index if index < len(self.pages) - 1 else index - 1

            # Переключаемся на новую страницу ПЕРЕД удалением старой
            self.switch_to_page(new_index)

            # Удаляем страницу из словаря page_names, если ключ существует
            if index in self.page_names:
                del self.page_names[index]

            # Теперь удаляем страницу (но не очищаем canvas сразу)
            del self.pages[index]

            # Обновляем нумерацию страниц
            temp_names = {}
            for i in range(len(self.pages)):
                temp_names[i] = self.page_names.get(i + 1, i + 1)
            self.page_names = temp_names

            # Убеждаемся, что переключились на существующую страницу
            if self.current_page >= len(self.pages):
                self.current_page = len(self.pages) - 1

            # Очищаем canvas и загружаем новую страницу
            self.canvas.clear()
            for obj in self.pages[self.current_page]:
                self.canvas.add(obj)

    def on_touch_down(self, touch):
        # Увеличенный хитбокс для кнопки меню
        menu_hitbox_x = dp(48)  # Учитываем размер иконки меню + небольшой запас
        menu_hitbox_y = self.height - self.top_panel_height  # Верхняя граница панели
        menu_hitbox_height = dp(64)  # Высота кнопки меню (обычно равна высоте панели)

        # Если касание попадает в зону кнопки меню, передаем управление дальше
        if touch.x <= menu_hitbox_x and menu_hitbox_y <= touch.y <= menu_hitbox_y + menu_hitbox_height or not self.collide_point(
                *touch.pos):
            return False  # Позволяем Kivy обработать нажатие на кнопку

        # Блокируем рисование на верхней панели
        if touch.y >= self.height - self.top_panel_height:
            return True
        self.save_state()
        self.redo_stack.clear()

        with self.canvas:
            Color(*self.current_color)  # Используем текущий цвет (для ластика это прозрачный)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.y < self.height - self.top_panel_height:
            if 'line' in touch.ud:
                touch.ud['line'].points += [touch.x + random.uniform(-1, 1), touch.y + random.uniform(-1, 1)]
        return super().on_touch_move(touch)

    def set_line_width(self, width):
        self.line_width = width

    def set_opacity(self, value):
        self.opacity = value

    def set_color(self, color):
        self.current_color = color

    def use_pencil(self):
        self.is_marker = False

    def use_marker(self):
        self.is_marker = True

    def fill(self):
        """Заливает фон текущим цветом."""
        self.save_state()
        self.redo_stack.clear()
        with self.canvas:
            Color(*self.current_color, self.opacity)
            Rectangle(pos=(0, 0), size=(self.width, self.height - self.top_panel_height))

    def use_eraser(self):
        self.set_color(self.canvas_color)  # Используем цвет фона холста

    def save_state(self):
        self.undo_stack.append(self.canvas.children[:])

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.canvas.children[:])
            last_state = self.undo_stack.pop()
            self.canvas.clear()
            for obj in last_state:
                self.canvas.add(obj)

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.canvas.children[:])
            next_state = self.redo_stack.pop()
            self.canvas.clear()
            for obj in next_state:
                self.canvas.add(obj)

    def add_layout(self, layout_path):
        """Добавляет макет (изображение) на текущую страницу."""
        if os.path.exists(layout_path):
            try:
                # Загружаем изображение
                img = Image(source=layout_path, allow_stretch=True, keep_ratio=True)

                # Устанавливаем размер изображения равным размеру холста
                img.size_hint = (1, 1)
                img.size = (self.width, self.height - self.top_panel_height)

                # Позиционируем изображение внизу холста
                img.pos = (0, 0)

                # Добавляем изображение на холст
                self.pages[self.current_page].append(img)
                self.add_widget(img)
            except Exception as e:
                print(f"Ошибка при загрузке макета: {e}")

    def add_dialog_window(self, dialog_path):
        """Добавляет диалоговое окно (изображение) на текущую страницу."""
        if os.path.exists(dialog_path):
            try:
                # Загружаем изображение
                img = Image(source=dialog_path, allow_stretch=True, keep_ratio=True)
                img.size_hint = (None, None)
                img.size = (300, 300)  # Начальный размер

                # Создаем Scatter для перемещения и масштабирования
                scatter = Scatter(
                    do_rotation=False,  # Отключаем вращение
                    do_scale=True,  # Включаем масштабирование
                    do_translation=True,  # Включаем перемещение
                    size_hint=(None, None),
                    size=img.size,
                )
                scatter.add_widget(img)

                # Добавляем обработчик для отладки
                def on_scatter_touch_down(scatter, touch):
                    print(f"Scatter touch down: {touch.pos}")
                    return super(Scatter, scatter).on_touch_down(touch)

                scatter.bind(on_touch_down=on_scatter_touch_down)

                # Добавляем кнопку подтверждения (галочку)
                confirm_button = Button(
                    text="✔️",  # Галочка
                    size_hint=(None, None),
                    size=(50, 50),
                    pos_hint={"right": 0.95, "top": 0.95},  # Позиция справа над кнопкой сохранения
                )
                confirm_button.bind(on_release=lambda btn: self.confirm_dialog(scatter, confirm_button))

                # Добавляем Scatter и кнопку на холст
                self.pages[self.current_page].append((scatter, confirm_button))
                self.add_widget(scatter)
                self.add_widget(confirm_button)
            except Exception as e:
                print(f"Ошибка при загрузке диалогового окна: {e}")

    def confirm_dialog(self, scatter, confirm_button):
        """Фиксирует диалоговое окно и позволяет рисовать на нём."""
        # Отключаем перемещение и масштабирование
        scatter.do_scale = False
        scatter.do_translation = False

        # Удаляем кнопку подтверждения
        self.remove_widget(confirm_button)

        # Теперь можно рисовать на диалоговом окне
        scatter.bind(on_touch_down=self.on_dialog_touch_down, on_touch_move=self.on_dialog_touch_move)

    def on_dialog_touch_down(self, scatter, touch):
        """Обрабатывает касания для рисования на диалоговом окне."""
        if scatter.collide_point(*touch.pos):
            with scatter.canvas:
                Color(*self.current_color)
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)
            return True
        return False

    def on_dialog_touch_move(self, scatter, touch):
        """Обрабатывает перемещение для рисования на диалоговом окне."""
        if scatter.collide_point(*touch.pos) and 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        return False


class PaintApp(MDApp):
    current_project = None  # Хранит активный проект

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.root = Builder.load_string(KV)
        Clock.schedule_once(lambda dt: self.update_pages_list(), 0.1)
        Clock.schedule_once(lambda dt: self.update_projects_list(), 0)

        return self.root

    from kivymd.uix.button import MDRaisedButton, MDFlatButton
    from kivymd.uix.card import MDCard

    from kivymd.uix.boxlayout import BoxLayout
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.label import MDLabel
    def clear_page(self):
        self.root.ids.paint_canvas.clear_page()

    def update_projects_list(self):
        """Обновляет список проектов на стартовом экране."""
        print('1')
        import os
        projects_list = self.root.ids.projects_list

        self.root.ids.projects_list.clear_widgets()

        if not os.path.exists(PROJECTS_DIR):
            os.makedirs(PROJECTS_DIR)
            print('piz')
        projects = [
            d for d in os.listdir(PROJECTS_DIR)
            if d.startswith("projects") and d[8:].isdigit()  # Проверяем правильный формат
        ]

        projects = sorted(projects, key=lambda x: int(x[8:]))  # Обрезаем 'projects' и конвертируем в число
        for project in projects:
            project_path = os.path.join(PROJECTS_DIR, project)
            print(project_path)

            # Используем MDCard для каждого проекта
            card = MDCard(size_hint=(None, None), size=("750dp", "250dp"), radius=[10, 10, 10, 10], elevation=5)
            card_box = BoxLayout(orientation="vertical", padding=10, spacing=10)

            # Добавляем изображение с превью
            preview = FitImage(source=self.get_preview_image(project_path), size_hint=(1, 0.7),
                               pos_hint={"center_x": 0.5})

            # Кнопки под изображением
            button_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.3), spacing=10, pos_hint={"center_x": 0.5})

            # Кнопка "Открыть"
            open_btn = MDRaisedButton(
                text=project,
                size_hint=(0.5, None),
                height="36dp",
                md_bg_color=(0.2, 0.6, 0.2, 1),  # Зеленый фон
                text_color=(1, 1, 1, 1),  # Белый текст
                font_size="12sp"
            )
            open_btn.bind(on_release=lambda x, p=project_path: self.open_project(p))

            # Кнопка "Удалить"
            del_btn = MDFlatButton(
                text="DEL",
                size_hint=(0.2, None),
                height="36dp",
                md_bg_color=(0.8, 0.2, 0.2, 1),  # Красный фон
                text_color=(1, 1, 1, 1),  # Белый текст
                font_size="12sp"
            )
            del_btn.bind(on_release=lambda x, p=project_path: self.confirm_delete_project(p))

            # Добавляем кнопки в horizontal BoxLayout
            button_box.add_widget(open_btn)
            button_box.add_widget(del_btn)

            # Добавляем изображение и кнопки в карточку
            card_box.add_widget(preview)
            card_box.add_widget(button_box)

            # Добавляем BoxLayout в карточку и карточку в список
            card.add_widget(card_box)
            projects_list.add_widget(card)

    def create_new_project(self):
        """Создаёт новый проект и загружает его в редактор."""
        project_number = 1
        while os.path.exists(os.path.join(PROJECTS_DIR, f"projects{project_number}")):
            project_number += 1

        new_project_path = os.path.join(PROJECTS_DIR, f"projects{project_number}")
        os.makedirs(new_project_path)

        self.open_project(new_project_path)

    def open_project(self, project_path):
        """Открывает существующий проект и загружает его в редактор."""
        self.current_project = project_path
        self.root.current = "paint"
        self.load_project()

    def confirm_delete_project(self, project_path):
        """Запрашивает подтверждение перед удалением проекта."""
        popup = Popup(
            title="Удаление проекта",
            content=Label(text="Вы уверены?"),
            size_hint=(1, 1), size=(400, 200),
        )

        layout = BoxLayout(orientation="horizontal")
        yes_btn = Button(text="Да", on_release=lambda x: self.delete_project(project_path, popup))
        no_btn = Button(text="Нет", on_release=popup.dismiss)

        layout.add_widget(yes_btn)
        layout.add_widget(no_btn)
        popup.content.add_widget(layout)
        popup.open()

    def delete_project(self, project_path, popup):
        """Удаляет проект."""
        print(project_path)
        shutil.rmtree(project_path)
        popup.dismiss()
        self.update_projects_list()

    # def get_preview_image(self, project_path):
    #     """Возвращает превью первой страницы или белый лист."""
    #
    #     preview_path = os.path.join(project_path, "page_1.png")
    #     return preview_path if os.path.exists(preview_path) else "blank.png"
    def get_preview_image(self, project_path):
        """Возвращает превью первой страницы или белый лист."""
        os.listdir(project_path)
        with open(os.path.join(project_path, "page_1.png")) as f:
            pass
        preview_path = os.path.join(project_path, "page_1.png")
        return preview_path if os.path.exists(preview_path) else "blank.png"

    def save_project(self):
        """Сохраняет ВСЕ страницы проекта и возвращает в меню."""
        if not self.current_project:
            return

        paint_canvas = self.root.ids.paint_canvas
        original_page = paint_canvas.current_page  # Запоминаем текущую страницу

        for i in range(len(paint_canvas.pages)):
            paint_canvas.switch_to_page(i)  # Переключаемся на страницу перед сохранением

            # Сохраняем страницу как изображение
            img_path = os.path.join(self.current_project, f"page_{i + 1}.png")
            if os.path.exists(img_path):
                os.remove(img_path)
            paint_canvas.export_to_png(img_path)

            # Сохраняем макет (если он есть)
            layout_path = os.path.join(self.current_project, f"layout_{i + 1}.png")
            if hasattr(paint_canvas, 'layout_image') and paint_canvas.layout_image:
                paint_canvas.layout_image.export_to_png(layout_path)

            # Сохраняем диалоговое окно (если оно есть)
            dialog_path = os.path.join(self.current_project, f"dialog_{i + 1}.png")
            if hasattr(paint_canvas, 'dialog_image') and paint_canvas.dialog_image:
                paint_canvas.dialog_image.export_to_png(dialog_path)

        self.update_projects_list()
        paint_canvas.switch_to_page(original_page)  # Возвращаемся на исходную страницу
        self.root.current = "start"  # Переходим на стартовый экран

    def load_project(self):
        """Загружает все страницы проекта с их рисунками, макетами и диалоговыми окнами."""
        paint_canvas = self.root.ids.paint_canvas

        # Очищаем текущие страницы
        paint_canvas.pages.clear()
        paint_canvas.canvas.clear()
        paint_canvas.current_page = None

        loaded_pages = False  # Флаг: загрузились ли страницы?

        for i in range(1, 100):  # Загружаем до 100 страниц
            img_path = os.path.join(self.current_project, f"page_{i}.png")
            layout_path = os.path.join(self.current_project, f"layout_{i}.png")
            dialog_path = os.path.join(self.current_project, f"dialog_{i}.png")

            if os.path.exists(img_path):
                self.load_page_from_image(img_path)  # Загружаем страницу
                loaded_pages = True

            if os.path.exists(layout_path):
                paint_canvas.add_layout(layout_path)  # Загружаем макет

            if os.path.exists(dialog_path):
                paint_canvas.add_dialog_window(dialog_path)  # Загружаем диалоговое окно

        if not loaded_pages:
            paint_canvas.create_new_page()  # Если нет страниц, создаём пустую

        paint_canvas.switch_to_page(0)  # Переход на первую загруженную страницу

    def save_page_as_image(self, page, path):
        """Сохраняет текущий холст как изображение."""
        if not page:
            return

        # ✅ Берём текстуру canvas
        self.root.ids.paint_canvas.export_to_png(path)

    def load_page_from_image(self, path):
        """Загружает страницу из изображения и добавляет в `canvas`."""
        paint_canvas = self.root.ids.paint_canvas
        paint_canvas.create_new_page()  # ✅ Создаём новую страницу
        imgg = PILImage.open(path)

        # Получаем размеры
        width, height = imgg.size
        # ✅ Загружаем изображение
        img = Image(source=path, allow_stretch=True, keep_ratio=True)
        img.size = (width, height)

        # ✅ Добавляем изображение в страницу
        paint_canvas.pages[-1].append(img)
        paint_canvas.add_widget(img)  # ✅ Показываем картинку на холсте
        imgg = None

    def update_pages_list(self):
        """Обновляет список страниц в боковой панели."""
        pages_list = self.root.ids.pages_list
        pages_list.clear_widgets()

        paint_canvas = self.root.ids.paint_canvas

        for i in range(len(paint_canvas.pages)):
            page_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)

            page_number = paint_canvas.page_names.get(i, i + 1)  # Берём сохранённый номер

            btn = Button(text=f'Страница {page_number}', size_hint_x=0.8)
            btn.bind(on_release=lambda x, index=i: paint_canvas.switch_to_page(index))

            del_btn = Button(text='❌', size_hint_x=0.2)
            del_btn.bind(on_release=lambda x, index=i: self.delete_page(index))

            page_layout.add_widget(btn)
            page_layout.add_widget(del_btn)
            pages_list.add_widget(page_layout)

        add_btn = Button(text='+', size_hint_y=None, height=40)
        add_btn.bind(on_release=lambda x: self.add_page())
        pages_list.add_widget(add_btn)

    def delete_page(self, index):
        """Удаляет страницу и обновляет список."""
        try:
            # Удаляем страницу из холста
            self.root.ids.paint_canvas.delete_page(index)
            self.update_pages_list()
        except KeyError as e:
            print(f"Ошибка при удалении страницы: {e}")

    def add_page(self):
        self.root.ids.paint_canvas.create_new_page()
        self.update_pages_list()

    def change_screen(self, screen_name):
        self.root.current = screen_name

    def set_line_width(self, value):
        self.root.ids.paint_canvas.set_line_width(value)

    def set_opacity(self, value):
        self.root.ids.paint_canvas.set_opacity(value)

    def open_color_picker(self):
        color_picker = MDColorPicker()
        color_picker.bind(on_select_color=self.on_color_selected)
        color_picker.open()

    def on_color_selected(self, instance, color):
        self.root.ids.paint_canvas.set_color(color)

    def use_eraser(self):
        self.root.ids.paint_canvas.use_eraser()  # Убедитесь, что используется paint_canvas, а не paint_widget

    def fill_canvas(self):
        self.root.ids.paint_canvas.fill()

    def use_pencil(self):
        self.root.ids.paint_canvas.use_pencil()

    def use_marker(self):
        self.root.ids.paint_canvas.use_marker()

    def undo(self):
        self.root.ids.paint_canvas.undo()

    def redo(self):
        self.root.ids.paint_canvas.redo()

    def open_file_chooser(self):
        """Открывает проводник для выбора изображения с кнопкой выбора"""
        layout = BoxLayout(orientation="vertical")
        file_chooser = FileChooserListView()
        btn_select = Button(text="Выбрать", size_hint=(1, None), height=dp(40))
        file_chooser = FileChooserListView(path=storagepath.get_downloads_dir())
        layout.add_widget(file_chooser)
        layout.add_widget(btn_select)

        popup = Popup(
            title="Выберите изображение",
            content=layout,
            size_hint=(0.9, 0.9),
        )

        def select_file(instance):
            """Загружает выбранное изображение"""
            if file_chooser.selection:
                self.load_image(file_chooser.selection, popup)

        btn_select.bind(on_release=select_file)
        popup.open()

    def load_image(self, selection, popup):
        """Загружает выбранное изображение в PaintWidget"""
        if selection:
            self.add_image(selection[0])

        popup.dismiss()

    def add_image(self, source):
        """Добавляет изображение на текущую страницу с возможностью перемещения и изменения размера."""
        scatter = Scatter(do_rotation=False, do_scale=True, do_translation=True)
        img = Image(source=source, size_hint=(1, 1), size=(300, 300))
        scatter.add_widget(img)

        # Добавляем кнопку подтверждения
        confirm_button = Button(text="Подтвердить", size_hint=(1, 1), size=(100, 50))
        confirm_button.bind(on_release=lambda btn: self.confirm_image(scatter, confirm_button))

        # Добавляем изображение на текущую страницу
        self.root.ids.paint_canvas.pages[self.root.ids.paint_canvas.current_page].append((scatter, confirm_button))
        self.root.ids.paint_canvas.add_widget(scatter)  # Добавляем scatter на холст
        self.root.ids.paint_canvas.add_widget(confirm_button)  # Добавляем кнопку подтверждения на холст

    def confirm_image(self, scatter, confirm_button):
        """Блокирует дальнейшее редактирование изображения."""
        scatter.do_scale = False
        scatter.do_translation = False
        self.root.ids.paint_canvas.remove_widget(confirm_button)  # Удаляем кнопку подтверждения

    def open_layout_chooser(self):
        """Открывает проводник для выбора макета."""
        layout = BoxLayout(orientation="vertical")
        file_chooser = FileChooserListView(path="sprite")
        btn_select = Button(text="Выбрать", size_hint=(1, None), height=dp(40))
        layout.add_widget(file_chooser)
        layout.add_widget(btn_select)

        popup = Popup(
            title="Выберите макет",
            content=layout,
            size_hint=(0.9, 0.9),
        )

        def select_layout(instance):
            """Загружает выбранный макет."""
            if file_chooser.selection:
                self.root.ids.paint_canvas.add_layout(file_chooser.selection[0])
                popup.dismiss()

        btn_select.bind(on_release=select_layout)
        popup.open()

    def open_dialog_chooser(self):
        """Открывает проводник для выбора диалогового окна."""
        layout = BoxLayout(orientation="vertical")
        file_chooser = FileChooserListView(path="dialog_window")
        btn_select = Button(text="Выбрать", size_hint=(1, None), height=dp(40))
        layout.add_widget(file_chooser)
        layout.add_widget(btn_select)

        popup = Popup(
            title="Выберите диалоговое окно",
            content=layout,
            size_hint=(0.9, 0.9),
        )

        def select_dialog(instance):
            """Загружает выбранное диалоговое окно."""
            if file_chooser.selection:
                self.root.ids.paint_canvas.add_dialog_window(file_chooser.selection[0])
                popup.dismiss()

        btn_select.bind(on_release=select_dialog)
        popup.open()


if __name__ == '__main__':
    PaintApp().run()