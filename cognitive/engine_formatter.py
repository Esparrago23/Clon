import re
import random

def humanizar_texto(texto: str) -> str:
    # 0. Eliminar cualquier cosa entre corchetes (ej. [15:12] o [jaja])
    texto = re.sub(r'\[.*?\]', '', texto).strip()

    # 1. Todo a minúsculas
    texto = texto.lower()
    
    # 2. Quitar puntos finales (suele verse muy formal en WhatsApp)
    if texto.endswith('.'):
        texto = texto[:-1]
        
    # 3. Quitar signos de interrogación o exclamación iniciales (típico de latinos al tipear rápido)
    texto = texto.replace('¿', '').replace('¡', '')
    
    return texto

def fragmentar_mensaje(mensaje: str) -> list[str]:
    """
    Toma un mensaje largo generado por el LLM y lo divide en partes más pequeñas
    simulando cómo escribiría un humano en WhatsApp (múltiples mensajes cortos).
    """
    mensaje = humanizar_texto(mensaje)

    # Si el mensaje es corto, no lo fragmentamos
    if len(mensaje) < 60 and "." not in mensaje:
        return [mensaje]

    # Separar por puntos, saltos de línea o signos de puntuación fuertes
    # Mantenemos los signos de puntuación en el recorte
    fragmentos = re.split(r'(?<=[!?.!?\n])\s+', mensaje.strip())
    
    resultado = []
    buffer = ""
    
    for frag in fragmentos:
        if not frag: continue
        
        # Si el fragmento por sí solo es muy largo, lo metemos al resultado
        if len(frag) > 80:
            if buffer:
                resultado.append(buffer.strip())
                buffer = ""
            resultado.append(frag.strip())
        # Si sumando el fragmento al buffer es corto, lo unimos
        elif len(buffer) + len(frag) < 60:
            buffer = buffer + " " + str(frag)
        else:
            resultado.append(buffer.strip())
            buffer = str(frag).strip()
            
    if buffer:
        resultado.append(buffer.strip())
        
    return resultado
