import sys
import os
import importlib.metadata as md

def filter_standard_library(module_names):
    """Filtra módulos que pertenecen a la librería estándar de Python."""
    if sys.version_info >= (3, 10):
        stdlib_names = sys.stdlib_module_names
    else:
        from distutils.sysconfig import get_python_lib
        stdlib_names = set(os.listdir(get_python_lib(standard_lib=True)))

    return {name for name in module_names if name not in stdlib_names}


def filter_local_modules(module_names, project_root):
    """
    Filtra módulos locales pero prioriza los de Pip si hay coincidencia de nombre.
    """
    # 1. Identificar módulos instalados en Pip (para evitar falsos positivos locales)
    pkg_dist = md.packages_distributions()
    
    # 2. Identificar todos los nombres locales del proyecto (carpetas y archivos .py)
    local_names_found = set()
    root_name = os.path.basename(project_root.rstrip(os.path.sep))
    local_names_found.add(root_name)

    ignore_dirs = {".git", "venv", ".venv", "__pycache__", "node_modules"}
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for d in dirs:
            local_names_found.add(d)
        for f in files:
            if f.endswith(".py"):
                local_names_found.add(f[:-3])

    non_local = set()
    for name in module_names:
        # WHITELIST: Apps críticas que NUNCA deben filtrarse
        if name.lower() in ["django", "ckeditor", "ckeditor_uploader"]:
            non_local.add(name)
            continue
            
        # Si el nombre es un paquete de pip real, se mantiene
        if name in pkg_dist:
            non_local.add(name)
            continue
            
        # Si NO es de pip y SÍ está en nuestra lista de carpetas/archivos locales, se filtra
        if name in local_names_found:
            continue
            
        non_local.add(name)
            
    return non_local


def filter_transitive_dependencies(package_versions):
    """Inactivo para asegurar visibilidad de lxml/Django."""
    return package_versions
