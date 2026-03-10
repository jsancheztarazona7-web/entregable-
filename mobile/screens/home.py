import requests
import threading
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.clock import Clock, mainthread
from screens.settings import get_api

class HomeScreen(MDScreen):

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.build_ui(), 0.1)

    def build_ui(self):
        self.clear_widgets()
        root = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(title="QuotePro", elevation=4)
        root.add_widget(toolbar)

        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(20),
            size_hint=(1, 1),
        )

        content.add_widget(MDLabel(
            text="Panel Principal",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(60),
        ))

        btn_products = MDRaisedButton(
            text="PRODUCTOS",
            size_hint=(1, None),
            height=dp(60),
            font_size="18sp",
        )
        btn_products.bind(on_release=lambda x: setattr(self.manager, 'current', 'products'))

        btn_providers = MDRaisedButton(
            text="PROVEEDORES",
            size_hint=(1, None),
            height=dp(60),
            font_size="18sp",
        )
        btn_providers.bind(on_release=lambda x: setattr(self.manager, 'current', 'providers'))

        btn_quotes = MDRaisedButton(
            text="COTIZACIONES",
            size_hint=(1, None),
            height=dp(60),
            font_size="18sp",
        )
        btn_quotes.bind(on_release=lambda x: setattr(self.manager, 'current', 'quotes'))

        btn_settings = MDFlatButton(
            text="Configurar servidor",
            size_hint=(1, None),
            height=dp(40),
        )
        btn_settings.bind(on_release=lambda x: setattr(self.manager, 'current', 'settings'))

        content.add_widget(btn_products)
        content.add_widget(btn_providers)
        content.add_widget(btn_quotes)
        content.add_widget(btn_settings)

        self.summary_label = MDLabel(
            text="Conectando...",
            halign="center",
            size_hint_y=None,
            height=dp(50),
        )
        content.add_widget(self.summary_label)
        root.add_widget(content)
        self.add_widget(root)

        threading.Thread(target=self.load_summary, daemon=True).start()

    def load_summary(self):
        try:
            api = get_api()
            n_prod = len(requests.get(f"{api}/products/",  timeout=5).json())
            n_prov = len(requests.get(f"{api}/providers/", timeout=5).json())
            n_quot = len(requests.get(f"{api}/quotes/",    timeout=5).json())
            self.update_summary(f"Productos: {n_prod}  |  Proveedores: {n_prov}  |  Cotizaciones: {n_quot}")
        except:
            self.update_summary("Sin conexion al servidor")

    @mainthread
    def update_summary(self, text):
        self.summary_label.text = text