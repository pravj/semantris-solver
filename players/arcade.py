import os
import cv2
import numpy as np
import pytesseract

# relative path to the 'arcade' triangle template image
current_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(
    current_path, '../assets/arcade_template.png'
)

# load template image to reuse while searching
template_img = cv2.imread(template_path, 0)
w, h = template_img.shape[::-1]


def get_selected_words(screen):
    """
    Return a list of words highlighted on the screen
    based on the light blue theme color of the game

    Reference docs:
    https://docs.opencv.org/3.3.0/d4/dc6/tutorial_py_template_matching.html

    :param screen: screen image instance returned by pyautogui
    :return: (list) highlighted words on the screen
    """
    selected_words = []

    # convert RGB screen image to BGR
    screen_img_rgb = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    # converting the screen to grayscale with a threshold for blue channel
    screen_img_gray = screen_img_rgb[:, :, 0]
    screen_img_gray = (screen_img_gray > 200) * screen_img_gray

    # apply opencv template matching
    res_img = cv2.matchTemplate(
        screen_img_gray, template_img, cv2.TM_CCOEFF_NORMED
    )

    # find the screen image section where the template is matching
    # with the given threshold range
    threshold = 0.75
    loc = np.where(res_img >= threshold)
    for pt in zip(*loc[::-1]):
        # crop rectangle section around the selected template
        # a rectangle right next to the template
        cropped_image = screen_img_gray[pt[1]:pt[1] + h + 5, pt[0] + w:pt[0] + w + 205]

        # append the image text to selected word list using tesseract
        selected_words.append(pytesseract.image_to_string(cropped_image))

    return selected_words
