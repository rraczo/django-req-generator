from django.core.management import ManagementUtility
from django.core.management.base import BaseCommand
import sys


class Command(BaseCommand):
    help = "Registra dependencias dinámicas durante la ejecución de un comando de Django (ej. runserver)."

    def add_arguments(self, parser):
        parser.add_argument(
            "subcommand",
            nargs="*",
            help="El comando de Django a ejecutar (ej. runserver, test)",
        )

    def handle(self, *args, **options):
        subcommand = options["subcommand"]
        if not subcommand:
            self.stdout.write(self.style.ERROR("Faltan argumentos para ejecutar el comando subyacente (ej. runserver)."))
            return

        from django_req_generator.scanner import dynamic_tracker
        
        self.stdout.write(self.style.SUCCESS(f"Activando rastreador dinámico..."))
        dynamic_tracker.start_tracking()

        try:
            # Ejecutamos el comando de Django dentro del mismo proceso
            # para que el Hook de importación capture todo.
            utility = ManagementUtility([sys.argv[0]] + subcommand)
            utility.execute()
        except KeyboardInterrupt:
            self.stdout.write("\nRastreo interrumpido por el usuario.")
        finally:
            dynamic_tracker.stop_tracking()
            used_modules = dynamic_tracker.get_tracked_modules()
            dynamic_tracker.save_tracked_modules()
            
            self.stdout.write(self.style.SUCCESS(f"\nSe detectaron {len(used_modules)} módulos raíces usados dinámicamente."))
            self.stdout.write(self.style.SUCCESS(f"Los hallazgos se guardaron en '.tracked_modules.json'."))
            
            self.stdout.write(self.style.WARNING("\nUsa 'generate_reqs' para consolidar estos hallazgos."))
