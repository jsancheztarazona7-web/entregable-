import requests
from kivymd.uix.screen        import MDScreen
from kivymd.uix.boxlayout     import MDBoxLayout
from kivymd.uix.scrollview    import MDScrollView
from kivymd.uix.label         import MDLabel
from kivymd.uix.button        import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.toolbar       import MDTopAppBar
from kivymd.uix.textfield     import MDTextField
from kivymd.uix.dialog        import MDDialog
from kivymd.uix.list          import MDList, TwoLineIconListItem, IconLeftWidget
from kivy.metrics             import dp
from kivy.clock               import Clock
from screens.settings         import get_api

class ProductsScreen(MDScreen):

    def on_enter(self):
        self.dialog = None
        self.clear_widgets()
        self.build_ui()
        Clock.schedule_once(lambda dt: self.load_products(), 0.3)

    def build_ui(self):
        self.root_layout = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title               = "Productos",
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

    def load_products(self):
        self.list_container.clear_widgets()
        try:
            r = requests.get(f"{get_api()}/products/", timeout=5)
            products = r.json()
        except:
            products = []

        if not products:
            self.list_container.add_widget(MDLabel(
                text    = "No hay productos registrados",
                halign  = "center",
                padding = [0, dp(40)],
            ))
            return

        for p in products:
            best = p.get("best_price")
            price_text = f"Mejor precio: ${best['price']:,.0f} - {best['provider_name']}" if best else "Sin precio registrado"
            item = TwoLineIconListItem(
                text           = f"[{p['code']}] {p['name']} ({p['unit']})",
                secondary_text = price_text,
                on_release     = lambda x, prod=p: self.open_detail(prod),
            )
            icon = IconLeftWidget(icon="package-variant")
            item.add_widget(icon)
            self.list_container.add_widget(item)

    def open_form(self, product=None):
        self.edit_product = product
        self.f_code  = MDTextField(hint_text="Codigo *",    text=product["code"]               if product else "")
        self.f_name  = MDTextField(hint_text="Nombre *",    text=product["name"]               if product else "")
        self.f_desc  = MDTextField(hint_text="Descripcion", text=product.get("description","") if product else "")
        self.f_unit  = MDTextField(hint_text="Unidad",      text=product["unit"]               if product else "UND")
        self.f_brand = MDTextField(hint_text="Marca",       text=product.get("brand","")       if product else "")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(320))
        for field in [self.f_code, self.f_name, self.f_desc, self.f_unit, self.f_brand]:
            content.add_widget(field)

        self.dialog = MDDialog(
            title       = "Editar Producto" if product else "Nuevo Producto",
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CANCELAR",  on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_release=lambda x: self.save_product()),
            ],
        )
        self.dialog.open()

    def save_product(self):
        data = {
            "code"       : self.f_code.text.strip(),
            "name"       : self.f_name.text.strip(),
            "description": self.f_desc.text.strip(),
            "unit"       : self.f_unit.text.strip() or "UND",
            "brand"      : self.f_brand.text.strip(),
        }
        if not data["code"] or not data["name"]:
            return
        try:
            if self.edit_product:
                requests.put(f"{get_api()}/products/{self.edit_product['id']}", json=data, timeout=5)
            else:
                requests.post(f"{get_api()}/products/", json=data, timeout=5)
        except:
            pass
        if self.dialog:
            self.dialog.dismiss()
        Clock.schedule_once(lambda dt: self.load_products(), 0.2)

    def open_detail(self, product):
        prices = product.get("prices", [])
        price_lines = "\n".join(
            [f"  {pr['provider_name']}: ${pr['price']:,.0f} + {pr['tax_percent']}% IVA" for pr in prices]
        ) or "  Sin precios registrados"

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(260))
        content.add_widget(MDLabel(text=f"Codigo: {product['code']}",          size_hint_y=None, height=dp(30)))
        content.add_widget(MDLabel(text=f"Unidad: {product['unit']}",          size_hint_y=None, height=dp(30)))
        content.add_widget(MDLabel(text=f"Marca:  {product.get('brand','—')}",  size_hint_y=None, height=dp(30)))
        content.add_widget(MDLabel(text="Precios por proveedor:",               size_hint_y=None, height=dp(30)))
        content.add_widget(MDLabel(text=price_lines,                            size_hint_y=None, height=dp(120)))

        self.dialog = MDDialog(
            title       = product["name"],
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CERRAR",     on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="EDITAR",   on_release=lambda x: self.edit_prod(product)),
                MDRaisedButton(text="+ PRECIO", on_release=lambda x: self.open_price_form(product)),
            ],
        )
        self.dialog.open()

    def edit_prod(self, product):
        if self.dialog:
            self.dialog.dismiss()
        self.open_form(product)

    def open_price_form(self, product):
        if self.dialog:
            self.dialog.dismiss()
        try:
            r = requests.get(f"{get_api()}/providers/", timeout=5)
            providers = r.json()
        except:
            providers = []

        self.price_product = product
        self.f_price       = MDTextField(hint_text="Precio sin IVA *", input_filter="float")
        self.f_tax         = MDTextField(hint_text="% IVA (default 19)", text="19", input_filter="float")
        self.f_provider_id = MDTextField(hint_text="ID Proveedor *", input_filter="int")

        prov_text = "\n".join([f"  ID {p['id']}: {p['name']}" for p in providers]) or "Sin proveedores"

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(280))
        content.add_widget(MDLabel(text="Proveedores disponibles:", size_hint_y=None, height=dp(25)))
        content.add_widget(MDLabel(text=prov_text,                  size_hint_y=None, height=dp(80)))
        for field in [self.f_provider_id, self.f_price, self.f_tax]:
            content.add_widget(field)

        self.dialog = MDDialog(
            title       = f"Agregar Precio - {product['name']}",
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CANCELAR",  on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_release=lambda x: self.save_price()),
            ],
        )
        self.dialog.open()

    def save_price(self):
        try:
            data = {
                "provider_id": int(self.f_provider_id.text),
                "price"      : float(self.f_price.text),
                "tax_percent": float(self.f_tax.text or 19),
            }
            requests.post(f"{get_api()}/products/{self.price_product['id']}/prices", json=data, timeout=5)
        except:
            pass
        if self.dialog:
            self.dialog.dismiss()
        Clock.schedule_once(lambda dt: self.load_products(), 0.2)

    def go_back(self):
        self.manager.current = "home"