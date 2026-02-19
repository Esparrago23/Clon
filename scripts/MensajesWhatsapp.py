import json
import time
import re
import random
from datetime import datetime
from dateutil import parser as dateparser
from playwright.sync_api import sync_playwright

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

    texto = re.sub(r"\n?\d{1,2}:\d{2}\s?[APMapm]{2}$", "", texto).strip()

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

            except Exception as e:
                print("Advertencia:", e)

            time.sleep(random.uniform(2.5, 4.5))


if __name__ == "__main__":
    run()
