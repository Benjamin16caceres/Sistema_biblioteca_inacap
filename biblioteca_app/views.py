from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Sala, Reserva
from .forms import ReservaRapidaForm, ReservaProgramadaForm
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta

def home(request):
    salas = Sala.objects.all()
    return render(request, 'biblioteca_app/home.html', {'salas': salas})

def sala_detail(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    return render(request, 'biblioteca_app/sala_detail.html', {'sala': sala})

def reserva_rapida(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    
    # VALIDAR DISPONIBILIDAD
    if not sala.esta_disponible:
        messages.error(request, f'La sala {sala.nombre} no está disponible para reserva rápida en este momento.')
        return redirect('home')
    
    # Calcular horarios para mostrar en template
    hora_actual = timezone.now()
    hora_inicio = hora_actual + timedelta(minutes=30)
    hora_fin = hora_inicio + timedelta(hours=2)
    
    if request.method == 'POST':
        form = ReservaRapidaForm(request.POST)
        if form.is_valid():
            try:
                # VERIFICACIÓN FINAL DE DISPONIBILIDAD
                if not sala.esta_disponible:
                    messages.error(request, f'La sala {sala.nombre} fue reservada por otro usuario mientras completabas el formulario.')
                    return redirect('home')
                
                reserva = form.save(commit=False)
                reserva.sala = sala
                reserva.fecha_inicio = hora_inicio
                reserva.fecha_termino = hora_fin
                reserva.save()
                
                messages.success(request, 
                    f'Reserva rápida confirmada para {sala.nombre}. '
                    f'Tu sala estará disponible desde {reserva.fecha_inicio.strftime("%H:%M")} '
                    f'hasta {reserva.fecha_termino.strftime("%H:%M")}'
                )
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = ReservaRapidaForm()
    
    return render(request, 'biblioteca_app/reserva_rapida.html', {
        'form': form,
        'sala': sala,
        'hora_actual': hora_actual,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin
    })

def reserva_programada(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    
    # VALIDAR DISPONIBILIDAD
    if not sala.esta_disponible:
        messages.error(request, f'La sala {sala.nombre} no está disponible para reservas en este momento.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ReservaProgramadaForm(request.POST, sala=sala)
        if form.is_valid():
            try:
                # VERIFICACIÓN FINAL DE DISPONIBILIDAD
                if not sala.esta_disponible:
                    messages.error(request, f'La sala {sala.nombre} fue reservada por otro usuario mientras completabas el formulario.')
                    return redirect('home')
                
                reserva = form.save(commit=False)
                reserva.sala = sala
                reserva.save()
                
                messages.success(request, 
                    f'Reserva programada confirmada para {sala.nombre} el '
                    f'{reserva.fecha_inicio.strftime("%d/%m/%Y a las %H:%M")}'
                )
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            # Mostrar errores específicos del formulario
            for error in form.errors.values():
                messages.error(request, f'Error: {error}')
    else:
        form = ReservaProgramadaForm(sala=sala)
    
    return render(request, 'biblioteca_app/reserva_programada.html', {
        'form': form,
        'sala': sala
    })

def mis_reservas(request):
    rut = ''
    reservas = Reserva.objects.none()
    
    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        if rut:
            reservas = Reserva.objects.filter(rut=rut).order_by('-fecha_inicio')
            
            if not reservas.exists():
                messages.info(request, f'No se encontraron reservas para el RUT: {rut}')
        else:
            messages.error(request, 'Por favor ingresa un RUT para buscar.')
    
    return render(request, 'biblioteca_app/mis_reservas.html', {
        'reservas': reservas,
        'rut_buscado': rut
    })

def cancelar_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        sala_nombre = reserva.sala.nombre
        reserva_fecha = reserva.fecha_inicio.strftime("%d/%m/%Y a las %H:%M")
        
        # Verificar que la reserva no haya ya comenzado
        if reserva.fecha_inicio <= timezone.now():
            messages.warning(request, 
                f'No puedes cancelar la reserva de {sala_nombre} porque ya comenzó.'
            )
        else:
            reserva.delete()
            messages.success(request, 
                f'Reserva de {sala_nombre} para el {reserva_fecha} fue cancelada exitosamente'
            )
        
        return redirect('mis_reservas')
    
    return redirect('mis_reservas')

def liberar_salas_manual(request):
    """Vista para liberar salas expiradas - PARA LA DEMO"""
    if request.method == 'POST':
        # Encontrar reservas expiradas
        reservas_expiradas = Reserva.objects.filter(fecha_termino__lt=timezone.now())
        count = reservas_expiradas.count()
        
        if count > 0:
            # Mostrar detalles de lo que se eliminará
            detalles = []
            for reserva in reservas_expiradas:
                detalles.append(f"{reserva.sala.nombre} (RUT: {reserva.rut})")
            
            # Eliminar las reservas expiradas
            reservas_expiradas.delete()
            
            messages.success(request, f'{count} salas liberadas automáticamente!')
            messages.info(request, f'Salas liberadas: {", ".join(detalles)}')
        else:
            messages.info(request, 'No hay salas pendientes de liberación')
        
        return redirect('liberar_salas')
    
    # Para GET request, mostrar estado actual
    reservas_expiradas = Reserva.objects.filter(fecha_termino__lt=timezone.now()).count()
    reservas_activas = Reserva.objects.filter(fecha_termino__gt=timezone.now()).count()
    
    return render(request, 'biblioteca_app/liberar_manual.html', {
        'reservas_expiradas': reservas_expiradas,
        'reservas_activas': reservas_activas,
    })

def programar_liberacion(request):
    """Vista para programar liberación de salas específicas"""
    if not request.user.is_staff:
        messages.error(request, 'Solo administradores pueden acceder')
        return redirect('home')
    
    # Obtener salas con reservas activas
    salas_ocupadas = []
    for sala in Sala.objects.all():
        reserva_activa = Reserva.objects.filter(sala=sala, fecha_termino__gt=timezone.now()).first()
        if reserva_activa:
            salas_ocupadas.append({
                'sala': sala,
                'reserva': reserva_activa
            })
    
    if request.method == 'POST':
        sala_id = request.POST.get('sala_id')
        minutos = int(request.POST.get('minutos', 1))
        
        sala = get_object_or_404(Sala, id=sala_id)
        reserva = Reserva.objects.filter(sala=sala, fecha_termino__gt=timezone.now()).first()
        
        if reserva:
            reserva.liberacion_programada = True
            reserva.tiempo_liberacion = minutos
            reserva.save()
            
            messages.success(request, f'Liberacion programada para {sala.nombre} en {minutos} minutos')
        else:
            messages.error(request, f'No hay reserva activa para {sala.nombre}')
        
        return redirect('programar_liberacion')
    
    return render(request, 'biblioteca_app/programar_liberacion.html', {
        'salas_ocupadas': salas_ocupadas,
    })

def liberar_ahora(request, sala_id):
    """Liberar una sala específica inmediatamente"""
    if not request.user.is_staff:
        messages.error(request, 'Solo administradores pueden realizar esta accion')
        return redirect('home')
    
    if request.method == 'POST':
        sala = get_object_or_404(Sala, id=sala_id)
        reservas = Reserva.objects.filter(sala=sala, fecha_termino__gt=timezone.now())
        
        if reservas.exists():
            count = reservas.count()
            reservas.delete()
            messages.success(request, f'{sala.nombre} liberada inmediatamente!')
        else:
            messages.info(request, f'{sala.nombre} ya está disponible')
        
        return redirect('programar_liberacion')
    
    return redirect('programar_liberacion')

def estado_liberaciones(request):
    """Vista para ver el estado de las liberaciones programadas"""
    if not request.user.is_staff:
        messages.error(request, 'Solo administradores pueden acceder a esta funcion')
        return redirect('home')
    
    # Reducir contador en 1 minuto cada vez que se visita
    reservas_programadas = Reserva.objects.filter(liberacion_programada=True)
    
    for reserva in reservas_programadas:
        if reserva.tiempo_liberacion > 0:
            reserva.tiempo_liberacion -= 1
            if reserva.tiempo_liberacion <= 0:
                # Liberar la sala automáticamente
                sala_nombre = reserva.sala.nombre
                reserva.delete()
                messages.success(request, f'{sala_nombre} liberada automaticamente!')
            else:
                reserva.save()
    
    # Obtener reservas actualizadas después de procesar
    reservas_actualizadas = Reserva.objects.filter(liberacion_programada=True)
    
    return render(request, 'biblioteca_app/estado_liberaciones.html', {
        'reservas_programadas': reservas_actualizadas,
    })

def actualizar_contador(request, reserva_id):
    """Reducir el contador en 1 minuto manualmente"""
    if not request.user.is_staff:
        messages.error(request, 'Solo administradores pueden realizar esta accion')
        return redirect('home')
    
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        
        if reserva.tiempo_liberacion > 0:
            reserva.tiempo_liberacion -= 1
            reserva.save()
            
            if reserva.tiempo_liberacion <= 0:
                messages.success(request, f'{reserva.sala.nombre} lista para liberar!')
            else:
                messages.info(request, f'Contador actualizado: {reserva.tiempo_liberacion} minutos restantes')
        else:
            messages.info(request, f'{reserva.sala.nombre} ya esta lista para liberar')
    
    return redirect('estado_liberaciones')