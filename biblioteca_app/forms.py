from django import forms
from .models import Reserva, Sala
from datetime import datetime, timedelta
from django.utils import timezone

class ReservaRapidaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['rut']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: 12345678-9'
            })
        }

class ReservaProgramadaForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'min': datetime.now().date().strftime('%Y-%m-%d')
        }),
        label="Fecha de reserva"
    )
    hora = forms.ChoiceField(
        choices=[(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 19)],
        label="Hora de inicio"
    )
    
    class Meta:
        model = Reserva
        fields = ['rut', 'fecha_inicio', 'fecha_termino']
        widgets = {
            'fecha_inicio': forms.HiddenInput(),
            'fecha_termino': forms.HiddenInput(),
            'rut': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: 12345678-9'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.sala = kwargs.pop('sala', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        
        if fecha and hora and self.sala:
            # Crear datetime para la reserva
            inicio = datetime.combine(fecha, datetime.strptime(hora, '%H:%M').time())
            termino = inicio + timedelta(hours=2)
            
            # Convertir a timezone aware
            inicio = timezone.make_aware(inicio)
            termino = timezone.make_aware(termino)
            
            # Asignar al modelo
            cleaned_data['fecha_inicio'] = inicio
            cleaned_data['fecha_termino'] = termino
            
            # Validar que no esté en el pasado
            if inicio < timezone.now():
                raise forms.ValidationError('No puedes reservar en horarios pasados.')
            
            # VALIDACIÓN DE CONFLICTOS - NUEVO
            reservas_conflicto = Reserva.objects.filter(
                sala=self.sala,
                fecha_inicio__lt=termino,
                fecha_termino__gt=inicio
            )
            
            if reservas_conflicto.exists():
                raise forms.ValidationError(
                    'Ya existe una reserva para esta sala en el horario seleccionado. '
                    'Por favor elige otro horario.'
                )
        
        return cleaned_data