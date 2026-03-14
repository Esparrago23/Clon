from datetime import datetime

def esta_durmiendo() -> bool:
    """
    Simula el ciclo biológico de sueño del clon.
    Devuelve True si la hora actual está dentro de la ventana de sueño.
    """
    hora_actual = datetime.now().time()
    
    # Supongamos que duermes de 1:00 AM a 8:00 AM
    hora_dormir, minuto_dormir = 1, 0
    hora_despertar, minuto_despertar = 8, 0
    
    # Lógica de cruce de medianoche
    if hora_dormir > hora_despertar:
        return hora_actual.hour >= hora_dormir or hora_actual.hour < hora_despertar
    else:
        return hora_dormir <= hora_actual.hour < hora_despertar

def respuesta_dormido() -> str:
    """
    Retorna el mensaje a enviar si alguien intenta comunicarse durante horas de sueño.
    """
    return "[SLEEP] Zzz... el bot está durmiendo. Responderá en la mañana."
