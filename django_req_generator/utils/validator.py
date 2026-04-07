import subprocess
import venv
import tempfile
import os
import shutil

from django_req_generator.utils.i18n import _

def validate_requirements(requirements_file_path, project_root, settings_module=None, plugin_root=None, log_callback=None, venv_dir=None):
    """
    Ejecuta django check en un entorno virtual. 
    Si venv_dir es proporcionado, reutiliza ese entorno (mucho más rápido).
    """
    report = {"success": True, "output": ""}

    def log(msg):
        if log_callback:
            log_callback(msg)

    # Si no nos pasan un venv_dir, creamos uno efímero (comportamiento antiguo)
    is_temporary = venv_dir is None
    if is_temporary:
        venv_dir = tempfile.mkdtemp()

    try:
        # Determinar el binario de python y pip
        if os.name == "nt":
            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
            pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
        else:
            python_exe = os.path.join(venv_dir, "bin", "python")
            pip_exe = os.path.join(venv_dir, "bin", "pip")

        # 1. Crear el entorno si no existe todavía
        if not os.path.exists(python_exe):
            log(_("log_create_venv", path=venv_dir))
            venv.create(venv_dir, with_pip=True)
            
            # 2. Instalar el propio plugin solo la primera vez
            if plugin_root:
                log(_("log_install_plugin", path=plugin_root))
                subprocess.run(
                    [pip_exe, "install", plugin_root],
                    check=True, capture_output=True, text=True
                )

        # 3. Instalar los requisitos (Pip es inteligente y solo instalará lo nuevo)
        log(_("log_install_reqs", file=requirements_file_path))
        subprocess.run(
            [pip_exe, "install", "-r", requirements_file_path],
            check=True, capture_output=True, text=True
        )

        # 4. Ejecutar django check
        manage_py = os.path.join(project_root, "manage.py")
        if not os.path.exists(manage_py):
            return {"success": False, "output": _("error_no_manage")}

        log(_("log_running_check", settings=settings_module or "Default"))
        check_cmd = [python_exe, manage_py, "check"]
        if settings_module:
            check_cmd.append(f"--settings={settings_module}")

        result = subprocess.run(
            check_cmd, check=True, capture_output=True, text=True
        )
        report["output"] = result.stdout

    except subprocess.CalledProcessError as e:
        report["success"] = False
        output = (e.stdout or "") + (e.stderr or "")
        report["output"] = output
        
        # Intentar extraer el módulo faltante del traceback
        import re
        match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", output)
        if match:
            report["missing_module"] = match.group(1)
    except Exception as e:
        report["success"] = False
        report["output"] = str(e)
    finally:
        # Solo lo borramos si es de la sesión efímera. 
        # Si lo gestiona generate_reqs.py, allí se debe borrar.
        if is_temporary and os.path.exists(venv_dir):
            shutil.rmtree(venv_dir)

    return report
