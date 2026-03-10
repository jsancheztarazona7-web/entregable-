# QuotePro — Sistema de Cotizaciones

Aplicación móvil Android para gestionar cotizaciones de productos con múltiples proveedores. Permite registrar productos, asignar precios por proveedor, seleccionar automáticamente el mejor precio y generar cotizaciones detalladas.

---

## Requisitos del sistema

- Windows 10 / 11
- Python 3.11 (no usar 3.12 o superior)
- Visual Studio Code
- SQL Server Express 2019 o 2022
- SQL Server Management Studio (SSMS)
- Git
- WSL2 con Ubuntu (para compilar el APK)
- Celular Android con versión 5.0 o superior

---

## Estructura del proyecto

```
QuotePro/
├── backend/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── products.py
│   │   ├── providers.py
│   │   └── quotes.py
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── mobile/
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── products.py
│   │   ├── providers.py
│   │   ├── quotes.py
│   │   └── settings.py
│   └── main.py
├── database/
│   └── schema.sql
├── .env
└── requirements.txt
```

---

## Instalación paso a paso

### 1. Clonar o descargar el proyecto

Coloca la carpeta `QuotePro` en:
```
C:\Users\TU_USUARIO\Documents\QuotePro
```

### 2. Crear entorno virtual con Python 3.11

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
py -3.11 -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```powershell
pip install kivy==2.3.0 kivymd==1.2.0 pillow==10.4.0
pip install fastapi uvicorn sqlalchemy pyodbc reportlab python-dotenv
```

### 4. Configurar la base de datos

Abre SQL Server y ejecuta:

```powershell
sqlcmd -S localhost\SQLEXPRESS -Q "CREATE DATABASE QuoteProDB"
sqlcmd -S localhost\SQLEXPRESS -d QuoteProDB -i database\schema.sql
```

### 5. Configurar el archivo .env

Edita el archivo `.env` en la raíz del proyecto:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=QuoteProDB
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED=yes
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Uso diario

### Iniciar el backend

Cada vez que vayas a usar la app, abre PowerShell y ejecuta:

```powershell
cd C:\Users\TU_USUARIO\Documents\QuotePro
venv\Scripts\activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Deja esta ventana abierta mientras usas la app.

### Verificar que el backend funciona

Abre el navegador y entra a:
```
http://localhost:8000
```
Debe mostrar: `{"message": "QuotePro API funcionando"}`

### Iniciar la app en escritorio (para pruebas)

Abre una segunda terminal y ejecuta:

```powershell
cd C:\Users\TU_USUARIO\Documents\QuotePro\mobile
venv\Scripts\activate
python main.py
```

---

## Configurar la app en el celular

### Primera vez

1. Instala el archivo `quotepro.apk` en tu celular Android.
2. Asegúrate que el celular esté conectado al **mismo WiFi** que tu PC.
3. En PowerShell verifica tu IP:
   ```powershell
   ipconfig | findstr "IPv4"
   ```
   Anota la IP bajo **Wi-Fi**, ejemplo: `192.168.1.87`
4. Abre la app en el celular.
5. Toca **Configurar servidor**.
6. Toca **LIMPIAR CAMPO** y escribe:
   ```
   http://192.168.1.87:8000
   ```
7. Toca **GUARDAR Y PROBAR** — debe mostrar `Conexion exitosa`.

### Cuando cambies de red WiFi

1. Verifica la nueva IP con `ipconfig | findstr "IPv4"`.
2. Abre la app → **Configurar servidor** → actualiza la IP.
3. Toca **GUARDAR Y PROBAR**.

---

## Funcionalidades

### Proveedores
- Registrar proveedores con código, nombre, contacto, email, teléfono y NIT.
- Ver listado de todos los proveedores activos.
- Editar información de un proveedor existente.

### Productos
- Registrar productos con código, nombre, descripción, unidad de medida y marca.
- Asignar precios por proveedor a cada producto (con porcentaje de IVA).
- Ver el mejor precio disponible para cada producto automáticamente.

### Cotizaciones
- Crear cotizaciones para clientes con nombre, email y teléfono.
- Agregar múltiples productos a cada cotización.
- La app selecciona automáticamente el mejor precio disponible.
- Ver resumen detallado con subtotales, IVA y total.
- Historial de cotizaciones anteriores con detalle completo.

---

## Compilar el APK (Android)

Requiere WSL2 con Ubuntu instalado en Windows.

### En Ubuntu (WSL2)

```bash
# Instalar dependencias
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev

# Instalar Buildozer
pip3 install --user --break-system-packages buildozer cython==0.29.33
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc && source ~/.bashrc

# Copiar proyecto
cp -r /mnt/c/Users/TU_USUARIO/Documents/QuotePro/mobile ~/QuotePro
cd ~/QuotePro

# Actualizar IP en archivos
sed -i "s|http://127.0.0.1:8000|http://TU_IP:8000|g" ~/QuotePro/screens/*.py

# Inicializar y compilar
buildozer init
buildozer android debug
```

### Copiar APK a Windows

```bash
cp ~/QuotePro/bin/quotepro-1.0-arm64-v8a-debug.apk /mnt/c/Users/TU_USUARIO/Documents/QuotePro/quotepro.apk
```

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `Sin conexion al servidor` | Verifica que el backend esté corriendo y que la IP esté configurada correctamente en la app |
| `No hay proveedores registrados` | Configura la IP del servidor en la app y verifica que el celular esté en el mismo WiFi |
| Backend no inicia | Verifica que el servicio `SQL Server (SQLEXPRESS)` esté corriendo en `services.msc` |
| Error al instalar APK | Activa `Instalar apps desconocidas` en Ajustes → Seguridad del celular |
| Puerto 8000 bloqueado | Ejecuta en PowerShell como Administrador: `New-NetFirewallRule -DisplayName "QuotePro" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow` |

---

## Documentación de la API

Con el backend corriendo, accede a la documentación interactiva en:
```
http://localhost:8000/docs
```

### Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/products/` | Listar productos |
| POST | `/products/` | Crear producto |
| PUT | `/products/{id}` | Actualizar producto |
| POST | `/products/{id}/prices` | Agregar precio a producto |
| GET | `/providers/` | Listar proveedores |
| POST | `/providers/` | Crear proveedor |
| PUT | `/providers/{id}` | Actualizar proveedor |
| GET | `/quotes/` | Listar cotizaciones |
| POST | `/quotes/` | Crear cotización |
| GET | `/quotes/{id}` | Ver detalle de cotización |

---

## Tecnologías utilizadas

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, pyodbc
- **Base de datos:** SQL Server 2022 Express
- **App móvil:** Python 3.11, Kivy 2.3.0, KivyMD 1.2.0
- **Compilación APK:** Buildozer, python-for-android
- **IDE:** Visual Studio Code

---

## Notas importantes

- El backend debe estar corriendo en el PC para que la app funcione.
- El celular y el PC deben estar en la misma red WiFi.
- Si cambias de red, actualiza la IP en **Configurar servidor** dentro de la app.
- La base de datos se almacena localmente en SQL Server. Haz copias de seguridad periódicas desde SSMS.
