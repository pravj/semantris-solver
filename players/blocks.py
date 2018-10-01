from utils import utils


def get_selected_words(screen):
    """
    Return a list of words having maximum possible score
    for a given screen.

    A word has maximum possible score when entering its
    associated word will get relatively more points.
    OR
    when the word block is attached to maximum similar
    color blocks.

    Reference docs:
    https://github.com/pravj/semantris-solver/blob/notebooks/Semantris%20Block%20Mode.ipynb

    :param screen: screen image instance returned by pyautogui
    :return: (list) highlighted words on the screen
    """

    color_tracked_screen = utils.color_tracked_image(screen, [230, 170, 70])
    max_area_contour_image = utils.get_maximum_area_contour(
        color_tracked_screen
    )

    return [utils.get_image_string(max_area_contour_image)]
