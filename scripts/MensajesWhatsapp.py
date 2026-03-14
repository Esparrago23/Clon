import json
import time
import re
import random
import sys
import os
from datetime import datetime
from dateutil import parser as dateparser
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.infrastructure.repositories.whatsapp import WhatsAppRepository
from app.application.use_cases.ingest_whatsapp import IngestWhatsAppMessageUseCase

from cognitive.shadow_engine import generar_respuesta
from cognitive.engine_formatter import fragmentar_mensaje
from cognitive.audio_processor import audio_agent

OUTPUT_FILE = "mensajes_whatsapp.jsonl"


def save_message(data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def get_active_contact(page):
    try:
        titulo_el = page.locator('header span[dir="auto"]').first
        if titulo_el.count() > 0:
            titulo = titulo_el.inner_text().strip()
            if titulo:
                return titulo
    except:
        pass
    return "desconocido"


def parse_message(msg, nombre_chat):
    clases_msg = msg.get_attribute("class") or ""
    es_mio = "message-out" in clases_msg

    remitente = "Tú" if es_mio else nombre_chat
    timestamp = None

    copyable_div = msg.query_selector('div[data-pre-plain-text]')

    if copyable_div:
        meta = copyable_div.get_attribute("data-pre-plain-text")
        match = re.search(r"\[(.*?)\]\s(.*?):", meta)

        if match:
            fecha_str = match.group(1)
            remitente_meta = match.group(2).strip()

            if not es_mio:
                remitente = remitente_meta

            try:
                timestamp = dateparser.parse(fecha_str).isoformat()
            except:
                timestamp = datetime.now().isoformat()

    texto_el = msg.query_selector("span.selectable-text")

    if texto_el:
        texto = texto_el.inner_text().strip()
    else:
        texto = msg.inner_text().strip()
        
    if remitente != "Tú" and texto.startswith(remitente + "\n"):
        texto = texto[len(remitente):].strip()
        
    # Validar si el mensaje es una nota de voz de WhatsApp (elemento audio)
    audio_el = msg.query_selector('audio')
    es_audio = audio_el is not None
    if es_audio and not texto:
        # En una implementación real de God Tier, aquí interceptaríamos el Blob del audio.
        # Por ahora enviamos una transcripción stub/simulada o pasamos el flag.
        audio_src = audio_el.get_attribute("src") or "audio_generico.ogg"
        
        # Simula la descarga y pasa a Whisper
        print(f" 🎵 [AUDIO_DETECTADO] Descargando y transcribiendo nota de voz...")
        texto = f"[NOTA DE VOZ] {audio_agent.transcribir_audio(audio_src)}"

    texto = re.sub(r"\n?\d{1,2}:\d{2}\s*[ap]\.?\s*m\.?$", "", texto, flags=re.IGNORECASE).strip()

    return {
        "chat": nombre_chat,
        "sender": remitente,
        "is_me": es_mio,
        "timestamp": timestamp or datetime.now().isoformat(),
        "text": texto
    }


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="whatsapp_session",
            headless=False,
            args=["--start-maximized"]
        )

        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        page.wait_for_selector('#pane-side', timeout=60000)
        time.sleep(5)

        mensajes_vistos = set()

        mensajes_iniciales = page.query_selector_all("div.message-in, div.message-out")

        for msg in mensajes_iniciales:
            msg_id = msg.get_attribute("data-id")
            if not msg_id:
                msg_id = hash(msg.inner_text().strip())
            mensajes_vistos.add(msg_id)

        db_session = SessionLocal()
        repo = WhatsAppRepository(db_session)
        use_case = IngestWhatsAppMessageUseCase(repo)

        while True:
            try:
                fila_chat = page.locator(
                    'div[role="listitem"]:has(span[aria-label*="no leíd"]), '
                    'div[role="listitem"]:has(span[aria-label*="unread"]), '
                    'div[role="row"]:has(span[aria-label*="no leíd"]), '
                    'div[role="row"]:has(span[aria-label*="unread"])'
                ).first

                if fila_chat.count() > 0:
                    fila_chat.click(force=True)
                    time.sleep(2)

                nombre_chat = get_active_contact(page)
                mensajes = page.query_selector_all("div.message-in, div.message-out")

                nuevos_mensajes_texto = []
                ultimo_remitente = None

                for msg in mensajes:
                    parsed = parse_message(msg, nombre_chat)
                    texto = parsed["text"]

                    if not texto:
                        continue

                    msg_id = msg.get_attribute("data-id") or hash(texto)

                    if msg_id in mensajes_vistos:
                        continue

                    mensajes_vistos.add(msg_id)

                    data = {
                        "id_whatsapp": msg_id,
                        **parsed
                    }

                    print(f"[{'ME' if parsed['is_me'] else 'OTRO'}] {parsed['chat']} -> {parsed['text']}")
                    save_message(data)
                    try:
                        use_case.execute(data)
                        print(" -> Guardado en Memoria Relacional (PostgreSQL)")
                        
                        if not parsed['is_me']:
                            # Filtrar por tiempo: Solo responder a mensajes recientes (ultimos 15 minutos)
                            try:
                                msg_time = dateparser.parse(parsed['timestamp']).replace(tzinfo=None)
                                time_diff_minutes = (datetime.now() - msg_time).total_seconds() / 60.0
                            except:
                                time_diff_minutes = 0 # Si no podemos parsear, asumimos reciente
                                
                            if time_diff_minutes < 15:
                                # Le damos al motor cognitivo el contexto de la hora a la que se envió
                                hora_formateada = msg_time.strftime("%H:%M") if 'msg_time' in locals() else "Reciente"
                                nuevos_mensajes_texto.append(f"[{hora_formateada}] {texto}")
                                ultimo_remitente = parsed['sender']
                            else:
                                print(f" [SKIP] Mensaje ignorado para auto-respuesta por ser antiguo ({time_diff_minutes:.0f} mins atrás)")
                            
                    except Exception as db_err:
                        print(f" -> Error en BD: {db_err}")

                # Generación de Respuesta por el Clon una vez procesados todos los mensajes nuevos del chat
                if nuevos_mensajes_texto and ultimo_remitente:
                    texto_combinado = "\n".join(nuevos_mensajes_texto)
                    respuesta_clon = generar_respuesta(nombre_chat, ultimo_remitente, texto_combinado)
                    
                    if "[ABORT]" in respuesta_clon:
                        print(f" ⚠️ {respuesta_clon}")
                    elif "[SLEEP]" in respuesta_clon:
                        print(f" 💤 {respuesta_clon} (Ignorando para no despertar)")
                    elif "[SEEN]" in respuesta_clon:
                        print(f" 👻 [CLON GHOST]: Conversación finalizada, dejando en visto.")
                    else:
                        print(f" [CLON PENSANDO...]")
                        
                        # Buscar la caja de texto (textarea) de WhatsApp
                        caja_texto = page.locator('div[aria-placeholder="Escribe un mensaje"]').first
                        if caja_texto.count() > 0:
                            
                            # Validar si Shadow decidió enviar un Audio
                            if respuesta_clon.startswith("[VOICE_NOTE]"):
                                audio_path = audio_agent.generar_voz(respuesta_clon.replace("[VOICE_NOTE]", "").strip())
                                print(f" 🎙️ [TTS] Enviando nota de voz generada: {audio_path}")
                                
                                # Simulamos adjuntar el archivo de audio. En una app real, 
                                # se da click en el clip de adjuntar -> documento/foto -> y se sube el .ogg
                                # page.locator('span[data-icon="clip"]').click()
                                # ... subida de archivo ...
                                time.sleep(random.uniform(5.0, 10.0)) # Simulando que graba el mensaje
                                caja_texto.click()
                                page.keyboard.type("*(Nota de voz enviada)*") # Placeholder visual
                                page.keyboard.press("Enter")
                                
                            else:
                                fragmentos = fragmentar_mensaje(respuesta_clon)
                                
                                # Si el context combinado era muy largo o tenso, dudamos más antes de contestar
                                if len(texto_combinado) > 150 or "!" in texto_combinado:
                                    print(" 🎭 [TENSION]: Añadiendo suspense extra al delay de pensamiento.")
                                    time_extra = random.uniform(5.0, 15.0)
                                    time.sleep(time_extra)

                                for k, frag in enumerate(fragmentos):
                                
                                    # Delay Humano de Respuesta basado en el texto total que leímos
                                    delay_pensamiento = min(10, int(len(texto_combinado if k == 0 else frag) / 15)) + random.uniform(1.0, 3.0)
                                    time.sleep(delay_pensamiento)
                                    
                                    caja_texto.click()
                                    
                                    # Escribir letra por letra simulando humano
                                    page.keyboard.type(frag, delay=random.randint(30, 80))
                                    
                                    # Delay final antes de dar Enter
                                    time.sleep(random.uniform(0.5, 1.5))
                                    page.keyboard.press("Enter")
                                    print(f" [CLON ENVIÓ ({k+1}/{len(fragmentos)})]: {frag}")
                                    
                        else:
                            print(" ❌ No se encontró la caja de texto para responder.")

            except Exception as e:
                print("Advertencia:", e)

            time.sleep(random.uniform(2.5, 4.5))


if __name__ == "__main__":
    run()
