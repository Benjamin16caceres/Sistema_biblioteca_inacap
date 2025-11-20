from django.core.management.base import BaseCommand
from django.utils import timezone
from biblioteca_app.models import Reserva

class Command(BaseCommand):
    help = 'Libera salas cuyas reservas han expirado'
    
    def handle(self, *args, **options):
        ahora = timezone.now()
        print(f"=== LIBERANDO SALAS EXPIRADAS ===")
        print(f"Hora actual: {ahora}")
        
        reservas_expiradas = Reserva.objects.filter(fecha_termino__lt=ahora)
        count = reservas_expiradas.count()
        
        if count > 0:
            print(f"Encontradas {count} reservas expiradas:")
            for reserva in reservas_expiradas:
                print(f" - {reserva.sala.nombre} (RUT: {reserva.rut})")
            
            reservas_expiradas.delete()
            print(f"✅ {count} salas liberadas exitosamente!")
        else:
            print("✅ No hay reservas expiradas para liberar")