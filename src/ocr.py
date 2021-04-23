import numpy as np
import pytesseract
import cv2
import re
import functools
print = functools.partial(print, flush=True)

print("Tesseract version:")
print(pytesseract.get_tesseract_version())

latest_state = 43442
possible_step = 10

def remove_whitespaces(str):
    return re.sub(r'\s+','',str)

def is_possible(state_str):
    if (len(state_str)==0):
        return -1
    global latest_state
    global possible_step
    print("\t\tis_possible "+state_str)
    print(f"\t\t\tlatest state: {latest_state}\tstep: {possible_step}")
    try:
        state = int(state_str)
        if (latest_state<=state<=(latest_state+possible_step)):
            latest_state=state
            print("\tyes")
            return state
        else:
            print(f"\tnot in range {latest_state} < {state} < {possible_step+latest_state}")
            return -1
    except:
        print("\terror")
        return -1

def convert_letters(str):
    return str \
        .replace('S','5') \
        .replace('Z','2') \
        .replace('A','4') \
        .replace('O','0') \
        .replace('B','8') \
        .replace('I','1')

def digits_regex(str):
    regex = re.compile('.*(04[\d]{4}).*')
    regex_results = regex.findall(str)
    if (len(regex_results)==1):
        return regex_results[0]
    else:
        return ""

def process_image(oem,psm,image):
    print("\tProcessing entire image")
    ocr_result = pytesseract.image_to_string(
        image,
        config=f"--psm {psm} --oem {oem} -c tessedit_char_whitelist=SZBAOI0123456789").strip()
    print(f"\t\tOCR result: {remove_whitespaces(ocr_result)}")
    ocr_result = convert_letters(ocr_result)
    print(f"\t\tafter adjusting: {remove_whitespaces(ocr_result)}")
    return digits_regex(ocr_result)

def process_edges(image):
    print("\tProcessing image contours")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.bitwise_not(gray_image)
    blur = cv2.GaussianBlur(gray_image,(5,5),0)
    thresh = cv2.adaptiveThreshold(blur,255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, \
    95,2)
    edges = cv2.Canny(thresh, 50, 90, apertureSize=3)
    finalresult = dict()
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for (i, c) in enumerate(contours):
      if cv2.contourArea(c)>100:
          # 100 dla pradu
          # 400 dla wody
        (x, y, w, h) = cv2.boundingRect(c)
        margin=5
        roi = blur[y-margin:y + h+margin, x-margin:x + w+margin]
        for oem in range(3,4):
            for psm in [8,6]:
                try:
                    tess_result = pytesseract.image_to_string(roi, config=f"--psm {psm} --oem {oem} -c tessedit_char_whitelist=SZBAOI0123456789").strip()
                    tess_result = convert_letters(tess_result)
                    if (len(tess_result)==1):
                        finalresult[x]=tess_result
                    elif is_possible(tess_result) != -1:
                        return tess_result
                except:
                # except pytesseract.TesseractError as e:
                    pass
    print("\t\tContours result: "+str(dict(sorted(finalresult.items())).values()))
    result_as_str = "".join(dict(sorted(finalresult.items())).values())
    result_as_str = digits_regex(result_as_str)
    return result_as_str

def ocr(path):
    image = cv2.imread(path)
    height, width, channels = image.shape
    print(f"New image to analyze {height} x {width}, channels {channels}")
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.bitwise_not(gray_image)
    blur = cv2.GaussianBlur(gray_image,(5,5),0)
    result = is_possible(process_image(3,12,blur))
    if (result==-1):
        result = is_possible(process_image(3,11,blur))
        if (result == -1):
            result = is_possible(process_edges(image))
    return result
