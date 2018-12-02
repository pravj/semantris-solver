import time
import random
import numpy as np
import pyautogui
import pytesseract
import cv2
from sklearn.cluster import KMeans
from datetime import datetime


def bgr_to_hsv_value(color):
    """
    Convert a list ([B, G, R]) of BGR color to HSV
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


def find_histogram(clt):
    """
    Return an image histogram with k clusters
    Referred from https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097

    :param: clt
    :return: hist
    """

    num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=num_labels)

    hist = hist.astype('float')
    hist /= hist.sum()

    return hist


def is_color_gray(r, g, b):
    """
    Check if given RGB values represent a gray color or not

    :param r: R
    :param g: G
    :param b: B
    :return: (bool) True if color is gray else False
    """

    return abs(r-g) <= 10 and abs(g-b) <= 10 and abs(b-r) <= 10


def is_blocks_background_color(r, g, b, area):
    # list of background colors in blocks mode
    blocks_background_colors_hs = [
        [132, 8],
        [128, 5]
    ]

    # color_hsv = bgr_to_hsv_value([b, g, r]).tolist()
    """
    if area > 0.2 or color_hsv[:2] in blocks_background_colors_hs:
        print(r, g, b, area, color_hsv, area > 0.2, blocks_background_colors_hs, True)
        return True
    """

    if area > 0.2 or is_color_gray(r, g, b):
        print(r, g, b, area, 'gray', area > 0.2, True)
        return True

    print(r, g, b, area, 'non-gray', area > 0.2, False)
    return False


def get_word_block_colors(image):
    """
    Return a list of [r, g, b] colors representing word blocks

    :param image: screen image instance
    :return: (list) word block color list
    """

    block_colors = []

    # cut screen into half (horizontal)
    frame = np.array(image)
    frame = frame[int(frame.shape[0] / 2):]

    # convert and reshape image format
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame.reshape((frame.shape[0] * frame.shape[1], 3))

    # Collect 8 major colors in the image using KMeans clustering
    color_cluster = KMeans(n_clusters=8)
    color_cluster.fit(frame)

    # histogram representing area proportion for each color
    hist = find_histogram(color_cluster)

    # filter out persistent colors from game background
    for i, rgb in enumerate(color_cluster.cluster_centers_):
        if not is_blocks_background_color(*rgb, hist[i]):
            block_colors.append(rgb)

    return block_colors


def color_tracked_image(image):
    """
    Return the color tracked version of a given image

    :param image: parent image
    :return:
    """

    # list of [r,b,b] colors representing word blocks
    block_colors = get_word_block_colors(image)

    frame = np.array(image)

    # Convert RGB to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # index of block color to track (random among all 4)
    block_color_index = random.randint(0, 3)
    print(block_colors, len(block_colors), '-' * 10)
    print('-' * 10, block_colors[block_color_index])

    # get approximate hue value for the given color
    block_color_hue = bgr_to_hsv_value(block_colors[block_color_index][::-1])[0]

    # # define range of a color to track using hue value
    lower_color_range = np.array([block_color_hue - 10, 50, 50])
    upper_color_range = np.array([block_color_hue + 10, 255, 255])

    # threshold the HSV image to get only blue colors
    mask_color_range = cv2.inRange(hsv, lower_color_range, upper_color_range)

    # Bitwise-AND mask and original images
    return cv2.bitwise_and(frame, frame, mask=mask_color_range)


def get_maximum_area_contour(image, num):
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

    print('total contours', len(contours))

    cv2.imwrite('gray-{}.png'.format(num), image_gray)

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
    cv2.imwrite('final-{}.png'.format(num), max_area_contour_image_bw_inverted)
    return max_area_contour_image_bw_inverted - cv2.bitwise_not(mask_contour)
