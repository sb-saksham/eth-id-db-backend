import re
import numpy
from PIL import Image
import cv2
import pytesseract

NameFormats = [
    re.compile(r"^name : [A-Za-z]+ [A-Za-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name: [A-Za-z]+ [A-Za-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name :[A-Za-z]+ [A-Za-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name[a-z]+ [a-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name[a-z]+[a-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name :[A-Za-z]+[A-Za-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name: [A-Za-z]+[A-Za-z]+$", re.IGNORECASE and re.MULTILINE),
    re.compile(r"^name : [A-Za-z]+[A-Za-z]+$", re.IGNORECASE and re.MULTILINE),
]


def recognize_all_text(image):
    all_recognized_text = ""
    pytesseract.pytesseract.tesseract_cmd = r'F:\Applications\tesseract\tesseract.exe'
    img = Image.open(image)
    img1 = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)


    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = img1[y:y + h, x:x + w]
        all_recognized_text += str(pytesseract.image_to_string(cropped))
    return all_recognized_text


def confirm_name(id_image, fn):
    all_text = recognize_all_text(id_image).lower()
    all_text = ''.join(filter(str.isalpha or str.isspace, all_text))
    name_verified = False
    if str(fn).lower() in all_text:
        name_verified = True
    return name_verified
