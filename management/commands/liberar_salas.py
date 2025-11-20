from django.core.management.base import BaseCommand
from django.utils import timezone
from biblioteca_app.models import Reserva

class Command(BaseCommand):
    help = 'Libera salas cuyas reservas han expirado'
    
    def handle(self, *args, **options):
        ahora = timezone.now()
        self.stdout.write(f"🕒 Ejecutando liberación automática a las {ahora}")
        
        # Encontrar reservas expiradas
        reservas_expiradas = Reserva.objects.filter(fecha_termino__lt=ahora)
        count = reservas_expiradas.count()
        
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Encontradas {count} reservas expiradas:')
            )
            
            for reserva in reservas_expiradas:
                self.stdout.write(
                    f'   🗑️  Eliminando: {reserva.sala.nombre} '
                    f'(RUT: {reserva.rut}, Terminó: {reserva.fecha_termino.strftime("%H:%M")})'
                )
            
            # Eliminar las reservas expiradas
            reservas_expiradas.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {count} salas liberadas exitosamente!')
            )
        else:
            self.stdout.write('✅ No hay reservas expiradas para liberar')