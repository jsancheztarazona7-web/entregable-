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

class QuotesScreen(MDScreen):

    def on_enter(self):
        self.dialog        = None
        self.quote_items   = []
        self.products_data = []
        self.clear_widgets()
        self.build_ui()
        Clock.schedule_once(lambda dt: self.load_quotes(), 0.3)

    def build_ui(self):
        self.root_layout = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(
            title              = "Cotizaciones",
            elevation          = 4,
            left_action_items  = [["arrow-left", lambda x: self.go_back()]],
            right_action_items = [["plus",       lambda x: self.open_new_quote()]],
        )
        self.root_layout.add_widget(toolbar)
        scroll = MDScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)
        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

    def load_quotes(self):
        self.list_container.clear_widgets()
        try:
            r      = requests.get(f"{get_api()}/quotes/", timeout=5)
            quotes = r.json()
        except:
            quotes = []

        if not quotes:
            self.list_container.add_widget(MDLabel(
                text="No hay cotizaciones registradas",
                halign="center",
                padding=[0, dp(40)],
            ))
            return

        for q in quotes:
            item = TwoLineIconListItem(
                text           = f"{q['quote_number']} - {q['client_name']}",
                secondary_text = f"Total: ${float(q['total_amount']):,.0f}  |  {q['status']}",
                on_release     = lambda x, quote=q: self.open_detail(quote),
            )
            icon = IconLeftWidget(icon="file-document")
            item.add_widget(icon)
            self.list_container.add_widget(item)

    def open_new_quote(self):
        self.quote_items = []
        try:
            r = requests.get(f"{get_api()}/products/", timeout=5)
            self.products_data = r.json()
        except:
            self.products_data = []

        self.f_client_name  = MDTextField(hint_text="Nombre cliente *")
        self.f_client_email = MDTextField(hint_text="Email cliente")
        self.f_client_phone = MDTextField(hint_text="Telefono cliente")
        self.f_notes        = MDTextField(hint_text="Observaciones")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(260))
        for f in [self.f_client_name, self.f_client_email, self.f_client_phone, self.f_notes]:
            content.add_widget(f)

        self.dialog = MDDialog(
            title       = "Nueva Cotizacion - Cliente",
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CANCELAR",        on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="AGREGAR ITEMS", on_release=lambda x: self.open_add_item()),
            ],
        )
        self.dialog.open()

    def open_add_item(self):
        if self.dialog:
            self.dialog.dismiss()
        if not self.products_data:
            return

        prod_lines = "\n".join([
            f"  ID {p['id']}: {p['name']} ({p['unit']}) - Mejor: "
            f"${p['best_price']['price']:,.0f} ({p['best_price']['provider_name']})"
            if p.get('best_price') else
            f"  ID {p['id']}: {p['name']} ({p['unit']}) - Sin precio"
            for p in self.products_data
        ])

        self.f_prod_id  = MDTextField(hint_text="ID Producto *",           input_filter="int")
        self.f_qty      = MDTextField(hint_text="Cantidad *",               input_filter="float")
        self.f_use_best = MDTextField(hint_text="Usar mejor precio? (s/n)", text="s")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(380))
        content.add_widget(MDLabel(text="Productos disponibles:", size_hint_y=None, height=dp(25), font_style="Caption"))
        content.add_widget(MDLabel(text=prod_lines,               size_hint_y=None, height=dp(160), font_style="Caption"))
        for f in [self.f_prod_id, self.f_qty, self.f_use_best]:
            content.add_widget(f)

        self.dialog = MDDialog(
            title       = "Agregar Producto",
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="FINALIZAR",         on_release=lambda x: self.finish_quote()),
                MDRaisedButton(text="+ OTRO PRODUCTO", on_release=lambda x: self.add_item()),
            ],
        )
        self.dialog.open()

    def add_item(self):
        try:
            prod_id  = int(self.f_prod_id.text)
            qty      = float(self.f_qty.text)
            use_best = self.f_use_best.text.strip().lower() in ["s","si","y","yes",""]
        except:
            return

        product = next((p for p in self.products_data if p["id"] == prod_id), None)
        if not product:
            return

        if use_best and product.get("best_price"):
            best        = product["best_price"]
            provider_id = best["provider_id"]
            price       = best["price"]
            tax         = best.get("tax_percent", 19)
        elif product.get("prices"):
            first       = product["prices"][0]
            provider_id = first["provider_id"]
            price       = first["price"]
            tax         = first.get("tax_percent", 19)
        else:
            return

        self.quote_items.append({
            "product_id"  : prod_id,
            "provider_id" : provider_id,
            "quantity"    : qty,
            "unit_price"  : price,
            "tax_percent" : tax,
            "product_name": product["name"],
            "unit"        : product["unit"],
        })
        self.f_prod_id.text  = ""
        self.f_qty.text      = ""
        self.f_use_best.text = "s"

    def finish_quote(self):
        if self.f_prod_id.text.strip():
            self.add_item()
        if self.dialog:
            self.dialog.dismiss()
        if not self.quote_items:
            return
        self.open_quote_summary()

    def open_quote_summary(self):
        total = sum(
            i["quantity"] * i["unit_price"] * (1 + i["tax_percent"] / 100)
            for i in self.quote_items
        )
        lines = ""
        for i in self.quote_items:
            subtotal = i["quantity"] * i["unit_price"] * (1 + i["tax_percent"] / 100)
            lines += f"- {i['product_name']}\n  {i['quantity']} {i['unit']} x ${i['unit_price']:,.0f} = ${subtotal:,.0f}\n\n"

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(340))
        content.add_widget(MDLabel(text=lines, size_hint_y=None, height=dp(260), font_style="Body2"))
        content.add_widget(MDLabel(
            text             = f"TOTAL: ${total:,.0f}",
            font_style       = "H6",
            halign           = "right",
            size_hint_y      = None,
            height           = dp(40),
            theme_text_color = "Custom",
            text_color       = [0.1, 0.4, 0.1, 1],
        ))

        self.dialog = MDDialog(
            title       = f"Resumen - {self.f_client_name.text}",
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CANCELAR",  on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_release=lambda x: self.save_quote()),
            ],
        )
        self.dialog.open()

    def save_quote(self):
        data = {
            "client_name"  : self.f_client_name.text.strip(),
            "client_email" : self.f_client_email.text.strip(),
            "client_phone" : self.f_client_phone.text.strip(),
            "notes"        : self.f_notes.text.strip(),
            "items"        : [{
                "product_id" : i["product_id"],
                "provider_id": i["provider_id"],
                "quantity"   : i["quantity"],
                "unit_price" : i["unit_price"],
                "tax_percent": i["tax_percent"],
            } for i in self.quote_items],
        }
        try:
            requests.post(f"{get_api()}/quotes/", json=data, timeout=5)
        except:
            pass
        if self.dialog:
            self.dialog.dismiss()
        self.quote_items = []
        Clock.schedule_once(lambda dt: self.load_quotes(), 0.2)

    def open_detail(self, quote):
        try:
            r      = requests.get(f"{get_api()}/quotes/{quote['id']}", timeout=5)
            detail = r.json()
        except:
            return

        lines = ""
        for i in detail.get("items", []):
            lines += (
                f"- {i['product_name']} ({i['unit']})\n"
                f"  Proveedor: {i['provider_name']}\n"
                f"  {i['quantity']} x ${i['unit_price']:,.0f} = ${i['subtotal']:,.0f}\n\n"
            )

        content = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None, height=dp(380))
        content.add_widget(MDLabel(text=f"Cliente: {detail['client_name']}",        size_hint_y=None, height=dp(28)))
        content.add_widget(MDLabel(text=f"Tel:     {detail.get('client_phone','—')}", size_hint_y=None, height=dp(24)))
        content.add_widget(MDLabel(text=f"Estado:  {detail['status']}",              size_hint_y=None, height=dp(24)))
        content.add_widget(MDLabel(text="—" * 30,                                    size_hint_y=None, height=dp(20)))
        content.add_widget(MDLabel(text=lines,                                       size_hint_y=None, height=dp(220)))
        content.add_widget(MDLabel(
            text             = f"TOTAL: ${float(detail['total_amount']):,.0f}",
            font_style       = "H6",
            halign           = "right",
            size_hint_y      = None,
            height           = dp(36),
            theme_text_color = "Custom",
            text_color       = [0.1, 0.4, 0.1, 1],
        ))

        self.dialog = MDDialog(
            title       = detail["quote_number"],
            type        = "custom",
            content_cls = content,
            buttons     = [
                MDFlatButton(text="CERRAR", on_release=lambda x: self.dialog.dismiss()),
            ],
        )
        self.dialog.open()

    def go_back(self):
        self.manager.current = "home"