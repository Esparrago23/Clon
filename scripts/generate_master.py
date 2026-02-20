from cognitive.shadow_engine import generar_respuesta

if __name__ == "__main__":

    r = generar_respuesta(
        nombre_chat="Roy",
        remitente_nombre="Roy",
        mensaje_entrante="¿quieres ir por tacos mañana?"
    )

    print("\nRESPUESTA:", r)