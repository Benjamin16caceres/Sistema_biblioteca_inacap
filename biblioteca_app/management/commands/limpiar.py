from django.core.management.base import BaseCommand
from biblioteca_app.models import Reserva
from django.utils import timezone

class Command(BaseCommand):
    help = 'Comando simple para limpiar reservas'
    
    def handle(self, *args, **options):
        print("🎉 ¡COMANDO DE PRUEBA FUNCIONANDO!")
        print("La estructura management/commands está correcta")
        
        # Mostrar estado
        expiradas = Reserva.objects.filter(fecha_termino__lt=timezone.now()).count()
        activas = Reserva.objects.filter(fecha_termino__gt=timezone.now()).count()
        
        print(f"Reservas activas: {activas}")
        print(f"Reservas expiradas: {expiradas}")