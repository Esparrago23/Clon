# 🧠 Project: Shadow - Clon Virtual Privado

**Project: Shadow** es una arquitectura de Inteligencia Artificial diseñada para operar como un clon cognitivo virtual. El sistema escucha, recuerda y comprende el contexto social y semántico del usuario de forma 100% local (Air-gapped), garantizando privacidad absoluta.

A diferencia de un chatbot tradicional, cuenta con un **Motor Cognitivo** avanzado que analiza la intención del mensaje y aplica estrategias conversacionales humanas (Agentic Workflow) antes de generar una respuesta, eliminando el "Síndrome del NPC".

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una Arquitectura Hexagonal, respaldado por un sistema de memoria dual y un motor de razonamiento:

| Componente | Tecnología | Función |
| :--- | :--- | :--- |
| **Captura en Vivo** | Playwright + Python | Extrae mensajes de WhatsApp Web leyendo el DOM en tiempo real. |
| **Memoria Relacional** | PostgreSQL + SQLAlchemy | Guarda estructura social: *Quién* habla, en qué *Sala* y *Cuándo*. |
| **Cerebro Semántico** | ChromaDB + HuggingFace | Convierte mensajes a vectores 3D para buscar por intención y tono. |
| **Motor Cognitivo** | Ollama (Llama 3) + Python | Detecta intención, selecciona estrategia social y redacta la respuesta final. |

---

## 📂 Estructura de Directorios

El código está dividido en capas para mantenerlo escalable y limpio:

* **`app/`**: Lógica de negocio y núcleo de la aplicación.
  * `core/`: Configuraciones y conexión a BD.
  * `domain/`: Modelos de datos (Reglas de negocio).
  * `application/`: Casos de uso (Lógica de procesamiento).
  * `infrastructure/`: Repositorios (Conexión directa con PostgreSQL).
* **`cognitive/`**: [NUEVO] El Motor de Razonamiento del agente.
  * `intent_detector.py`: Usa LLM para clasificar qué quiere el usuario (invitación, broma, pregunta, etc.).
  * `strategy_selector.py`: Decide la estrategia social a aplicar según la intención (ej. si es invitación -> mostrar interés y pedir detalles logísticos).
  * `personality_rag.py`: Conecta con ChromaDB para extraer recuerdos de tu personalidad basados en el contexto dinámico.
  * `prompt_builder.py`: Ensambla el perfil social, el historial reciente, la estrategia y los recuerdos en un "Súper Prompt" limpio.

shadow_engine.py: El orquestador maestro que une los 4 pasos anteriores y genera la respuesta humana final.
* **`chats/`**: Directorio temporal para exportaciones `.txt` de WhatsApp y `.json` de Instagram.
* **`docker/`**: Orquestación de contenedores (PostgreSQL y ChromaDB).
* **`scripts/`**: Herramientas ejecutables del proyecto (Ingesta, sincronización y pruebas).
* **`whatsapp_session/`**: Almacenamiento local de la sesión web (evita escanear código QR a diario).
* **`cognitive/`**: 

---

## ⚙️ Guía Rápida: Reset y Setup Inicial

Si necesitas limpiar el sistema por completo y levantar las bases de datos desde cero, ejecuta estos comandos en orden:

```bash
# 1. Reiniciar desde cero los contenedores
cd docker
docker-compose down -v
docker-compose up -d
cd ..

# 2. Inicializar las tablas en PostgreSQL
python -m app.core.init_db

# 3. Ingresar información histórica
python -m scripts.ingest_history
python -m scripts.ingest_instagram

# 4. Crear vectores semánticos en ChromaDB
python -m scripts.sync_embeddings

# 5. Hacer pruebas de recuperación semántica
python -m scripts.test_chroma

Catálogo de Scripts (/scripts/)
El sistema cuenta con dos flujos de trabajo principales: Tiempo Real y Procesamiento de Memoria.

📡 1. Ejecución en Conjunto (Modo Tiempo Real)
Estos scripts se encargan de la "audición" activa del clon. Trabajan de la mano para capturar la mensajería del día a día.

MensajesWhatsapp.py (Los "Ojos" del Clon): Abre un navegador invisible, escanea tus chats activos e inyecta los nuevos mensajes a PostgreSQL al instante.

ingest_to_db.py (El Respaldo): Si falló la inyección en vivo, fuerza la lectura del respaldo local mensajes_whatsapp.jsonl hacia PostgreSQL.

🧠 2. Ejecución Independiente (Mantenimiento y Aprendizaje IA)
Estos scripts operan bajo demanda para enseñarle al clon tu pasado y entrenar su motor de comprensión.

ingest_history.py: Procesa exportaciones .txt de WhatsApp en lote para inyectar historial de conversaciones.

ingest_instagram.py: Procesa exportaciones .json de Instagram, unificando cuentas de IG con los perfiles canónicos de WhatsApp.

sync_embeddings.py: Lee todos los mensajes enviados por ti en PostgreSQL y los vectoriza hacia ChromaDB. Ejecutar siempre después de una ingesta histórica.

test_chroma.py: Herramienta de depuración semántica.

generate_master.py / generate_response.py: Scripts de prueba del LLM (obsoletos frente a shadow_engine.py, pero útiles para pruebas crudas de generación).

💾 Estado Actual de las Bases de Datos
PostgreSQL (Puerto 5432): Distingue entre Salas (conversations), Humanos (persons) y Textos (messages). Soporta perfiles sociales dinámicos (niveles de confianza y notas).

ChromaDB (Puerto 8000): Colección personalidad_bug activa. Almacena tensores multidimensionales que mapean tu estilo, modismos y ritmo de escritura.