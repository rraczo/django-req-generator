from django.core.management.base import BaseCommand
import os
from django_req_generator.utils.i18n import _


class Command(BaseCommand):
    help = _("command_help")

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            default="requirements.txt",
            help=_("arg_output_help"),
        )
        parser.add_argument(
            "--validate",
            action="store_true",
            help=_("arg_validate_help"),
        )
        parser.add_argument(
            "-d",
            "--develop",
            help=_("arg_develop_help"),
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        validate = options["validate"]

        self.stdout.write(self.style.SUCCESS(_("start_gen", file=output_file)))
        
        # 1. Estrategias de escaneo
        from django_req_generator.scanner import ast_analysis, django_inspector, dynamic_tracker
        from django_req_generator.utils import mapper, filter, validator

        self.stdout.write(_("scan_ast"))
        project_root = os.getcwd()
        ast_modules = ast_analysis.scan_directory(project_root)

        self.stdout.write(_("scan_django"))
        django_modules = django_inspector.inspect_settings()
        
        self.stdout.write(_("load_dynamic"))
        dynamic_modules = dynamic_tracker.load_tracked_modules()

        all_modules = ast_modules.union(django_modules).union(dynamic_modules)

        # 2. Filtrado y Mapeo
        self.stdout.write(_("filter_map"))
        # Filtrar librería estándar primero
        all_cleaned = filter.filter_standard_library(all_modules)
        # Filtrar archivos y carpetas locales (los tuyos)
        clean_modules = filter.filter_local_modules(all_cleaned, project_root)
        
        # Log para depuración si verbosity >= 2
        if options.get("verbosity", 1) >= 2:
            self.stdout.write(f"DEBUG: Módulos detectados tras limpieza: {clean_modules}")

        package_versions = mapper.map_modules_to_packages(clean_modules)

        # 3. Filtrado de dependencias transitivas
        final_packages = filter.filter_transitive_dependencies(package_versions)

        # 4. Backup solo si es el nombre por defecto (requirements.txt) y ya existe
        if output_file == "requirements.txt" and os.path.exists(output_file):
            n = 1
            while os.path.exists(f"{output_file}.backup_{n}"):
                n += 1
            backup_name = f"{output_file}.backup_{n}"
            os.rename(output_file, backup_name)
            self.stdout.write(self.style.WARNING(_("backup_created", backup=backup_name)))

        # 5. Escritura del archivo
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(_("header_autogen") + "\n")
            f.write(_("header_repo") + "\n\n")

            for pkg, ver in sorted(final_packages.items()):
                if ver == "???":
                    f.write(f"{pkg}\n")
                else:
                    f.write(f"{pkg}=={ver}\n")
        
        self.stdout.write(self.style.SUCCESS(_("write_success", file=output_file, count=len(final_packages))))

        if validate:
            self.stdout.write(self.style.WARNING(_("warn_production")))
            confirm = input(_("prompt_continue")).lower()
            
            if confirm not in ["y", "s", "yes", "si"]:
                self.stdout.write(self.style.NOTICE(_("validate_skipped")))
            else:
                self.stdout.write(_("validate_start"))
                # Capturar el módulo de configuración y la ruta del plugin
                settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
                
                # Priorizar flag --develop para la ruta del plugin
                plugin_root = options.get("develop")
                if not plugin_root:
                    # Fallback si no se pasa el flag (intentar subir niveles)
                    plugin_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                
                # Gestión de entorno temporal fuera del bucle para reutilización óptima
                import tempfile
                with tempfile.TemporaryDirectory() as venv_dir:
                    # Bucle de auto-curación interactivo
                    while True:
                        report = validator.validate_requirements(
                            output_file, 
                            project_root, 
                            settings_module=settings_module,
                            plugin_root=plugin_root,
                            log_callback=self.stdout.write,
                            venv_dir=venv_dir
                        )
                        
                        if report["success"]:
                            self.stdout.write(self.style.SUCCESS(_("validate_success")))
                            break
                    
                    # Si falló, mirar si es por un módulo faltante (lazy import)
                    missing_mod = report.get("missing_module")
                    if missing_mod:
                        confirm_add = input(_("prompt_missing_module", module=missing_mod)).lower()
                        if confirm_add in ["y", "s", "yes", "si"]:
                            # Mapear y añadir a la lista actual
                            new_pkgs = mapper.map_modules_to_packages({missing_mod})
                            final_packages.update(new_pkgs)
                            
                            # Sobrescribir el archivo con la nueva librería
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(_("header_autogen") + "\n")
                                f.write(_("header_repo") + "\n\n")
                                for pkg, ver in sorted(final_packages.items()):
                                    if ver == "???":
                                        f.write(f"{pkg}\n")
                                    else:
                                        f.write(f"{pkg}=={ver}\n")
                            
                            # Reintentar validación
                            continue
                    
                    self.stdout.write(self.style.ERROR(_("validate_error", output=report['output'])))
                    break
