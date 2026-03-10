import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config
Config.set('graphics', 'resizable', '1')

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from screens.home      import HomeScreen
from screens.products  import ProductsScreen
from screens.providers import ProvidersScreen
from screens.quotes    import QuotesScreen
from screens.settings  import SettingsScreen

class QuoteProApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette  = "BlueGray"
        self.theme_cls.accent_palette   = "Amber"
        self.theme_cls.theme_style      = "Light"
        self.theme_cls.primary_hue      = "800"
        self.title                      = "QuotePro"

        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProductsScreen(name="products"))
        sm.add_widget(ProvidersScreen(name="providers"))
        sm.add_widget(QuotesScreen(name="quotes"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm

if __name__ == "__main__":
    QuoteProApp().run()