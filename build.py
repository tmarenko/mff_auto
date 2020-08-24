import os
import time
import shutil
import subprocess
import urllib.request
from distutils.dir_util import copy_tree


def cur_dir():
    return os.path.dirname(os.path.abspath(__file__))


FNULL = open(os.devnull, 'w')
SEVEN_ZIP_DOWNLOAD_URL = "https://sourceforge.net/projects/sevenzip/files/7-Zip/9.20/7z920.exe/download"
TESSERACT_OCR_3_05_02_DOWNLOAD_URL = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-setup-3.05.02-20180621.exe"
PORTABLE_PYTHON_3_6_5_DOWNLOAD_URL = "https://sourceforge.net/projects/portable-python/files/Portable Python 3.6.5/Portable Python 3.6.5 Basic.7z/download"
SEVEN_ZIP_FILE_NAME = "7z920.exe"
SEVEN_ZIP_FILE_PATH = os.path.join(cur_dir(), SEVEN_ZIP_FILE_NAME)
SEVEN_ZIP_FOLDER = "7zip"
TESSRACT_OCR_FILE_NAME = "tesseract-ocr-setup-3.05.02-20180621.exe"
TESSRACT_OCR_FILE_PATH = os.path.join(cur_dir(), TESSRACT_OCR_FILE_NAME)
PORTABLE_PYTHON_FILE_NAME = "Portable Python 3.6.5 Basic.7z"
PORTABLE_PYTHON_FILE_PATH = os.path.join(cur_dir(), PORTABLE_PYTHON_FILE_NAME)
PORTABLE_PYTHON_FOLDER = "Python 3.6.5 Portable"
REQUIREMENTS_FILE = os.path.join(cur_dir(), "requirements.txt")
BUILD_FOLDER = os.path.join(cur_dir(), "build")
SEVEN_ZIP_EXE = os.path.join(cur_dir(), SEVEN_ZIP_FOLDER, "7z.exe")
IMAGES_FOLDER = "images"
LIB_FOLDER = "lib"
SETTINGS_FOLDER = "settings"
GUI_FOLDER = "gui"
UI_FOLDER = "ui"
TESSERACT_FOLDER = "tesseract"
LOG_FOLDER = "logs"
EXAMPLE_FILE = "example.py"
APP_FILE = "app.py"
GUI_APP_FILE = "app_gui.py"
GUI_ICON = "icon.ico"
START_BAT_FILE = "start.bat"
README_FILE = "README.md"
LICENSE_FILE = "LICENSE"


def remove_last_build():
    print("Removing last build.")
    if os.path.isdir(BUILD_FOLDER):
        shutil.rmtree(BUILD_FOLDER)
    if os.path.isfile('build.7z'):
        os.remove('build.7z')


def copy_project_files():
    print("Copy project files to build folder.")
    copy_tree(src=LIB_FOLDER, dst=os.path.join(BUILD_FOLDER, LIB_FOLDER))
    copy_tree(src=IMAGES_FOLDER, dst=os.path.join(BUILD_FOLDER, IMAGES_FOLDER))
    copy_tree(src=SETTINGS_FOLDER, dst=os.path.join(BUILD_FOLDER, SETTINGS_FOLDER))
    shutil.copy2(src=EXAMPLE_FILE, dst=os.path.join(BUILD_FOLDER, APP_FILE))
    shutil.copy2(src=GUI_APP_FILE, dst=os.path.join(BUILD_FOLDER, GUI_APP_FILE))
    shutil.copy2(src=GUI_ICON, dst=os.path.join(BUILD_FOLDER, GUI_ICON))
    shutil.copy2(src=README_FILE, dst=os.path.join(BUILD_FOLDER, README_FILE))
    shutil.copy2(src=LICENSE_FILE, dst=os.path.join(BUILD_FOLDER, LICENSE_FILE))
    if os.path.isdir(os.path.join(BUILD_FOLDER, SETTINGS_FOLDER, GUI_FOLDER)):
        shutil.rmtree(os.path.join(BUILD_FOLDER, SETTINGS_FOLDER, GUI_FOLDER))
    os.mkdir(path=os.path.join(BUILD_FOLDER, LOG_FOLDER))
    os.mkdir(path=os.path.join(BUILD_FOLDER, LOG_FOLDER, TESSERACT_FOLDER))
    os.mkdir(path=os.path.join(BUILD_FOLDER, SETTINGS_FOLDER, GUI_FOLDER))


def download_7zip():
    if os.path.isfile(SEVEN_ZIP_FILE_PATH):
        return
    print("Downloading 7zip.")
    with urllib.request.urlopen(SEVEN_ZIP_DOWNLOAD_URL) as url_file:
        with open(SEVEN_ZIP_FILE_NAME, "b+w") as file:
            file.write(url_file.read())


def download_portable_python():
    if os.path.isfile(PORTABLE_PYTHON_FILE_PATH):
        return
    print("Downloading Portable Python.")
    with urllib.request.urlopen(PORTABLE_PYTHON_3_6_5_DOWNLOAD_URL) as url_file:
        with open(PORTABLE_PYTHON_FILE_NAME, "b+w") as file:
            file.write(url_file.read())


def download_tesseract_ocr():
    if os.path.isfile(TESSRACT_OCR_FILE_PATH):
        return
    print("Downloading Tesseract OCR.")
    with urllib.request.urlopen(TESSERACT_OCR_3_05_02_DOWNLOAD_URL) as url_file:
        with open(TESSRACT_OCR_FILE_NAME, "b+w") as file:
            file.write(url_file.read())


def extract_7zip():
    print("Extracting 7zip.")
    output_folder = os.path.join(cur_dir(), SEVEN_ZIP_FOLDER)
    extract_python_cmd = [SEVEN_ZIP_FILE_NAME, "/S", f"/D={output_folder}"]
    subprocess.call(extract_python_cmd, shell=True)


def extract_portable_python():
    print("Extracting Portable Python.")
    extract_python_cmd = [SEVEN_ZIP_EXE, "x", PORTABLE_PYTHON_FILE_PATH, "-aoa", f"-o{BUILD_FOLDER}"]
    subprocess.call(extract_python_cmd, shell=True, stdout=FNULL)
    python_folder = os.path.join(BUILD_FOLDER, PORTABLE_PYTHON_FOLDER)
    copy_tree(src=python_folder, dst=os.path.join(BUILD_FOLDER, "python"))


def extrace_tesseract_ocr():
    print("Extracting Tesseract OCR.")
    tesseract_folder = os.path.join(BUILD_FOLDER, TESSERACT_FOLDER)
    extract_tesseract_cmd = [SEVEN_ZIP_EXE, "x", TESSRACT_OCR_FILE_PATH, "-aoa", f"-o{tesseract_folder}"]
    subprocess.call(extract_tesseract_cmd, shell=True, stdout=FNULL)


def install_requirements():
    print("Installing Python requirements.")
    python_console = os.path.join(BUILD_FOLDER, "python", "App", "Python", "python.exe")
    install_requirements_cmd = [python_console, "-m", "pip", "install", "--no-cache-dir", "-r", REQUIREMENTS_FILE]
    subprocess.call(install_requirements_cmd, shell=True)


def remove_trash():
    print("Removing useless files.")
    to_remove = [
        os.path.join(BUILD_FOLDER, PORTABLE_PYTHON_FOLDER),
        os.path.join(BUILD_FOLDER, "python", "App", "PyScripter"),
        os.path.join(BUILD_FOLDER, "python", "App", "Python", "Lib", "test"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "$PLUGINSDIR"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "$PLUGINSDIR"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "doc"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "java"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "icudata57.dll"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "configs"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "tessconfigs"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.bigrams"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.fold"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.lm"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.nn"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.params"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.size"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.cube.word-freq"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.tesseract_cube.nn"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.user-patterns"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "eng.user-words"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "osd.traineddata"),
        os.path.join(BUILD_FOLDER, TESSERACT_FOLDER, "tessdata", "pdf.ttf")
    ]
    for rem in to_remove:
        if os.path.isdir(rem):
            shutil.rmtree(rem)
        if os.path.isfile(rem):
            os.remove(rem)

    for root, dirs, files in os.walk(os.path.join(BUILD_FOLDER, "python")):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))

    for root, dirs, files in os.walk(os.path.join(BUILD_FOLDER, LIB_FOLDER)):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))

    for root, dirs, files in os.walk(os.path.join(BUILD_FOLDER, TESSERACT_FOLDER)):
        exe_files = [file for file in files if '.exe' in file]
        for exe_file in exe_files:
            os.remove(os.path.join(root, exe_file))


def create_gui_start_file():
    print("Creating start.bat")
    python_cmd = os.path.join("%CD%", "python", "App", "Python", "python.exe")
    with open(os.path.join(BUILD_FOLDER, START_BAT_FILE), "w", encoding='utf-8') as f:
        f.write(f"SET PATH=%CD%\\tesseract\n"
                f"{python_cmd} {GUI_APP_FILE}\n")


def archive_build():
    print("Archiving build folder.")
    archive_build_cmd = [SEVEN_ZIP_EXE, "a", "-t7z", "-m0=lzma", "-mx=9", "-mfb=64", "-md=64m", "-ms=on", "build.7z",
                         f"{BUILD_FOLDER}\\*"]
    subprocess.call(archive_build_cmd, shell=True, stdout=FNULL)


def remove_7zip():
    print("Removing 7zip.")
    seven_zip_folder = os.path.join(cur_dir(), SEVEN_ZIP_FOLDER)
    if os.path.isdir(seven_zip_folder):
        shutil.rmtree(seven_zip_folder)


def build_binaries():
    remove_last_build()
    copy_project_files()
    download_7zip()
    download_portable_python()
    download_tesseract_ocr()
    extract_7zip()
    extract_portable_python()
    extrace_tesseract_ocr()
    install_requirements()
    remove_trash()
    create_gui_start_file()
    archive_build()
    remove_7zip()


if __name__ == '__main__':
    now = time.time()
    build_binaries()
    print(f"Total time: {time.time() - now}")
