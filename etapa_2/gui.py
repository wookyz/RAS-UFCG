from collections import deque
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk


width = 680
height = 520
points = deque(maxlen=32)
(dx, dy) = (0, 0)

root = tk.Tk()
root.title("GUI")
root.geometry(f"{width}x{height}")

guiFrame = tk.Frame(root, padx=10, pady=10)
guiFrame.grid(row=0, column=0)

controlFrame = tk.Frame(guiFrame, padx=10, pady=10, border=2, relief=tk.GROOVE)
controlFrame.grid(row=0, column=0)


def createVarSlide(parent, varName, label, baseValue=0, row=0, column=0):
    frameVarSlide = tk.Frame(parent)
    frameVarSlide.grid(row=row, column=column)

    var = tk.IntVar()
    var.set(baseValue)

    label = tk.Label(frameVarSlide, text=label)
    label.grid(row=0, column=0)

    entry = tk.Entry(frameVarSlide, textvariable=var, width=5)
    entry.grid(row=1, column=0)

    slider = tk.Scale(frameVarSlide, from_=0, to=255, orient=tk.HORIZONTAL,
                      variable=var, length=200, width=15)
    slider.grid(row=2, column=0)

    return var, slider, entry


hueMin, hueMinSlider, hueMinEntry = createVarSlide(
    controlFrame, "hueMin", "HueMin", baseValue=0, row=0, column=0)
saturationMin, saturationMinSlider, saturationMinEntry = createVarSlide(
    controlFrame, "saturationMin", "SaturationMin", baseValue=0, row=0, column=1)
valueMin, valueMinSlider, valueMinEntry = createVarSlide(
    controlFrame, "valueMin", "ValueMin", baseValue=0, row=0, column=2)
saturationMax, saturationMaxSlider, saturationMaxEntry = createVarSlide(
    controlFrame, "saturationMax", "SaturationMax", baseValue=255, row=1, column=1)
valueMax, valueMaxSlider, valueMaxEntry = createVarSlide(
    controlFrame, "valueMax", "ValueMax", baseValue=255, row=1, column=2)
hueMax, hueMaxSlider, hueMaxEntry = createVarSlide(
    controlFrame, "hueMax", "HueMax", baseValue=255, row=1, column=0)

colorsDefaultFrame = tk.Frame(controlFrame)
colorsDefaultFrame.grid(row=2, column=0, columnspan=3)

colorsDefault = {
    "Vermelho": [np.array([130, 25, 105]), np.array([255, 255, 255])],
    "Verde": [np.array([30, 75, 70]), np.array([100, 255, 255])],
    "Azul": [np.array([100, 150, 70]), np.array([130, 255, 255])],
    "Amarelo": [np.array([20, 50, 145]), np.array([40, 255, 255])],
}


def setValuesColors(arrays):
    hueMin.set(arrays[0][0])
    saturationMin.set(arrays[0][1])
    valueMin.set(arrays[0][2])
    hueMax.set(arrays[1][0])
    saturationMax.set(arrays[1][1])
    valueMax.set(arrays[1][2])


for i, color in enumerate(colorsDefault):
    button = tk.Button(colorsDefaultFrame, text=color,
                       command=lambda color=color:
                       setValuesColors(colorsDefault[color]))
    button.grid(row=0, column=i)

quitButton = tk.Button(controlFrame, text="Quit", command=quit)
quitButton.grid(row=3, column=1)

videosFrame = tk.Frame(guiFrame, padx=10, pady=10)
videosFrame.grid(row=1, column=0)

normalCapture = tk.Label(videosFrame, text="Normal Capture")
normalCapture.grid(row=0, column=0)

maskCapture = tk.Label(videosFrame, text="Masked Capture")
maskCapture.grid(row=0, column=1)

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width//4)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height//4)
cam.set(cv2.CAP_PROP_FPS, 30)


def displayFrame(frame, label, loop):
    image = ImageTk.PhotoImage(image=Image.fromarray(frame))
    label.imgtk = image
    label.configure(image=image)
    label.after(10, loop)


def showFrame():
    sucess, frame = cam.read()

    frame = cv2.flip(frame, 1)
    hsv = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), (11, 11), 0)
    mask = cv2.inRange(hsv,
                       np.array(
                           [hueMin.get(), saturationMin.get(), valueMin.get()]),
                       np.array(
                           [hueMax.get(), saturationMax.get(), valueMax.get()]))
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
                center = (x + w//2, y + h//2)
                points.append(center)

                for i in np.arange(1, len(points)):
                    if points[i - 1] is None or points[i] is None:
                        continue
                    thickness = int(np.sqrt(float(i + 1) / 32) * 10)
                    cv2.line(frame, points[i - 1],
                             points[i], (0, 0, 255), thickness)

    if not contours:
        points.clear()

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    displayFrame(frame, normalCapture, showFrame)

    global lastFrameMask
    lastFrameMask = mask.copy()
    global lastFrameGray
    lastFrameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def showFrame2():
    displayFrame(lastFrameMask, maskCapture, showFrame2)


showFrame()
showFrame2()


def quit(event=None):
    cam.release()
    root.destroy()


root.mainloop()
