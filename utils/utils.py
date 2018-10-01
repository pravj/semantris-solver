import time
import numpy as np
import pyautogui
import pytesseract
import cv2


def bgr_to_hue_value(color):
    """
    Convert a list ([B, G, R]) of BGR color to approximate Hue value
    """

    c = np.uint8([[color]])
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    return hsv[0][0]


def get_image_string(image):
    """
    Return word string from a given image using OCR/tesseract
    :param image: parent image
    :return: (str) detected word string in the image
    """

    return pytesseract.image_to_string(image, config='-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')


def get_screen_shot(region=None, wait_time=0):
    """
    region: four-integer tuple of the left, top,
    width, and height of the region to capture
    wait_time: (int) seconds to wait before taking screen shot
    """

    print('Waiting {} seconds before screen shot'.format(wait_time))
    print('Please change the browser window to semantris blocks mode')
    time.sleep(wait_time)

    return pyautogui.screenshot(region=region)


def color_tracked_image(image, bgr_color):
    """
    Return the color tracked version of a given image

    :param image: parent image
    :param bgr_color: (list) color values in BGR space
    :return:
    """

    frame = np.array(image)

    # Convert RGB to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # define range of a color to track (blue) in HSV
    # lower_color_range = np.array([90,50,50])
    # upper_color_range = np.array([110,255,255])

    # get approximate hue value for the given color
    hue_value = bgr_to_hue_value(bgr_color)[0]

    # define range of a color to track (green) in HSV
    lower_color_range = np.array([hue_value - 10, 50, 50])
    upper_color_range = np.array([hue_value + 10, 255, 255])

    # threshold the HSV image to get only blue colors
    mask_color_range = cv2.inRange(hsv, lower_color_range, upper_color_range)

    # Bitwise-AND mask and original images
    return cv2.bitwise_and(frame, frame, mask=mask_color_range)


def get_maximum_area_contour(image):
    """
    Convert color specific image to image with maximum block contour

    :param image: parent image
    :return: image containing maximum block contour
    """

    # grayscale version of the single color image
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # bilateral filter is effective when you want to
    # keep the edges sharp while removing noise
    image_gray = cv2.bilateralFilter(image_gray, 10, 50, 50)

    # find contour in gray scale image after applying erosion and dilation
    _, thresh = cv2.threshold(image_gray, 75, 255, 0)
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)

    _, contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # finding contour with maximum area
    max_area_contour_index = 0
    max_area_contour = 0

    for i, contour in enumerate(contours):
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        image_gray = cv2.drawContours(image_gray, [box], 0, (0, 255, 0), 10)

        print('perimeter', cv2.arcLength(contour, True))
        area = cv2.contourArea(contour)
        print('area', area)

        if cv2.contourArea(contour) >= max_area_contour:
            max_area_contour = area
            max_area_contour_index = i

    # mask out the image with maximum area contour
    mask_contour = np.zeros(image_gray.shape[:2], np.uint8)
    cv2.drawContours(mask_contour, [contours[max_area_contour_index]], -1, 255, -1)
    max_area_contour_image = cv2.bitwise_and(image, image, mask=mask_contour)

    max_area_contour_image_gray = cv2.cvtColor(
        max_area_contour_image,
        cv2.COLOR_RGB2GRAY
    )
    _, max_area_contour_image_bw = cv2.threshold(
        max_area_contour_image_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )

    max_area_contour_image_bw_inverted = cv2.bitwise_not(max_area_contour_image_bw)
    return max_area_contour_image_bw_inverted - cv2.bitwise_not(mask_contour)
