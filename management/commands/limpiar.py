from django.core.management.base import BaseCommand
from biblioteca_app.models import Reserva
from django.utils import timezone

class Command(BaseCommand):
    help = 'Limpiar reservas expiradas'
    
    def handle(self, *args, **options):
        print("=== LIMPIANDO RESERVAS EXPIRADAS ===")
        print(f"Hora actual: {timezone.now()}")
        
        expiradas = Reserva.objects.filter(fecha_termino__lt=timezone.now())
        cantidad = expiradas.count()
        
        if cantidad > 0:
            print(f"Encontradas {cantidad} reservas expiradas:")
            for r in expiradas:
                print(f" - {r.sala.nombre} (RUT: {r.rut}) - Terminó: {r.fecha_termino}")
            expiradas.delete()
            print(f"✅ {cantidad} salas liberadas!")
        else:
            print("✅ No hay reservas expiradas.")