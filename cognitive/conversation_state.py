from datetime import datetime

class ConversationState:
    def __init__(self):
        self.topic = None
        self.intent_active = None
        self.plan_time = None
        self.status = "IDLE" # IDLE, NEGOTIATING, CONFIRMED
        self.last_update = datetime.now()

    def update(self, intent: str, message: str):
        text = message.lower()

        # Si detectamos una invitación, entramos en modo negociación
        if intent == "invitacion":
            self.intent_active = "plan"
            self.status = "NEGOTIATING"

        # Si estamos negociando y mencionan tiempo, lo registramos
        if self.status == "NEGOTIATING" and any(w in text for w in ["hora", "hr", "cuando", "10", "pm", "am", "tarde", "temprano"]):
            self.plan_time = message
            self.status = "NEGOTIATING"

        # Si confirman, cerramos el trato
        if any(w in text for w in ["va", "jalo", "ok", "smn", "arre", "listo"]):
            self.status = "CONFIRMED"
            
        # Reseteo simple si pasa mucho tiempo (opcional para el futuro)
        self.last_update = datetime.now()

    def summary(self):
        if self.status == "IDLE":
            return "Ningún plan activo. Charla casual."
        return (
            f"ESTADO DE LA CONVERSACIÓN: {self.status}\n"
            f"TEMA ACTIVO: {self.intent_active}\n"
            f"HORA PROPUESTA EN LA MESA: {self.plan_time if self.plan_time else 'Aún no definida'}\n"
        )