FROM ppawlowski/opencv:rpizero
RUN apk add -q zlib-dev libjpeg-turbo-dev libjpeg alpine-sdk
RUN pip install flask jsonpickle Pillow tesseract image pytesseract
ADD tessdata/ /usr/share/tessdata/
