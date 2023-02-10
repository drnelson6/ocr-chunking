# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 14:08:30 2023

@author: dnelson
"""

from pdf2image import convert_from_path
import tempfile
import numpy as np
# from PIL import Image
import pytesseract
import cv2


def convert_pdf(pdf_doc, dpi):
    images = []
    images.extend(
                    list(
                            map(
                                lambda image: cv2.cvtColor(
                                    np.asarray(image), code=cv2.COLOR_RGB2BGR
                                    ),
                                convert_from_path(pdf_doc, dpi=dpi),
                                )
                            )
                    )
    return images


file_path = 'P:/Center for Digital Scholarship/Fellows/Maeve Kane/baptismal-records-pdfs/type 2 - most common/ny-success-drc-ed-jfrost.pdf'

# list for holding output
output = []

# get temporary directory of Image objects
with tempfile.TemporaryDirectory() as path:
    images = convert_pdf(file_path, 300)
    # run process on each image
    for i in images:
        gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)
        # threshing to improve contouring - need binary image
        gray = cv2.threshold(gray, 0, 255,
                             cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
        # set kernel size - fudge numbers to capture bigger or smaller regions
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        # dilate image - create large blobs of text to detect clusters
        dilation = cv2.dilate(gray, rect_kernel, iterations=3)
        # standard contouring method
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_NONE)
        # get bbox for all contours and draw to Image object
        tesseract_output = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            rect = cv2.rectangle(i, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped = i[y:y + h, x:x + w]
            text = pytesseract.image_to_string(cropped)
            tesseract_output.append(text)
        output.append(''.join(tesseract_output))
    # uncomment to view image output
    # cv2.imshow('Window', i)
    # cv2.waitKey(0)

with open('output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
