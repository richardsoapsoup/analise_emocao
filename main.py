import cv2
from fer import FER
from elasticsearch import Elasticsearch
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

elastic_url = os.getenv("ELASTIC_URL")
elastic_user = os.getenv("ELASTIC_USER")
elastic_password = os.getenv("ELASTIC_PASSWORD")

# Inicializa o detector de emoções
detector = FER(mtcnn=True)

# Conexão com Elasticsearch
es = Elasticsearch(
    elastic_url,
    basic_auth=(elastic_user, elastic_password)
    )  

# Abre câmera (0 = webcam local ou substitua por URL RTSP)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detecta emoções
    results = detector.detect_emotions(frame)

    for result in results:
        # Local da face
        (x, y, w, h) = result["box"]

        # Emoções detectadas
        emotions = result["emotions"]
        top_emotion = max(emotions, key=emotions.get)
        score = emotions[top_emotion]

        # Regras básicas de comportamento
        if top_emotion == "angry" and score > 0.6:
            comportamento = "potencialmente agressivo"
        elif top_emotion == "sad" and score > 0.6:
            comportamento = "depressivo"
        elif top_emotion == "happy" and score > 0.6:
            comportamento = "positivo"
        else:
            comportamento = "neutro"

        # Documento a ser enviado
        doc = {
            "timestamp": datetime.utcnow().isoformat(),
            "camera_id": "entrada_1",
            "expressao_dominante": top_emotion,
            "pontuacao": round(score, 2),
            "comportamento": comportamento,
        }

        # Envia para Elasticsearch
        es.index(index="analise_comportamento", document=doc)

        # Desenha retângulo no rosto
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Texto com emoção e pontuação
        texto = f"{top_emotion} ({score:.2f})"
        cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.9, (255, 255, 255), 2, cv2.LINE_AA)

    # Exibe a imagem
    cv2.imshow("Análise de Emoções", frame)

    # Pressione 'q' para parar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
