import requests
import threading
import json
import os
from kivymd.uix.screen    import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label     import MDLabel
from kivymd.uix.button    import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar   import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivy.metrics         import dp
from kivy.clock           import Clock, mainthread
from kivy.app             import App

def get_config_path():
    try:
        app = App.get_running_app()
        if app and hasattr(app, 'user_data_dir'):
            return os.path.join(app.user_data_dir, "quotepro_config.json")
    except:
        pass
    return "quotepro_config.json"

def get_api():
    try:
        with open(get_config_path(), "r") as f:
            return json.load(f)["api_url"]
    except:
        return "http://192.168.207.152:8000"

def save_api(url):
    try:
        with open(get_config_path(), "w") as f:
            json.dump({"api_url": url}, f)
    except:
        pass

class SettingsScreen(MDScreen):

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def build_ui(self):
        self.clear_widgets()
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Configuracion del Servidor",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        root.add_widget(toolbar)

        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(16),
        )

        content.add_widget(MDLabel(
            text="Direccion del servidor",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
        ))

        content.add_widget(MDLabel(
            text="Ejemplo: http://192.168.1.87:8000",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(25),
        ))

        self.f_url = MDTextField(
            hint_text="URL del servidor",
            text=get_api(),
            size_hint_y=None,
            height=dp(50),
            mode="rectangle",
        )
        content.add_widget(self.f_url)

        btn_clear = MDFlatButton(
            text="LIMPIAR CAMPO",
            size_hint=(1, None),
            height=dp(36),
        )
        btn_clear.bind(on_release=lambda x: setattr(self.f_url, 'text', ''))
        content.add_widget(btn_clear)

        btn_save = MDRaisedButton(
            text="GUARDAR Y PROBAR",
            size_hint=(1, None),
            height=dp(55),
        )
        btn_save.bind(on_release=lambda x: self.save_and_test())
        content.add_widget(btn_save)

        self.status_label = MDLabel(
            text="",
            halign="center",
            size_hint_y=None,
            height=dp(50),
            font_style="H6",
        )
        content.add_widget(self.status_label)

        content.add_widget(MDLabel(
            text="IP actual: " + get_api(),
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(30),
        ))

        root.add_widget(content)
        self.add_widget(root)

    def save_and_test(self):
        url = self.f_url.text.strip().rstrip("/")
        if not url:
            self.status_label.text = "Escribe una URL valida"
            return
        save_api(url)
        self.status_label.text = "Probando conexion..."
        threading.Thread(target=self.test_connection, args=(url,), daemon=True).start()

    def test_connection(self, url):
        try:
            r = requests.get(f"{url}/", timeout=5)
            if r.ok:
                self.update_status("Conexion exitosa")
            else:
                self.update_status("Servidor no responde")
        except:
            self.update_status("No se pudo conectar")

    @mainthread
    def update_status(self, text):
        self.status_label.text = text

    def go_back(self):
        self.manager.current = "home"