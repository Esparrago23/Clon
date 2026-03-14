import os

# Notas:  
# Para que Whisper funcione en local, necesitas instalar: pip install openai-whisper
# Además de ffmpeg instalado a nivel de sistema (apt install ffmpeg / choco install ffmpeg)

class AudioProcessor:
    def __init__(self):
        print(" [AUDIO] Inicializando procesador de audios...")
        try:
            import whisper
            # Cargamos el modelo pequeño (rápido para CPU o GPUs pequeñas)
            # Opciones: 'tiny', 'base', 'small', 'medium', 'large'
            self.modelo_whisper = whisper.load_model("small")
            self.whisper_disponible = True
        except ImportError:
            print(" [AUDIO-WARNING] Librería 'whisper' no detectada. Las notas de voz no se transcribirán.")
            self.whisper_disponible = False

    def transcribir_audio(self, filepath: str) -> str:
        """
        Toma una ruta a un archivo de audio (.ogg de WhatsApp), lo procesa con Whisper 
        y devuelve el texto exacto que dijo la persona.
        """
        if not self.whisper_disponible or not os.path.exists(filepath):
            return "[Audio Inaccesible o Whisper apagado]"
            
        print(f" [WHISPER] Escuchando audio de {os.path.basename(filepath)}...")
        try:
            resultado = self.modelo_whisper.transcribe(filepath, language="es")
            texto_transcrito = resultado["text"].strip()
            print(f" [WHISPER-OUT] '{texto_transcrito}'")
            return texto_transcrito
        except Exception as e:
            print(f" [WHISPER-ERROR] Falló la transcripción: {e}")
            return "[Error transcribiendo audio]"

    def generar_voz(self, texto: str, output_path: str = "respuesta_clon.ogg") -> str:
        """
        STUB de Text-To-Speech (ElevenLabs o XTTSv2)
        Toma el texto generado por Llama3 y fabrica un archivo .ogg con tu voz clonada.
        """
        # Aquí iría el código de la API de ElevenLabs o el modelo TTS local
        print(" [TTS-STUB] Generando audio simulado a partir de texto...")
        
        # Simulamos que creamos un archivo (Solo para desarrollo)
        with open(output_path, "wb") as f:
            f.write(b"falso audio wey")
            
        return output_path

audio_agent = AudioProcessor()
