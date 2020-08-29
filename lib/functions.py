import cv2
from scipy.stats import truncnorm
import random
import time
from PIL import Image
from numpy import array, concatenate
from lib.structural_similarity.ssim import compare_ssim
from lib.tesseract3 import TesseractPool

tesseract = TesseractPool()


def get_text_from_image(image, threshold, chars=None, save_file=None, max_height=None):
    """Get text from image using Tesseract OCR.
    https://github.com/tesseract-ocr/

    :param image: numpy.array of image.
    :param threshold: threshold of gray-scale for grabbing image's text.
    :param chars: available character in image's text.
    :param save_file: name of file for saving result of gray-scaling.
    :param max_height: max height of image (in pixels).

    :return: text from image.
    """
    image = resize_and_keep_aspect_ratio(image, height=max_height)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold_img = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    if save_file:
        cv2.imwrite(f"logs/tesseract/{save_file}.png", threshold_img)
    psm = 13 if chars else 3
    text = tesseract.image_to_string(threshold_img, whitelist=chars, page_segmentation=psm)
    return text


def is_strings_similar(original, compare, overlap=0.25):
    """Check if strings are similar.

    :param original: original string.
    :param compare: string to compare.
    :param overlap: overlap parameter. If string's similarity >= overlap then strings are similar.

    :return: True or False.
    """
    def levenshtein_distance(a, b):
        """Return the Levenshtein edit distance between two strings."""
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


def wait_until(predicate, timeout, period=0.25, condition=True, *args, **kwargs):
    """Wait period of time until predicate is True.

    :param predicate: predicate function to check.
    :param timeout: how much time wait overall.
    :param period: how much time wait to check predicate.
    :param condition: predicate expected condition.
    :param args: predicate function args.
    :param kwargs: predicate function kwargs.

    :return: True or False of predicate function.
    """
    time_limit = time.time() + timeout
    while time.time() < time_limit:
        if predicate(*args, **kwargs) == condition:
            return True
        time.sleep(period)
    return False


def get_position_inside_rectangle(rect, mean_mod=2, sigma_mod=5):
    """Get (x,y) position inside rectangle.
    Using normal distribution position usually will be near rectangle center.

    :param rect: rectangle of screen.
    :param mean_mod: mean for distribution.
    :param sigma_mod: standard deviation for distribution.

    :return: (x, y) position inside rectangle.
    """
    def get_truncated_normal(mean=0, sd=0.2, low=0, up=1):
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
    """Random sleep with radius.

    :param seconds: how much seconds to sleep.
    :param radius_modifier: random radius offset.
    """
    offset = float(seconds) / radius_modifier
    time.sleep(random.uniform(seconds - offset, seconds + offset))


def load_image(path):
    """Load image by path.

    :param path: path to image.
    :return: numpy.array of image.
    """
    image = Image.open(path)
    bands = image.getbands()
    if len(bands) == 3:
        b, g, r = image.split()
    else:
        b, g, r, a = image.split()
    image = Image.merge("RGB", (r, g, b))
    return array(image)


def is_images_similar(image1, image2, overlap=0.6, save_file=None):
    """Check if images are similar.
    Using structural similarity.

    :param image1: original image.
    :param image2: image to check.
    :param overlap: overlap parameter. If images similarity > overlap then images are similar.
    :param save_file: name of file for saving result of checking.

    :return: True or False.
    """
    max_x = image1.shape[0] if image1.shape[0] > image2.shape[0] else image2.shape[0]
    max_y = image1.shape[1] if image1.shape[1] > image2.shape[1] else image2.shape[1]
    image1 = cv2.resize(image1, (max_y, max_x), interpolation=cv2.INTER_CUBIC)
    image2 = cv2.resize(image2, (max_y, max_x), interpolation=cv2.INTER_CUBIC)
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    sim, diff = compare_ssim(image1, image2, full=True)
    if save_file:
        cv2.imwrite(f"logs/tesseract/{save_file}.png", concatenate((image1, image2), axis=1))
    return sim > overlap


def is_color_similar(color1, color2, overlap=0.05):
    """Check if colors are similar.

    :param color1: original color.
    :param color2: color to check.
    :param overlap: overlap parameter. If colors similarity > overlap then colors are similar.

    :return: True or False.
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    d = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** (1 / 2.0)
    return d / 510 <= overlap


def resize_and_keep_aspect_ratio(image, width=None, height=None):
    """Resize image by width or height and keep original ratio between them.

    :param image: numpy.array of image.
    :param width: width to resize.
    :param height: height to resize.

    :return: numpy.array of resized image.
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
