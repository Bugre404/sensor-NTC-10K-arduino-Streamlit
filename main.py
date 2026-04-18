import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime
import matplotlib

# Força o uso de uma janela externa (evita que o programa feche sozinho)
matplotlib.use('TkAgg')

# --- CONFIGURAÇÕES ---
porta_serial = 'COM4'  # Verifique se a sua porta ainda é a COM4
baud_rate = 9600
arquivo_csv = "historico_temperatura.csv"

# Inicializa Serial
try:
    ser = serial.Serial(porta_serial, baud_rate, timeout=1)
    print(f"Conectado em {porta_serial}. Gravando dados...")
except:
    print("Erro: Verifique se o Arduino está conectado e o Serial Monitor fechado.")
    exit()

# Cria o arquivo e escreve o cabeçalho (se o arquivo não existir)
with open(arquivo_csv, "w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(["Data", "Hora", "Temperatura_C"])

# Listas para o gráfico
x_horas = []
y_temps = []

fig, ax = plt.subplots(figsize=(10, 5))
plt.subplots_adjust(bottom=0.25)  # Espaço para as horas não cortarem


def update(frame):
    try:
        if ser.in_waiting > 0:
            linha = ser.readline().decode('utf-8').strip()

            if linha:
                temp = float(linha)

                # Captura tempo real
                agora = datetime.now()
                data_str = agora.strftime("%Y-%m-%d")
                hora_str = agora.strftime("%H:%M:%S")

                # 1. SALVAR NO CSV
                with open(arquivo_csv, "a", newline="") as f:
                    escritor = csv.writer(f)
                    escritor.writerow([data_str, hora_str, temp])

                # 2. ATUALIZAR GRÁFICO
                y_temps.append(temp)
                x_horas.append(hora_str)

                # Mantém apenas os últimos 30 pontos na tela para não embolar
                x_plot = x_horas[-30:]
                y_plot = y_temps[-30:]

                ax.clear()
                ax.plot(x_plot, y_plot, marker='o', color='red', linestyle='-')

                # Estética do Gráfico
                ax.set_title("Monitoramento de Temperatura NTC 10K")
                ax.set_ylabel("Graus Celsius (°C)")
                ax.set_xlabel("Horário da Leitura")
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)

                # Ajusta o limite do eixo Y para a temperatura atual
                ax.set_ylim(min(y_plot) - 2, max(y_plot) + 2)

    except Exception as e:
        print(f"Aguardando dados... {e}")


# Animação: atualiza a cada 1000ms (1 segundo)
ani = FuncAnimation(fig, update, interval=1000, cache_frame_data=False)

plt.show()

# Fecha ao sair
ser.close()
print(f"Dados salvos com sucesso em {arquivo_csv}")

