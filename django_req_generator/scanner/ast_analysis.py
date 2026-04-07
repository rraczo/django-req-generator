import ast
import os


def scan_directory(path):
    """Escanea un directorio buscando archivos .py y extrayendo sus imports."""
    imports = set()
    ignore_dirs = {".git", "venv", ".venv", "__pycache__", "node_modules", "dist", "build", ".pytest_cache", ".tox"}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Llamada al extractor por cada archivo
                imports.update(get_imports_from_file(file_path))
    return imports


def get_imports_from_file(file_path):
    """Extrae los nombres de los módulos importados en un archivo usando AST."""
    file_imports = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    file_imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    file_imports.add(node.module.split(".")[0])
    except Exception:
        # Ignorar archivos que no se pueden parsear (ej. errores de sintaxis)
        pass
    return file_imports
