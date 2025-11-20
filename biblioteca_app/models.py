from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

class Sala(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('mantencion', 'En Mantencion'),
    ]
    
    nombre = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    habilitada = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.nombre} - Capacidad: {self.capacidad}"
    
    @property
    def esta_disponible(self):
        """Verifica si la sala está disponible para reservar ahora"""
        if self.estado != 'disponible' or not self.habilitada:
            return False
        
        # Verificar si no hay reservas activas
        reservas_activas = self.reserva_set.filter(fecha_termino__gt=timezone.now())
        return not reservas_activas.exists()

class Reserva(models.Model):
    rut = models.CharField(max_length=12, verbose_name="RUT")
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_termino = models.DateTimeField()
    liberacion_programada = models.BooleanField(default=False)
    tiempo_liberacion = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        # Si no hay fecha término, calcular 2 horas desde fecha inicio
        if not self.fecha_termino:
            self.fecha_termino = self.fecha_inicio + timedelta(hours=2)
        super().save(*args, **kwargs)
    
    def esta_activa(self):
        return timezone.now() < self.fecha_termino
    
    def __str__(self):
        return f"Reserva {self.sala.nombre} - {self.rut}"  