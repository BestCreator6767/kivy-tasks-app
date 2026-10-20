import json
import os

from kivy.config import Config
Config.set("graphics", "multisamples", "4")

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

DATA_FILE = "tasks.json"

THEMES = {
    "dark": {
        "window_bg": (0.08, 0.07, 0.10, 1),
        "card_bg": (0.13, 0.12, 0.16, 1),
        "input_bg": (0.16, 0.15, 0.19, 1),
        "input_border": (0.24, 0.22, 0.28, 1),
        "primary": (0.82, 0.74, 1.0, 1),
        "on_primary": (0.22, 0.12, 0.45, 1),
        "text": (0.91, 0.89, 0.92, 1),
        "text_hex": "#E6E1E5",
        "muted_hex": "#8C8693",
        "hint": (0.55, 0.53, 0.58, 1),
        "danger_bg": (0.35, 0.15, 0.18, 0.9),
        "danger_cross": (1.0, 0.65, 0.65, 1),
        "toggle_btn_bg": (0.18, 0.17, 0.22, 1),
        "toggle_btn_text": (0.95, 0.85, 0.45, 1),
        "toggle_label": "Светлая тема",
    },
    "light": {
        "window_bg": (0.98, 0.96, 0.99, 1),
        "card_bg": (0.94, 0.91, 0.96, 1),
        "input_bg": (0.91, 0.88, 0.93, 1),
        "input_border": (0.82, 0.79, 0.85, 1),
        "primary": (0.40, 0.31, 0.64, 1),
        "on_primary": (1.0, 1.0, 1.0, 1),
        "text": (0.11, 0.11, 0.14, 1),
        "text_hex": "#1D1B22",
        "muted_hex": "#79747E",
        "hint": (0.47, 0.45, 0.50, 1),
        "danger_bg": (0.95, 0.85, 0.85, 1),
        "danger_cross": (0.75, 0.15, 0.15, 1),
        "toggle_btn_bg": (0.90, 0.87, 0.93, 1),
        "toggle_btn_text": (0.32, 0.25, 0.48, 1),
        "toggle_label": "Тёмная тема",
    },
}

class MaterialButton(ButtonBehavior, Label):
    def __init__(self, bg_color, text_color, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.custom_bg_color = bg_color
        self.color = text_color
        self.radius = radius

        with self.canvas.before:
            self.bg_color_inst = Color(*self.custom_bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self.border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                width=1.2,
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)

    def set_color(self, bg_rgba, text_rgba=None):
        self.custom_bg_color = bg_rgba
        self.bg_color_inst.rgba = bg_rgba
        if text_rgba:
            self.color = text_rgba

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.bg_color_inst.rgba = [c * 0.85 for c in self.custom_bg_color[:3]] + [self.custom_bg_color[3]]
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.bg_color_inst.rgba = self.custom_bg_color
        return super().on_touch_up(touch)

class DeleteButton(ButtonBehavior, Widget):
    def __init__(self, bg_color, cross_color, radius=10, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (34, 34)
        self.radius = radius
        self.custom_bg_color = bg_color
        self.custom_cross_color = cross_color

        with self.canvas.before:
            self.bg_color_inst = Color(*self.custom_bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self.border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                width=1.0,
            )

        with self.canvas:
            self.cross_color_inst = Color(*self.custom_cross_color)
            self.line1 = Line(points=[], width=1.6, cap="round")
            self.line2 = Line(points=[], width=1.6, cap="round")

        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
        d = 5.5
        cx, cy = self.center_x, self.center_y
        self.line1.points = [cx - d, cy - d, cx + d, cy + d]
        self.line2.points = [cx - d, cy + d, cx + d, cy - d]

    def set_colors(self, bg_rgba, cross_rgba):
        self.custom_bg_color = bg_rgba
        self.custom_cross_color = cross_rgba
        self.bg_color_inst.rgba = bg_rgba
        self.cross_color_inst.rgba = cross_rgba

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.bg_color_inst.rgba = [c * 0.8 for c in self.custom_bg_color[:3]] + [self.custom_bg_color[3]]
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.bg_color_inst.rgba = self.custom_bg_color
        return super().on_touch_up(touch)

class RoundedTextInput(BoxLayout):
    def __init__(self, bg_color, border_color, hint_text="", radius=16, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.radius = radius
        self.custom_bg_color = bg_color
        self.custom_border_color = border_color
        self.padding = [14, 0, 14, 0]

        with self.canvas.before:
            self.bg_color_inst = Color(*self.custom_bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self.border_color_inst = Color(*self.custom_border_color)
            self.border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                width=1.2,
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

        self.input = TextInput(
            hint_text=hint_text,
            multiline=False,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            padding=[4, 15, 4, 15],
            font_size="15sp",
            size_hint=(1, 1),
        )
        self.add_widget(self.input)

    def _update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)

    def set_colors(self, bg_rgba, border_rgba, fg_rgba, hint_rgba, cursor_rgba):
        self.custom_bg_color = bg_rgba
        self.custom_border_color = border_rgba
        self.bg_color_inst.rgba = bg_rgba
        self.border_color_inst.rgba = border_rgba
        self.input.foreground_color = fg_rgba
        self.input.hint_text_color = hint_rgba
        self.input.cursor_color = cursor_rgba

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, val):
        self.input.text = val

    def bind_text_validate(self, callback):
        self.input.bind(on_text_validate=callback)

class TaskCard(BoxLayout):
    def __init__(self, task, app, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.app = app
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 54
        self.spacing = 10
        self.padding = [12, 6, 12, 6]

        t = self.app.get_theme()

        with self.canvas.before:
            self.bg_color_inst = Color(*t["card_bg"])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            self.border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, 14),
                width=1.0,
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.checkbox = CheckBox(
            active=self.task.get("done", False),
            size_hint=(None, None),
            size=(34, 34),
            pos_hint={"center_y": 0.5},
            color=t["primary"],
        )
        self.checkbox.bind(active=self.on_toggle)

        self.label = Label(
            text=self.get_formatted_text(),
            markup=True,
            halign="left",
            valign="middle",
            font_size="15sp",
        )
        self.label.bind(size=self.label.setter("text_size"))

        self.del_btn = DeleteButton(
            bg_color=t["danger_bg"],
            cross_color=t["danger_cross"],
            radius=10,
            pos_hint={"center_y": 0.5},
        )
        self.del_btn.bind(on_press=self.delete_card)

        self.add_widget(self.checkbox)
        self.add_widget(self.label)
        self.add_widget(self.del_btn)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 14)

    def get_formatted_text(self):
        t = self.app.get_theme()
        safe_text = (
            self.task["text"]
            .replace("&", "&amp;")
            .replace("[", "&bl;")
            .replace("]", "&br;")
        )
        if self.task.get("done", False):
            return f"[s][color={t['muted_hex']}]{safe_text}[/color][/s]"
        return f"[color={t['text_hex']}]{safe_text}[/color]"

    def update_theme(self):
        t = self.app.get_theme()
        self.bg_color_inst.rgba = t["card_bg"]
        self.checkbox.color = t["primary"]
        self.label.text = self.get_formatted_text()
        self.del_btn.set_colors(t["danger_bg"], t["danger_cross"])

    def on_toggle(self, checkbox, value):
        self.task["done"] = value
        self.label.text = self.get_formatted_text()
        self.app.save_data()

    def delete_card(self, button):
        self.app.delete_task(self.task, self)

class MyApp(App):
    def build(self):
        self.title = "Мои задачи"
        self.current_theme, self.tasks = self.load_data()

        t = self.get_theme()
        Window.clearcolor = t["window_bg"]

        main_layout = BoxLayout(orientation="vertical", padding=16, spacing=12)

        top_bar = BoxLayout(size_hint_y=None, height=48, spacing=10)

        self.header_title = Label(
            text="[b]Задачи[/b]",
            markup=True,
            font_size="22sp",
            color=t["text"],
            halign="left",
            valign="middle",
        )
        self.header_title.bind(size=self.header_title.setter("text_size"))

        self.theme_btn = MaterialButton(
            bg_color=t["toggle_btn_bg"],
            text_color=t["toggle_btn_text"],
            radius=14,
            text=t["toggle_label"],
            font_size="13sp",
            bold=True,
            size_hint=(None, None),
            size=(126, 38),
            pos_hint={"center_y": 0.5},
        )
        self.theme_btn.bind(on_press=self.toggle_theme)

        top_bar.add_widget(self.header_title)
        top_bar.add_widget(self.theme_btn)
        main_layout.add_widget(top_bar)

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=4,
            bar_color=(*t["primary"][:3], 0.6),
            bar_inactive_color=(*t["primary"][:3], 0.2),
            scroll_type=["bars", "content"],
        )

        self.tasks_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8,
            padding=[0, 4, 4, 4],
        )
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter("height"))
        self.scroll.add_widget(self.tasks_layout)
        main_layout.add_widget(self.scroll)

        self.empty_label = Label(
            text=f"[color={t['muted_hex']}]Список задач пуст\nДобавьте новую задачу ниже[/color]",
            markup=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=120,
            font_size="15sp",
        )

        input_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)

        self.task_input = RoundedTextInput(
            bg_color=t["input_bg"],
            border_color=t["input_border"],
            hint_text="Новая задача...",
            radius=16,
        )
        self.task_input.set_colors(
            t["input_bg"], t["input_border"], t["text"], t["hint"], t["primary"]
        )
        self.task_input.bind_text_validate(self.add_task)

        self.add_btn = MaterialButton(
            bg_color=t["primary"],
            text_color=t["on_primary"],
            radius=16,
            text="Создать",
            bold=True,
            font_size="14sp",
            size_hint=(None, 1),
            width=110,
        )
        self.add_btn.bind(on_press=self.add_task)

        input_bar.add_widget(self.task_input)
        input_bar.add_widget(self.add_btn)
        main_layout.add_widget(input_bar)

        for task in self.tasks:
            self.tasks_layout.add_widget(TaskCard(task, self))
        self.check_empty_state()

        return main_layout

    def get_theme(self):
        return THEMES[self.current_theme]

    def toggle_theme(self, *args):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.save_data()
        self.apply_theme()

    def apply_theme(self):
        t = self.get_theme()
        Window.clearcolor = t["window_bg"]

        self.header_title.color = t["text"]
        self.theme_btn.text = t["toggle_label"]
        self.theme_btn.set_color(t["toggle_btn_bg"], t["toggle_btn_text"])

        self.scroll.bar_color = (*t["primary"][:3], 0.6)
        self.scroll.bar_inactive_color = (*t["primary"][:3], 0.2)

        self.empty_label.text = f"[color={t['muted_hex']}]Список задач пуст\nДобавьте новую задачу ниже[/color]"

        self.task_input.set_colors(
            t["input_bg"], t["input_border"], t["text"], t["hint"], t["primary"]
        )
        self.add_btn.set_color(t["primary"], t["on_primary"])

        for child in self.tasks_layout.children:
            if isinstance(child, TaskCard):
                child.update_theme()

    def check_empty_state(self):
        if not self.tasks:
            if self.empty_label not in self.tasks_layout.children:
                self.tasks_layout.add_widget(self.empty_label)
        else:
            if self.empty_label in self.tasks_layout.children:
                self.tasks_layout.remove_widget(self.empty_label)

    def load_data(self):
        theme = "dark"
        tasks = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                tasks.append({"text": item, "done": False})
                            elif isinstance(item, dict):
                                tasks.append({
                                    "text": str(item.get("text", "")),
                                    "done": bool(item.get("done", False)),
                                })
                    elif isinstance(data, dict):
                        theme = data.get("theme", "dark")
                        if theme not in THEMES:
                            theme = "dark"
                        for item in data.get("tasks", []):
                            if isinstance(item, str):
                                tasks.append({"text": item, "done": False})
                            elif isinstance(item, dict):
                                tasks.append({
                                    "text": str(item.get("text", "")),
                                    "done": bool(item.get("done", False)),
                                })
            except Exception:
                pass
        return theme, tasks

    def save_data(self):
        payload = {
            "theme": self.current_theme,
            "tasks": self.tasks,
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def add_task(self, *args):
        text = self.task_input.text.strip()
        if text:
            new_task = {"text": text, "done": False}
            self.tasks.append(new_task)
            self.save_data()
            self.tasks_layout.add_widget(TaskCard(new_task, self))
            self.task_input.text = ""
            self.check_empty_state()

    def delete_task(self, task, card_widget):
        if task in self.tasks:
            self.tasks.remove(task)
            self.save_data()
        self.tasks_layout.remove_widget(card_widget)
        self.check_empty_state()

MyApp().run()