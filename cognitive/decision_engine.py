def tomar_decision(intent: str, conv_status: str, energy: float) -> str:
    """
    Decide la acción táctica a tomar basándose en el contexto.
    """
    
    # 1. Reglas de Negociación Activa (Prioridad Máxima)
    if conv_status == "NEGOTIATING":
        if "tarde" in intent or "hr" in intent or intent == "pregunta" or intent == "desconocido":
            # Si estamos negociando y nos dan una alternativa (como "mas tarde?")
            if energy > 0.5:
                return "ACEPTAR_ALTERNATIVA: Confirma que la nueva hora/opción te parece bien de forma corta ('va', 'smn a esa hr')."
            else:
                return "POSPONER_PLAN: Tienes poca energía. Dile que mejor lo dejan para otro día ('mejor otro dia we', 'ando cansado hoy')."
                
    # 2. Reglas de Invitación Inicial
    if intent == "invitacion":
        if energy < 0.4:
            return "RECHAZAR_DIRECTO: No tienes energía. Rechaza amablemente pero cortante ('hoy no jalo', 'paso')."
        return "PEDIR_DETALLES: Muestra interés y pregunta OBLIGATORIAMENTE lugar u hora ('a q hr?', 'donde?')."

    # 3. Reglas Generales
    if intent == "broma":
        return "REACCIONAR_HUMOR: Solo ríete ('jajaja', 'xd')."
        
    if intent == "pregunta":
        return "RESPONDER_CORTO: Contesta la duda sin rodeos."

    # Acción por defecto
    return "MANTENER_CHARLA: Responde de forma casual y corta para seguir el hilo."