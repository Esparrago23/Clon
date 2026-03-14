from datetime import datetime
from app.core.database import SessionLocal
from app.domain.models.core_state import CoreState

class PersonaStateManager:
    def __init__(self):
        self.db = SessionLocal()
        self.state = self._get_or_create_state()

    def _get_or_create_state(self):
        # Buscamos la mente de Bug en la base de datos
        state = self.db.query(CoreState).filter_by(name="Bug").first()
        if not state:
            state = CoreState(
                name="Bug",
                energy=0.7,
                mood="neutral",
                social_interest=0.7,
                cognitive_load=0.3,
                last_update=datetime.now()
            )
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        return state

    def update_time_decay(self):
        """Simula el paso del tiempo: Recupera energía y baja el estrés"""
        now = datetime.now()
        hours = (now - self.state.last_update).total_seconds() / 3600

        # Recuperas 5% de energía por hora, y el estrés baja 4% por hora
        self.state.energy = min(1.0, self.state.energy + 0.05 * hours)
        self.state.cognitive_load = max(0.0, self.state.cognitive_load - 0.04 * hours)
        
        # Si han pasado más de 12 horas desde el último mensaje, tu humor se resetea a neutral
        if hours > 12:
            self.state.mood = "neutral"

        self.state.last_update = now
        self.db.commit()

    def update_from_message(self, message: str):
        """Ajusta tus emociones basándose en lo que te acaban de escribir"""
        text = message.lower()

        if any(word in text for word in ["fiesta", "salir", "antro", "tacos", "comer"]):
            self.state.social_interest += 0.1

        if any(word in text for word in ["tarea", "trabajo", "examen", "proyecto"]):
            self.state.cognitive_load += 0.2
            self.state.energy -= 0.1

        if any(word in text for word in ["jaja", "xd", "😂"]):
            self.state.mood = "positivo"

        if any(word in text for word in ["problema", "mal", "triste", "enfermo"]):
            self.state.mood = "negativo"
            self.state.energy -= 0.1

        self._normalize()
        self.db.commit()

    def _normalize(self):
        """Asegura que los valores no se salgan del rango 0.0 a 1.0"""
        self.state.energy = max(0.0, min(1.0, self.state.energy))
        self.state.social_interest = max(0.0, min(1.0, self.state.social_interest))
        self.state.cognitive_load = max(0.0, min(1.0, self.state.cognitive_load))

    def summary(self) -> str:
        """Devuelve el texto que se inyectará en el Prompt de Ollama"""
        return (
            f"Energía física y social: {self.state.energy:.2f}/1.0\n"
            f"Estado de ánimo actual: {self.state.mood}\n"
            f"Interés en conversar: {self.state.social_interest:.2f}/1.0\n"
            f"Carga mental/Estrés: {self.state.cognitive_load:.2f}/1.0\n"
        )
        
    def close(self):
        self.db.close()