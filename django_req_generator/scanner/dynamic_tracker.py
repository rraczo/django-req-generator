import builtins


_used_modules = set()
_original_import = builtins.__import__


def tracking_import(name, *args, **kwargs):
    """Hook que registra el nombre del módulo raíz importado."""
    if name:
        root_module = name.split(".")[0]
        _used_modules.add(root_module)
    return _original_import(name, *args, **kwargs)


def start_tracking():
    """Activa el Hook de importación."""
    builtins.__import__ = tracking_import


def stop_tracking():
    """Detiene el Hook de importación y restaura el original."""
    builtins.__import__ = _original_import


def get_tracked_modules():
    """Devuelve la lista de módulos registrados."""
    return _used_modules


def save_tracked_modules(file_path=".tracked_modules.json"):
    """Guarda los módulos rastreados en un archivo JSON."""
    import json
    with open(file_path, "w") as f:
        json.dump(list(_used_modules), f)


def load_tracked_modules(file_path=".tracked_modules.json"):
    """Carga módulos rastreados desde un archivo JSON."""
    import json
    import os
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return set(json.load(f))
    return set()
