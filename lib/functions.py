import logging
import random
import time

import cv2
import win32api
from numpy import concatenate, array
from scipy.stats import truncnorm

from lib.structural_similarity.ssim import compare_ssim
from lib.tesseract3 import TesseractPool, AUTOMATIC_PAGE_SEGMENTATION, RAW_LINE_PAGE_SEGMENTATION

logger = logging.getLogger()

# Use default eng data for any letters
tesseract_eng = TesseractPool(language="eng", processes=1)
# Use 'mff.traineddata' language for numbers
tesseract_mff = TesseractPool(language="mff+eng", processes=1)


def get_text_from_image(image, threshold, chars=None, save_file=None, max_height=None):
    """Get text from image using Tesseract OCR.
    https://github.com/tesseract-ocr/

    :param numpy.ndarray image: image.
    :param int threshold: threshold of gray-scale for grabbing image's text.
    :param str chars: available character in image's text.
    :param str save_file: name of file for saving result of gray-scaling.
    :param int max_height: max height of image (in pixels).

    :return: text from image.
    :rtype: str
    """
    image = resize_and_keep_aspect_ratio(image, height=max_height)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold_img = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    if save_file:
        cv2.imwrite(f"logs/tesseract/{save_file}.png", threshold_img)
    psm = RAW_LINE_PAGE_SEGMENTATION if chars else AUTOMATIC_PAGE_SEGMENTATION
    tesseract = tesseract_mff if chars and any(char.isdigit() for char in chars) else tesseract_eng
    return tesseract.image_to_string(threshold_img, whitelist=chars, page_segmentation=psm)


def is_strings_similar(original, compare, overlap=0.25):
    """Check if strings are similar.

    :param str original: original string.
    :param str compare: string to compare.
    :param float overlap: overlap parameter. If string's similarity >= overlap then strings are similar.

    :rtype: bool
    """

    def levenshtein_distance(a, b):
        """Returns the Levenshtein edit distance between two strings."""
        if a == b:
            return 0
        if len(a) < len(b):
            a, b = b, a
        prev_row = range(len(b) + 1)
        for i, column1 in enumerate(a):
            cur_row = [i + 1]
            for j, column2 in enumerate(b):
                insertions = prev_row[j + 1] + 1
                deletions = cur_row[j] + 1
                substitutions = prev_row[j] + (column1 != column2)
                cur_row.append(min(insertions, deletions, substitutions))
            prev_row = cur_row
        return prev_row[-1]

    distance = levenshtein_distance(original.upper(), compare.upper())
    non_similarity = distance / len(original) if len(original) > 0 else 1
    return non_similarity <= overlap


def wait_until(predicate, timeout=3, period=0.25, condition=True, *args, **kwargs):
    """Wait period of time until predicate equals to condition.

    :param function predicate: predicate function to check.
    :param float timeout: how much time wait overall.
    :param float period: how much time wait to check predicate.
    :param bool condition: predicate expected condition.
    :param args: predicate function args.
    :param kwargs: predicate function kwargs.

    :return: was predicate's output equal to condition in given timeout or not.
    :rtype: bool
    """
    time_limit = time.time() + timeout
    while time.time() < time_limit:
        if predicate(*args, **kwargs) == condition:
            return True
        time.sleep(period)
    return False


def get_position_inside_rectangle(rect, mean_mod=2, sigma_mod=5):
    """Gets (x,y) position inside rectangle.
    Using normal distribution position usually will be near rectangle center.

    :param tuple[float, float, float, float] rect: rectangle of screen.
    :param int mean_mod: mean for distribution.
    :param int sigma_mod: standard deviation for distribution.

    :return: (x, y) position inside rectangle.
    :rtype: tuple[float, float]
    """

    def get_truncated_normal(mean=0.0, sd=0.2, low=0.0, up=1.0):
        """Get truncated normal distribution between low and up."""
        return truncnorm((low - mean) / sd, (up - mean) / sd, loc=mean, scale=sd).rvs()

    mean_x = (rect[0] + rect[2]) / mean_mod
    mean_y = (rect[1] + rect[3]) / mean_mod
    sd_x = (rect[2] - rect[0]) / sigma_mod
    sd_y = (rect[3] - rect[1]) / sigma_mod
    normal_x = get_truncated_normal(mean_x, sd_x, rect[0], rect[2])
    normal_y = get_truncated_normal(mean_y, sd_y, rect[1], rect[3])
    return normal_x, normal_y


def r_sleep(seconds, radius_modifier=15.0):
    """Does random sleep with given radius.

    :param float seconds: how much seconds to sleep.
    :param float radius_modifier: radius offset in percentages for randomness.
    """
    offset = float(seconds) / radius_modifier
    time.sleep(random.uniform(seconds - offset, seconds + offset))


def load_image(path):
    """Loads image by given path.

    :param str path: path to image.

    :rtype: numpy.ndarray
    """
    return cv2.imread(path)


def bgr_to_rgb(image_array):
    """Converts RGB image to BGR image. Or backwards, depends on original image's mode.

    :param numpy.ndarray image_array: image.

    :return: converted image.
    :rtype: numpy.ndarray
    """
    return image_array[..., ::-1]


def is_images_similar(image1, image2, overlap=0.6, save_file=None):
    """Checks if images are similar.
    Uses structural similarity.

    :param numpy.ndarray image1: original image.
    :param numpy.ndarray image2: image to check.
    :param float overlap: overlap parameter. If images similarity > overlap then images are similar.
    :param str save_file: name of file for saving result of checking.

    :rtype: bool
    """
    max_x = image1.shape[0] if image1.shape[0] > image2.shape[0] else image2.shape[0]
    max_y = image1.shape[1] if image1.shape[1] > image2.shape[1] else image2.shape[1]
    image1 = colored1 = cv2.resize(image1, (max_y, max_x), interpolation=cv2.INTER_CUBIC)
    image2 = colored2 = cv2.resize(image2, (max_y, max_x), interpolation=cv2.INTER_CUBIC)
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    sim, diff = compare_ssim(image1, image2, full=True)
    if save_file:
        gray_images = cv2.cvtColor(cv2.hconcat([image1, image2]), cv2.COLOR_GRAY2BGR)
        original_images = cv2.hconcat([colored1, colored2])
        cv2.imwrite(f"logs/tesseract/{save_file}.png", concatenate((gray_images, original_images), axis=0))
    return sim > overlap


def is_color_similar(color1, color2, overlap=0.05):
    """Checks if colors are similar.

    :param tuple[int, int, int] color1: original color.
    :param tuple[int, int, int] color2: color to check.
    :param float overlap: overlap parameter. If colors similarity > overlap then colors are similar.

    :rtype: bool
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    d = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** (1 / 2.0)
    return d / 510 <= overlap


def resize_and_keep_aspect_ratio(image, width=None, height=None):
    """Resizes image by width or height and keep original ratio between them.

    :param numpy.ndarray image: numpy.array of image.
    :param int width: width to resize.
    :param int height: height to resize.

    :return: resized image.
    :rtype: numpy.ndarray
    """
    if width and height:
        raise ValueError("Only width or height should be given.")
    if not width and not height:
        return image
    image_height, image_width, _ = image.shape
    new_width, new_height = None, None
    if width:
        new_width = width
        new_height = round(new_width * image_height / image_width)
    if height:
        new_height = height
        new_width = round(new_height * image_width / image_height)
    return cv2.resize(image, dsize=(new_width, new_height), interpolation=cv2.INTER_CUBIC)


def get_file_properties(path_to_file):
    """Reads all properties of the given file by it's path.

    :param str path_to_file: path to file.

    :return: dictionary of properties.
    :rtype: dict
    """
    properties = ('Comments', 'InternalName', 'ProductName', 'CompanyName', 'LegalCopyright', 'ProductVersion',
                  'FileDescription', 'LegalTrademarks', 'PrivateBuild', 'FileVersion', 'OriginalFilename',
                  'SpecialBuild')

    file_props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    fixed_info = win32api.GetFileVersionInfo(path_to_file, '\\')
    file_props['FixedFileInfo'] = fixed_info
    file_props['FileVersion'] = f"{fixed_info['FileVersionMS'] / 65536:.0f}." \
                                f"{fixed_info['FileVersionMS'] % 65536:.0f}." \
                                f"{fixed_info['FileVersionLS'] / 65536:.0f}." \
                                f"{fixed_info['FileVersionLS'] % 65536:.0f}"

    lang, code_page = win32api.GetFileVersionInfo(path_to_file, r'\VarFileInfo\Translation')[0]
    str_info = {}
    for prop_name in properties:
        str_info_path = f'\\StringFileInfo\\{lang:04x}{code_page:04x}\\{prop_name}'
        str_info[prop_name] = win32api.GetFileVersionInfo(path_to_file, str_info_path)

    file_props['StringFileInfo'] = str_info

    return file_props


def convert_colors_in_image(image, colors, color_to_convert=(255, 255, 255), blur_result=(2, 2)):
    """Converts given colors in image to one color.

    :param numpy.ndarray image: image.
    :param list[tuple[tuple[int, int, int], tuple[int, int, int]] colors: list of colors to convert;
        each color represents tuple of low and high values for color.
    :param tuple[int, int, int] color_to_convert: color to convert.
    :param tuple[int, int] blur_result: tuple of blur size if you want to blur the result image.

    :return: image with converted colors.
    :rtype: numpy.ndarray
    """
    for color_low, color_high in colors:
        if isinstance(color_low, (set, list)):
            color_low = array(color_low)
        if isinstance(color_high, (set, list)):
            color_high = array(color_high)
        mask = cv2.inRange(image, color_low, color_high)
        image[mask > 0] = color_to_convert
    if blur_result:
        image = cv2.blur(image, blur_result)
    return image


def confirm_condition_by_time(confirm_condition, confirm_timeout=3, confirm_period=0.5):
    """Confirms that given condition is always True for given amount of time.

    :param function confirm_condition: function to confirm.
    :param float confirm_timeout: timeout for confirm.
    :param float confirm_period: how much time wait to check condition.

    :return: was condition always True for given timeout or not.
    :rtype: bool
    """
    results = []
    for _ in range(int(confirm_timeout / confirm_period)):
        results.append(confirm_condition())
        r_sleep(confirm_period)
    return all(results)
