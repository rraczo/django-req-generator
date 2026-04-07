from django.conf import settings


def inspect_settings():
    """Extrae nombres de módulos de las configuraciones de Django."""
    found_modules = set()

    # Si estamos inspeccionando esto, Django DEBE estar
    found_modules.add("django")

    # 1. INSTALLED_APPS
    apps = getattr(settings, "INSTALLED_APPS", [])
    for app in apps:
        if isinstance(app, str):
            app = app.strip()
            if app:
                found_modules.add(app.split(".")[0])

    # 2. MIDDLEWARE
    middlewares = getattr(settings, "MIDDLEWARE", [])
    for middleware in middlewares:
        found_modules.add(middleware.split(".")[0])

    # 3. CACHES (Detectar django-redis, etc.)
    caches = getattr(settings, "CACHES", {})
    for cache_config in caches.values():
        backend = cache_config.get("BACKEND", "")
        if backend:
            found_modules.add(backend.split(".")[0])

    # 4. AUTHENTICATION_BACKENDS
    auth_backends = getattr(settings, "AUTHENTICATION_BACKENDS", [])
    for auth in auth_backends:
        found_modules.add(auth.split(".")[0])

    # 5. DATABASES (Motores internos de Django y sus drivers)
    databases = getattr(settings, "DATABASES", {})
    db_drivers = {
        "django.db.backends.postgresql": "psycopg2", # o psycopg
        "django.db.backends.mysql": "mysqlclient",
        "django.db.backends.oracle": "oracledb",
        "django.db.backends.sqlite3": None, # stdlib
    }

    for db_config in databases.values():
        engine = db_config.get("ENGINE", "")
        if engine:
            if engine in db_drivers:
                driver = db_drivers[engine]
                if driver:
                    found_modules.add(driver)
            else:
                # Si es un motor de terceros
                parts = engine.split(".")
                if len(parts) > 1 and parts[0] != "django":
                    found_modules.add(parts[0])

    return found_modules
