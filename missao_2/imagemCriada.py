import numpy as np
import cv2

imagem = np.zeros((300, 300, 3), np.uint8)
imagem[:] = (255, 255, 255)

cv2.circle(imagem, (100, 100), 50, (0, 0, 255), -1)
cv2.circle(imagem, (200, 100), 50, (0, 255, 0), -1)
cv2.circle(imagem, (150, 150), 50, (255, 0, 0), -1)

cv2.imshow("Imagem Criada", imagem)
cv2.waitKey(0)

cv2.imwrite("imagemCriada.jpg", imagem)
