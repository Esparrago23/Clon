# Reiniciar desde cero los contenedores
cd docker
docker-compose down -v
docker-compose up -d
cd ..
python -m app.core.init_db
# ingresar info 
python -m scripts.ingest_history
python -m scripts.ingest_instagram

# hacer vectore en chroma
python -m scripts.sync_embeddings

# hacer pruebas
python -m scripts.test_chroma
# 🧠 Project: Shadow - Clon Virtual Privado

Project: Shadow es una arquitectura de Inteligencia Artificial diseñada para operar como un clon cognitivo virtual. El sistema escucha, recuerda y comprende el contexto social y semántico del usuario de forma 100% local (Air-gapped) garantizando privacidad absoluta.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una Arquitectura Hexagonal y está respaldado por un sistema de memoria dual:

| Componente | Tecnología | Función |
| :--- | :--- | :--- |
| **Captura en Vivo** | Playwright + Python | Extrae mensajes de WhatsApp Web leyendo el DOM en tiempo real. |
| **Memoria Relacional** | PostgreSQL + SQLAlchemy | Guarda estructura social: *Quién* habla, en qué *Sala* y *Cuándo*. |
| **Cerebro Semántico** | ChromaDB + HuggingFace | Convierte mensajes a vectores 3D para buscar por intención y tono. |

---

## 🚀 Guía de Ejecución

Antes de ejecutar los scripts, asegúrate de que tus bases de datos estén activas en Docker:
`docker-compose up -d`

El sistema cuenta con dos flujos de trabajo principales: **Tiempo Real** y **Procesamiento de Memoria**.

### 📡 1. Ejecución en Conjunto (Modo Tiempo Real)
Estos scripts se encargan de la "audición" activa del clon. Trabajan de la mano para capturar la mensajería del día a día.

**Paso A: Iniciar el Cazador de Mensajes**
Abre un navegador fantasma, escanea tus chats activos e inyecta los nuevos mensajes a PostgreSQL al instante.
```bash
python -m scripts.MensajesWhatsapp
Paso B: Respaldo Manual de Ingesta (Opcional)
El script anterior guarda un registro físico en mensajes_whatsapp.jsonl. Si PostgreSQL estaba apagado o falló la inyección en vivo, puedes forzar la lectura del JSON hacia la base de datos con:

Bash

python -m scripts.ingest_to_db
🧠 2. Ejecución Independiente (Mantenimiento y Aprendizaje IA)
Estos scripts operan bajo demanda. Se usan para enseñarle al clon tu pasado y entrenar su motor de comprensión.

Ingesta Masiva de Historiales (ingest_history.py)
Procesa exportaciones .txt de WhatsApp en lote. Puedes configurar 1 o múltiples archivos al mismo tiempo editando la variable CHATS_A_PROCESAR dentro del script. Ideal para alimentar el contexto social rápidamente.

Bash

python -m scripts.ingest_history
Sincronización del Cerebro Vectorial (sync_embeddings.py)
Lee todos los mensajes que Tú has enviado en la base PostgreSQL y los pasa por el modelo neuronal local para guardarlos en ChromaDB. Ejecutar siempre después de una ingesta histórica.

Bash

python -m scripts.sync_embeddings
Diagnóstico Semántico (test_chroma.py)
Herramienta de depuración para la IA. Te permite hacerle una pregunta al sistema para verificar qué recuerdos tuyos recupera basados en similitud semántica.

Bash

python -m scripts.test_chroma
📂 Estructura de Directorios
app/: Lógica de negocio (Core, Dominio, Infraestructura, Casos de Uso).

chats/: Directorio temporal para soltar tus exportaciones .txt de WhatsApp.

docker/: Archivos de orquestación de bases de datos.

scripts/: Herramientas ejecutables del proyecto.

whatsapp_session/: Almacenamiento local de la sesión web (evita escanear código QR diario).



Project: Shadow - Documentación de Arquitectura
Visión General
Project: Shadow es un clon virtual local y privado. Actualmente, el sistema es capaz de "escuchar", "recordar" y "entender" el contexto social y semántico del usuario. Todo funciona offline (localmente) garantizando privacidad absoluta (Air-gapped).

El sistema se divide en tres fases principales que ya están operativas:

Captura: Lectura de mensajes en tiempo real y carga de historiales pasados.

Memoria Relacional (PostgreSQL): Almacenamiento estructurado (quién habla, en qué chat y cuándo).

Memoria Semántica (ChromaDB): Vectorización de la personalidad del usuario utilizando modelos de IA para entender el contexto y estilo de escritura.

📂 Estructura del Proyecto (Arquitectura Hexagonal)
El código está dividido en capas para mantenerlo escalable y limpio:

app/: El núcleo de la aplicación.

core/: Configuraciones (config.py) y conexión a la base de datos (database.py, init_db.py).

domain/: Los modelos de datos (person.py, conversation.py, message.py). Definen las reglas del negocio.

application/: Casos de uso (ingest_whatsapp.py). Contiene la lógica para procesar los datos crudos.

infrastructure/: Repositorios (whatsapp.py). Es la única capa que se comunica directamente con PostgreSQL.

chats/: Carpeta temporal donde se colocan los historiales exportados de WhatsApp (.txt) para inyección masiva.

docker/: Contiene docker-compose.yml que levanta los contenedores de PostgreSQL y ChromaDB.

whatsapp_session/: Carpeta generada por Playwright para mantener la sesión de WhatsApp Web abierta (no requiere escanear QR a diario).

🛠️ Catálogo de Scripts (/scripts/)
Aquí están las herramientas ejecutables del sistema. Cada script tiene un propósito específico en el ciclo de vida del dato:

1. MensajesWhatsapp.py (Los "Ojos" del Clon)
¿Qué hace?: Abre un navegador invisible (Playwright), entra a WhatsApp Web y actúa como un "cazador de notificaciones".

Funcionamiento: Detecta cuando llega un mensaje nuevo, identifica el remitente, extrae el texto limpio y lo inyecta en tiempo real a PostgreSQL usando el caso de uso IngestWhatsAppMessageUseCase. También guarda un respaldo en mensajes_whatsapp.jsonl.

Protección: Cuenta con validación de idempotencia (usa whatsapp_id) para asegurar que si se reinicia el script, no se guarden mensajes duplicados.

Cuándo usarlo: Cuando quieras que tu clon escuche en vivo lo que está pasando en tu WhatsApp.

2. ingest_history.py (La Máquina del Tiempo)
¿Qué hace?: Lee archivos .txt exportados directamente desde la app móvil de WhatsApp.

Funcionamiento: Limpia la basura del formato de Android (fechas, "Multimedia omitida", saltos de línea), genera IDs únicos usando Hashes (MD5) y carga miles de mensajes históricos a PostgreSQL en segundos.

Cuándo usarlo: Cuando quieras enseñarle a tu clon cómo hablabas hace meses o años con una persona o grupo específico.

3. ingest_to_db.py (El Respaldo)
¿Qué hace?: Lee el archivo mensajes_whatsapp.jsonl línea por línea y lo inyecta en PostgreSQL.

Cuándo usarlo: Es un script de mantenimiento. Se usa si por alguna razón la base de datos estaba apagada mientras Playwright corría, permitiendo recuperar esos mensajes desde el archivo JSONL.

4. sync_embeddings.py (El Sincronizador de Personalidad)
¿Qué hace?: Construye el cerebro semántico.

Funcionamiento: Se conecta a PostgreSQL, extrae solo los mensajes enviados por "Tú", los pasa por un modelo neuronal local (paraphrase-multilingual-MiniLM-L12-v2) para convertirlos en vectores matemáticos de 384 dimensiones, y los guarda en ChromaDB.

Cuándo usarlo: Debe ejecutarse después de una inyección masiva de historial (ingest_history.py) o de vez en cuando para que ChromaDB aprenda tus nuevas formas de hablar.

5. test_chroma.py (La Herramienta de Diagnóstico)
¿Qué hace?: Prueba si la IA realmente entiende tu contexto.

Funcionamiento: Le das una frase de prueba (ej. "¿Vamos a comer?"), la vectoriza y busca en ChromaDB los 3 recuerdos tuyos que sean matemáticamente (semánticamente) más similares a esa frase.

Cuándo usarlo: Para verificar que ChromaDB está recuperando tus frases correctamente antes de conectarlo al LLM.

💾 Estado Actual de las Bases de Datos
PostgreSQL (Puerto 5432): Modelo relacional perfecto. Ya distingue entre Salas (conversations), Humanos (persons) y sus Textos (messages).

ChromaDB (Puerto 8000): Colección personalidad_bug activa y cargada con tensores que representan la intención de tus palabras pasadas.