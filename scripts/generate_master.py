from cognitive.shadow_engine import generar_respuesta

if __name__ == "__main__":
    print(" Iniciando Motor Cognitivo V1.5 (Modo Chat Interactivo)...")
    print(" Escribe 'salir' para terminar la prueba.\n")
    
    contacto_prueba = "Trike"
    memoria_terminal = []  
    
    while True:
        mensaje_usuario = input(f"[{contacto_prueba}]: ")
        
        if mensaje_usuario.lower() in ['salir', 'exit', 'quit']:
            print(" Cerrando simulación...")
            break
            
        if not mensaje_usuario.strip():
            continue
            
        print(" Pensando...")
        
        respuesta_clon = generar_respuesta(
            nombre_chat=contacto_prueba,
            remitente_nombre=contacto_prueba,
            mensaje_entrante=mensaje_usuario,
            historial_simulado=memoria_terminal
        )
        
        print(f"[Bug (Clon)]: {respuesta_clon}\n")
        
        memoria_terminal.append(f"{contacto_prueba}: {mensaje_usuario}")
        memoria_terminal.append(f"Tú: {respuesta_clon}")
        memoria_terminal = memoria_terminal[-6:]