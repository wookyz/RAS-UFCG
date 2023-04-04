import cv2

imagem = cv2.imread('entrada.jpg')

# (b, g, r) = imagem[0, 0] #veja que a ordem BGR e não RGB
# print('O pixel (0, 0) tem as seguintes cores:')
# print('Vermelho:', r, 'Verde:', g, 'Azul:', b)

# for i in range(0, imagem.shape[0]):
#     for j in range(0, imagem.shape[1]):
#         imagem[i, j] = (255, 0, 0)
# cv2.imshow("Entrada modificada", imagem)
# cv2.waitKey(0)

# for y in range(0, imagem.shape[0]):
#     for x in range(0, imagem.shape[1]):
#         imagem[y, x] = (x % 256, y % 256, x % 256)
# cv2.imshow("Entrada modificada", imagem)
# cv2.waitKey(0)

# for y in range(0, imagem.shape[0]):
#     for x in range(0, imagem.shape[1]):
#         imagem[y, x] = (0, (x*y) % 256, 0)
# cv2.imshow("Entrada modificada", imagem)
# cv2.waitKey(0)

for y in range(0, imagem.shape[0], 10):
    for x in range(0, imagem.shape[1], 10):
        imagem[y, x] = (0, 255, 2500)
cv2.imshow("Entrada modificada", imagem)
cv2.waitKey(0)
