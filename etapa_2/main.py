from collections import deque
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

"""
O código abaixo é uma junção do Tkinter com o OpenCV, para criar uma interface que permite
a visualização da captura de vídeo e o uso de sliders para definir os valores de cores dentro
de um determinado intervalo. Dessa forma, a interface gráfica contém duas capturas, uma
normal e outra com a máscara aplicada. A máscara é aplicada com base nos valores dos sliders.
Os valores podem ser determinados pelos slides, ou alterando os valores diretamente nos
campos de texto. Também é possível escolher uma das cores padrão para definir os valores dos
sliders.
"""


# CONSTANTES.
WIDTH = 680
HEIGHT = 520
DELAY = 15
BUFFER_SIZE = 16
MIN_AREA_CONTOUR = 500
QTD_VAR_SLIDES_POR_LINHA = 3

# Fila para armazenar os últimos 32 pontos para desenhar a linha.
points = deque(maxlen=16)
(dx, dy) = (0, 0)

# Variáveis para o controle de quantos sliders serão criados e quantos por linha.
contadorVarSliders = 0
colorValues = {}

# Cria a janela.
root = tk.Tk()
root.title("GUI")
root.geometry(f"{WIDTH}x{HEIGHT}")

# Cria o container principal.
guiFrame = tk.Frame(root, padx=10, pady=10)
guiFrame.grid(row=0, column=0)

# Cria o container para os controles.
controlFrame = tk.Frame(guiFrame, padx=10, pady=10, border=2, relief=tk.GROOVE)
controlFrame.grid(row=0, column=0)


def createVarSlide(varName: str, baseValue=0) -> tk.IntVar:
    # Função para criar um slider associado a uma variável.
    frameVarSlide = tk.Frame(controlFrame)
    global contadorVarSliders
    frameVarSlide.grid(
        row=contadorVarSliders // QTD_VAR_SLIDES_POR_LINHA,
        column=contadorVarSliders % QTD_VAR_SLIDES_POR_LINHA
    )

    var = tk.IntVar()
    var.set(baseValue)

    label = tk.Label(frameVarSlide, text=varName.capitalize())
    label.grid(row=0, column=0)

    entry = tk.Entry(frameVarSlide, textvariable=var, width=5)
    entry.grid(row=1, column=0)

    slider = tk.Scale(frameVarSlide, from_=0, to=255, orient=tk.HORIZONTAL,
                      variable=var, length=200, width=15)
    slider.grid(row=2, column=0)

    contadorVarSliders += 1
    colorValues[varName] = var

    return var


# Cria os sliders.
createVarSlide("Matiz Mínima")
createVarSlide("Saturação Mínima")
createVarSlide("Valor Mínimo")
createVarSlide("Matiz Máxima")
createVarSlide("Saturação Máxima")
createVarSlide("Valor Máximo")

# Cria um container para os botões de cores padrão.
defaultColorsFrame = tk.Frame(controlFrame)
defaultColorsFrame.grid(row=2, column=0, columnspan=3)

# Dicionário com o alcance de cores padrão.
defaultColors = {
    "Vermelho": [np.array([130, 25, 105]), np.array([255, 255, 255])],
    "Verde": [np.array([30, 75, 70]), np.array([100, 255, 255])],
    "Azul": [np.array([100, 150, 70]), np.array([130, 255, 255])],
    "Amarelo": [np.array([20, 50, 145]), np.array([40, 255, 255])],
}


def setValuesColors(color):
    # Função para definir os valores dos sliders de acordo com a cor padrão.
    arrays = defaultColors[color]
    for i, var in enumerate(colorValues):
        colorValues[var].set(arrays[i // 3][i % 3])


# Cria os botões de cores padrão.
for i, color in enumerate(defaultColors):
    button = tk.Button(defaultColorsFrame, text=color,
                       command=lambda color=color:
                       setValuesColors(color))
    button.grid(row=0, column=i)

# Cria o botão de sair.
quitButton = tk.Button(controlFrame, text="Sair", command=quit)
quitButton.grid(row=3, column=0, columnspan=3)

# Cria o container para os vídeos.
videosFrame = tk.Frame(guiFrame, padx=10, pady=10)
videosFrame.grid(row=1, column=0)

# Cria os labels para os vídeos, é onde os frames serão exibidos.
normalCapture = tk.Label(videosFrame, text="Normal")
normalCapture.grid(row=0, column=0)
maskCapture = tk.Label(videosFrame, text="Masked")
maskCapture.grid(row=0, column=1)

# Inicia a captura de vídeo, define o tamanho da captura e a taxa de quadros.
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH//2)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT//2)
cam.set(cv2.CAP_PROP_FPS, 30)


def displayFrame(frame, label, loop):
    # Função para exibir o frame no label e atualizar o frame a cada 15ms.
    image = ImageTk.PhotoImage(image=Image.fromarray(frame))
    label.imgtk = image
    label.configure(image=image)
    label.after(DELAY, loop)


def showFrame():
    # Função para exibir o frame normal e o frame com a máscara.
    sucess, frame = cam.read()  # Captura a imagem como um numpy array.

    frame = cv2.flip(frame, 1)  # Espelha a imagem.

    # Transforma a imagem em HSV e aplica um blur.
    hsv = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), (11, 11), 0)

    # Cria a máscara com base nos valores dos sliders.
    rangeMin = np.array(
        [colorValues["Matiz Mínima"].get(), colorValues["Saturação Mínima"].get(),
         colorValues["Valor Mínimo"].get()])
    rangeMax = np.array(
        [colorValues["Matiz Máxima"].get(), colorValues["Saturação Máxima"].get(),
         colorValues["Valor Máximo"].get()])
    mask = cv2.inRange(hsv, rangeMin, rangeMax)

    # Aplica erosão e dilatação para remover ruídos.
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Aplica a máscara na imagem.
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        for contour in contours:
            # Se o contorno for maior que o mínimo, desenha o retângulo.
            if cv2.contourArea(contour) > MIN_AREA_CONTOUR:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
                center = (x + w//2, y + h//2)  # Ponto central do retângulo.
                points.append(center)

                # Para cada ponto, desenha uma linha entre ele e o anterior.
                for i in np.arange(1, len(points)):
                    if points[i - 1] is None or points[i] is None:
                        continue
                    thickness = int(np.sqrt(float(i + 1) / BUFFER_SIZE) * 10)
                    cv2.line(frame, points[i - 1],
                             points[i], (0, 0, 255), thickness)

    # Se não houver contornos, não há pontos, portanto, limpa a lista.
    if not contours:
        points.clear()

    # converte a imagem para RGB para exibir no tkinter.
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    displayFrame(frame, normalCapture, showFrame)

    # Copia a máscara para ser exibida no segundo label.
    global lastFrameMask
    lastFrameMask = mask.copy()


def showFrame2():
    # Exibe a máscara no segundo label.
    displayFrame(lastFrameMask, maskCapture, showFrame2)


# Inicia a exibição dos frames.
showFrame()
showFrame2()


def quit():
    # Função para fechar a janela e a captura de vídeo.
    cam.release()
    root.destroy()


# Inicia o loop principal.
root.mainloop()
