"""Take picture from webcam"""
import os
import cv2
import pytesseract

# TODO get info from serial number api
print(f"Importing {os.path.basename(__file__)}...")

CAM_PORT = 2

cam = cv2.VideoCapture(CAM_PORT)

result, serial_image = cam.read()

if result:
    print("Got Image")
    cv2.imshow("Test", serial_image)
    cv2.waitKey(0)
    cv2.destroyWindow("test")
else:
    print("No image")


cv2.imshow("test", serial_image)
cv2.waitKey(0)
gray = cv2.cvtColor(serial_image, cv2.COLOR_BGR2GRAY)
ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

cv2.imshow("test", gray)
cv2.waitKey(0)

im2 = serial_image.copy()

for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)

    # Drawing a rectangle on copied image
    rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Cropping the text block for giving input to OCR
    cropped = im2[y : y + h, x : x + w]

    # Apply OCR on the cropped image
    text = pytesseract.image_to_string(cropped)
    print(text)
