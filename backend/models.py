from pydantic import BaseModel
from datetime import datetime

class EventoEmocao(BaseModel):
    id_evento: str
    timestamp: datetime
    camera_id: str
    expressao_dominante: str
    pontuacao: float
    media_emocoes: float
    comportamento: str
    pessoas_unicas_ate_agora: int
