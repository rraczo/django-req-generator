import importlib.metadata as md
import urllib.request
import json
import logging

def check_pypi_existence(package_name):
    """
    Verifica si un paquete existe en PyPI usando su API JSON.
    Devuelve el nombre oficial si existe, None si no.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data.get("info", {}).get("name", package_name)
    except Exception:
        pass
    return None

def map_modules_to_packages(module_names):
    """
    Mapea módulos a paquetes de forma dinámica. 
    Prioriza lo instalado y usa PyPI como fallback inteligente.
    """
    pkg_dist = md.packages_distributions()
    canonical_names = {dist.metadata.get("Name").lower(): dist.metadata.get("Name") 
                       for dist in md.distributions() if dist.metadata.get("Name")}

    mapped_packages = {}

    for module in module_names:
        # Django es innegociable
        if module == "django":
            try:
                import django as dj
                mapped_packages["Django"] = dj.get_version()
                continue
            except Exception: pass

        # 1. ¿Está instalado localmente? (La vía rápida)
        if module in pkg_dist:
            dist_name = pkg_dist[module][0]
            official_name = canonical_names.get(dist_name.lower(), dist_name)
            try:
                mapped_packages[official_name] = md.version(dist_name)
                continue
            except Exception: pass

        # 2. ¿No está instalado? Vamos a preguntarle a PyPI (Detección Dinámica)
        # Probamos el nombre original (con guiones si tiene guiones bajos)
        search_name = module.replace("_", "-")
        pypi_name = check_pypi_existence(search_name)
        
        if pypi_name:
            mapped_packages[pypi_name] = "???"
        else:
            # 3. No existe tal cual... ¿será una app de Django? Probemos con prefijo
            django_guess = f"django-{search_name}"
            pypi_name = check_pypi_existence(django_guess)
            if pypi_name:
                mapped_packages[pypi_name] = "???"
            else:
                # 4. Fallback final: lo incluimos como el módulo mismo
                mapped_packages[search_name] = "???"

    return mapped_packages
