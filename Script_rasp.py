import cv2
import time
import os
import bluetooth
from ultralytics import YOLO

# ===============================
# CONFIGURAÇÕES
# ===============================
MODEL_PATH = '/home/brayon/yolov5/yolov5n.pt'
TARGET_CLASS_ID = 0  # 0 = pessoa
OUTPUT_FOLDER = "capturas"
ESP32_MAC = "7C:9E:BD:3A:08:6E"
TEMPO_MAXIMO = 10  # segundos
MAX_FOTOS = 5
INTERVALO_FOTOS = TEMPO_MAXIMO / MAX_FOTOS
PORTA_BLUETOOTH = 1

# ===============================
# FUNÇÕES
# ===============================
def enviar_alerta_bluetooth(mac_address):
    """Envia sinal 'A' via Bluetooth para o ESP32 acionar buzzer."""
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        print(f"[BLUETOOTH] Conectando ao ESP32 ({mac_address})...")
        sock.connect((mac_address, PORTA_BLUETOOTH))
        sock.send("A")
        print("[BLUETOOTH] Alerta enviado! ESP32 deve acionar o buzzer.")
    except bluetooth.btcommon.BluetoothError as err:
        print(f"[BLUETOOTH] Erro de conexão: {err}")
    finally:
        sock.close()

# ===============================
# PREPARAÇÃO
# ===============================
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(0)

detectando = False
inicio_detec = 0
fotos_tiradas = 0
proxima_foto_timestamp = 0 # <<-- NOVA VARIÁVEL

# ===============================
# LOOP PRINCIPAL
# ===============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, classes=[TARGET_CLASS_ID], verbose=False)
    detections = results[0].boxes

    pessoa_detectada_neste_frame = len(detections) > 0

    if pessoa_detectada_neste_frame:
        if not detectando:
            # Bloco que roda apenas no início de uma NOVA sequência de detecção
            detectando = True
            inicio_detec = time.time()
            fotos_tiradas = 0
            proxima_foto_timestamp = time.time() # <<-- Inicia o cronômetro para a primeira foto
            print("\n[INFO] Nova sequência de detecção iniciada.")
            enviar_alerta_bluetooth(ESP32_MAC)

        tempo_atual = time.time()
        tempo_passado = tempo_atual - inicio_detec

        # Verifica se está na hora de tirar a próxima foto
        if fotos_tiradas < MAX_FOTOS and tempo_atual >= proxima_foto_timestamp:
            nome_arquivo = os.path.join(OUTPUT_FOLDER, f"captura_{int(time.time())}.jpg")
            cv2.imwrite(nome_arquivo, frame)
            fotos_tiradas += 1
            print(f"[INFO] Foto {fotos_tiradas}/{MAX_FOTOS} salva: {nome_arquivo}")
            proxima_foto_timestamp = time.time() + INTERVALO_FOTOS # <<-- Agenda a próxima foto

        # Reset após o tempo máximo
        if tempo_passado > TEMPO_MAXIMO:
            detectando = False
            print("[INFO] Ciclo de detecção finalizado.\n")

    else: # Se nenhuma pessoa for detectada neste frame
        # Se estávamos no meio de uma detecção, reseta também
        if detectando:
            detectando = False
            print("[INFO] Alvo perdido. Ciclo de detecção finalizado.\n")

    # Linhas de display comentadas para rodar via SSH
    # annotated_frame = results[0].plot()
    # cv2.imshow("YOLO Webcam", annotated_frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

cap.release()
# cv2.destroyAllWindows()
