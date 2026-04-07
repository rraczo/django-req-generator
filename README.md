# django-req-generator 🚀

**Generador inteligente de `requirements.txt` / Smart `requirements.txt` generator**

---

## 🇪🇸 Español

### Descripción
Este plugin para Django sirve para empaquetar tu proyecto e instalarlo de forma limpia en otros entornos (Docker, Servidores de Producción, CI/CD). Está específicamente diseñado para manejar proyectos Django complejos donde no basta con un simple `pip freeze`.

### Características Principales
- 🔍 **Análisis Estático (AST)**: Detecta imports reales en todo el árbol de tu código fuente.
- 🧩 **Inspección Profunda de Django**: Analiza `INSTALLED_APPS`, `MIDDLEWARE`, `DATABASES` (detecta drivers como `oracledb`), y `CACHES` (detecta `django-redis` y `pymemcache`).
- 🧹 **Limpieza Automática**: Filtra la librería estándar de Python y tus propios módulos locales (`apps`, `models`, `serializers`, etc.).
- 🔗 **Resolución Dinámica PyPI**: No usa mapeos manuales fallidos; pregunta directamente a la API de PyPI para encontrar el paquete correcto.
- 🤖 **Auto-curación Interactiva**: Durante la validación, si detecta un módulo faltante (`ModuleNotFoundError`), te pregunta si quieres añadirlo y reintenta la validación en caliente.
- 🧪 **Validación en Venv**: Crea un entorno virtual temporal para asegurar que el archivo generado permite que el proyecto arranque.
- 🌎 **Multilingüe**: Soporta comandos y mensajes en Español e Inglés.

### Uso
```bash
# Generación estándar con backup automático
python manage.py generate_reqs

# Generación con validación y settings específicos
python manage.py generate_reqs --validate --settings=mi_proyecto.settings_docker

# Modo Desarrollo (instala el plugin desde código fuente en la validación)
python manage.py generate_reqs --validate -d /ruta/al/plugin
```

---

## 🇺🇸 English

### Description
This Django plugin is designed to package your project and install it cleanly in other environments (Docker, Production Servers, CI/CD). It is specifically built for complex Django projects where a simple `pip freeze` isn't enough.

### Key Features
- 🔍 **Static Analysis (AST)**: Deep-scans your entire source code to detect actual imports.
- 🧩 **Deep Django Inspection**: Analyzes `INSTALLED_APPS`, `MIDDLEWARE`, `DATABASES` (detects drivers like `oracledb`), and `CACHES` (detects `django-redis` and `pymemcache`).
- 🧹 **Automatic Cleanup**: Filters out Python's standard library and your own local modules (`apps`, `models`, `serializers`, etc.).
- 🔗 **Dynamic PyPI Resolution**: Replaces outdated manual mappings by querying the PyPI API directly for the correct package name.
- 🤖 **Interactive Self-Healing**: During validation, if a missing module is found (`ModuleNotFoundError`), it asks if you want to add it and retries the validation on the fly.
- 🧪 **Venv Validation**: Creates a temporary virtual environment to ensure the generated file allows the project to start.
- 🌎 **Multilingual**: Supports commands and console messages in both Spanish and English.

### Usage
```bash
# Standard generation with automatic backup
python manage.py generate_reqs

# Generation with validation and specific settings
python manage.py generate_reqs --validate --settings=my_project.settings_docker

# Development Mode (installs plugin from source during validation)
python manage.py generate_reqs --validate -d /path/to/plugin
```

---

**Made with ❤️ and AI Collaboration | Creado con ❤️ y el apoyo de IA**
