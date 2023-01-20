"""Take picture from webcam"""
import os
import cv2
import pytesseract

# TODO get info from serial number api
print(f"Importing {os.path.basename(__file__)}...")

CAM_PORT = 0
WIDTH = 1920
HEIGHT = 1080


def take_serial_image():
    """Take image from document camera and return string of serial number."""
    capture = cv2.VideoCapture(CAM_PORT)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    while True:
        result = False
        while not result:

            result, serial_image = capture.read()
            serial_image = cv2.cvtColor(serial_image, cv2.COLOR_BGR2GRAY)
            (_, black_and_white_image) = cv2.threshold(serial_image, 127, 255, cv2.THRESH_BINARY)

            if result:
                serial_image_data = pytesseract.image_to_data(
                    black_and_white_image, config="--psm 12", output_type=pytesseract.Output.DICT
                )

        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf > 5:
                if word[0:1] == "D":
                    print(word)

        cv2.imshow("Serial Image", black_and_white_image)
        if cv2.waitKey(1000) & 0xFF == ord("q"):
            quit()
        cv2.destroyAllWindows()


take_serial_image()
