import requests
from kivymd.uix.screen        import MDScreen
from kivymd.uix.boxlayout     import MDBoxLayout
from kivymd.uix.scrollview    import MDScrollView
from kivymd.uix.label         import MDLabel
from kivymd.uix.button        import MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar       import MDTopAppBar
from kivymd.uix.textfield     import MDTextField
from kivymd.uix.dialog        import MDDialog
from kivymd.uix.list          import MDList, TwoLineIconListItem, IconLeftWidget
from kivy.metrics             import dp
from kivy.clock               import Clock
from screens.settings         import get_api

class ProvidersScreen(MDScreen):

    def on_enter(self):
        self.dialog = None
        self.clear_widgets()
        self.build_ui()
        Clock.schedule_once(lambda dt: self.load_providers(), 0.3)

    def build_ui(self):
        self.root_layout = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title               = "Proveedores",
            elevation           = 4,
            left_action_items   = [["arrow-left", lambda x: self.go_back()]],
            right_action_items  = [["plus", lambda x: self.open_form()]],
        )
        self.root_layout.add_widget(toolbar)
        scroll = MDScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)
        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

    def load_providers(self):
        self.list_container.clear_widgets()
        try:
            r = requests.get(f"{get_api()}/providers/", timeout=5)
            providers = r.json()
        except:
            providers = []

        if not providers:
            self.list_container.add_widget(MDLabel(
                text="No hay proveedores registrados",
                halign="center",
                padding=[0, dp(40)],
            ))
            return

        for p in providers:
            item = TwoLineIconListItem(
                text           = f"[{p['code']}] {p['name']}",
                secondary_text = f"Tel: {p.get('phone','—')}  |  NIT: {p.get('nit','—')}",
                on_release     = lambda x, prov=p: self.open_detail(prov),
            )
            icon = IconLeftWidget(icon="truck")
            item.add_widget(icon)
            self.list_container.add_widget(item)

    def open_form(self, provider=None):
        self.edit_provider = provider
        self.f_code    = MDTextField(hint_text="Codigo *",      text=provider["code"]                     if provider else "")
        self.f_name    = MDTextField(hint_text="Nombre *",      text=provider["name"]                     if provider else "")
        self.f_contact = MDTextField(hint_text="Contacto",      text=provider.get("contact_name","")      if provider else "")
        self.f_email   = MDTextField(hint_text="Email",         text=provider.get("email","")             if provider else "")
        self.f_phone   = MDTextField(hint_text="Telefono",      text=provider.get("phone","")             if provider else "")
        self.f_nit     = MDTextField(hint_text="NIT",           text=provider.get("nit","")               if provider else "")
        self.f_days    = MDTextField(hint_text="Dias entrega",  text=str(provider.get("delivery_days",1)) if provider else "1", input_filter="int")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(420))
        for field in [self.f_code, self.f_name, self.f_contact, self.f_email, self.f_phone, self.f_nit, self.f_days]:
            content.add_widget(field)

        self.dialog = MDDialog(
            title       = "Editar Proveedor" if provider else "Nuevo Proveedor",
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CANCELAR",  on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_release=lambda x: self.save_provider()),
            ],
        )
        self.dialog.open()

    def save_provider(self):
        data = {
            "code"         : self.f_code.text.strip(),
            "name"         : self.f_name.text.strip(),
            "contact_name" : self.f_contact.text.strip(),
            "email"        : self.f_email.text.strip(),
            "phone"        : self.f_phone.text.strip(),
            "nit"          : self.f_nit.text.strip(),
            "delivery_days": int(self.f_days.text or 1),
            "payment_terms": 30,
        }
        if not data["code"] or not data["name"]:
            return
        try:
            if self.edit_provider:
                requests.put(f"{get_api()}/providers/{self.edit_provider['id']}", json=data, timeout=5)
            else:
                requests.post(f"{get_api()}/providers/", json=data, timeout=5)
        except:
            pass
        if self.dialog:
            self.dialog.dismiss()
        Clock.schedule_once(lambda dt: self.load_providers(), 0.2)

    def open_detail(self, provider):
        content = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None, height=dp(200))
        for label in [
            f"Codigo:       {provider['code']}",
            f"Contacto:     {provider.get('contact_name','—')}",
            f"Email:        {provider.get('email','—')}",
            f"Telefono:     {provider.get('phone','—')}",
            f"NIT:          {provider.get('nit','—')}",
            f"Dias entrega: {provider.get('delivery_days',1)}",
        ]:
            content.add_widget(MDLabel(text=label, size_hint_y=None, height=dp(28)))

        self.dialog = MDDialog(
            title       = provider["name"],
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CERRAR",   on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="EDITAR", on_release=lambda x: self.edit_prov(provider)),
            ],
        )
        self.dialog.open()

    def edit_prov(self, provider):
        if self.dialog:
            self.dialog.dismiss()
        self.open_form(provider)

    def go_back(self):
        self.manager.current = "home"