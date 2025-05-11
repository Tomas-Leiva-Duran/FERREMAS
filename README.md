# FERREMAS

FERREMAS es una aplicación web construida con Python y Flask, inspirada en el sitio original de Ferremax.cl. Su objetivo es servir como base para una ferretería online con vistas a integración futura con APIs y aplicaciones móviles.

## 🚀 Tecnologías Usadas

- Python 3
- Flask
- HTML / CSS
- Jinja2 (para plantillas)
- JSON (para la API)

## 🧰 Funcionalidades

- Página de inicio
- Catálogo de productos
- Página de contacto
- API REST (GET y POST de productos)

## 📦 Estructura

```
ferremas/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── productos.html
│   └── contacto.html
├── static/
│   └── style.css
└── README.md
```

## 📡 Rutas API

- `GET /api/productos` → Devuelve la lista de productos.
- `POST /api/productos` → Agrega un producto nuevo (requiere JSON).

## ⚙️ Instalación y Ejecución

```bash
pip install flask
python app.py
```

Visita `http://127.0.0.1:5000` en tu navegador.

## 📝 Licencia

MIT