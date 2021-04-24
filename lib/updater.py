﻿import os
import shutil
import lib.logger as logging
import zipfile
import importlib
import importlib.util
import urllib.request as request
import urllib.error as urlib_error
import version as current_version_module
from distutils.version import StrictVersion
from distutils.dir_util import copy_tree

logger = logging.get_logger(__name__)


class Version:
    """Class for working with project versions."""

    @staticmethod
    def version_to_str(self):
        """Override __str__ function of StrictVersion to always return full version string."""
        vstring = '.'.join(map(str, self.version))
        if self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])
        return vstring

    def __init__(self, version_module):
        """Class initialization.

        :param version_module: module of version.py
        """
        StrictVersion.__str__ = self.version_to_str
        self.mff_auto = StrictVersion(version_module.mff_auto)
        self.mff = StrictVersion(version_module.mff)
        self.updater = StrictVersion(version_module.updater)


class Updater:
    """Class for working with project updates."""

    NEW_VERSION_FILE = "new_version.py"
    GITHUB_VERSION_LINK = "https://raw.githubusercontent.com/tmarenko/mff_auto/master/version.py"
    GITHUB_SOURCE_CODE_URL = "https://github.com/tmarenko/mff_auto/archive/{version}.zip"
    DOWNLOAD_COUNTER_LINK = "https://api.countapi.xyz/hit/mff_auto/{version}"
    SOURCE_CODE_FOLDER_NAME = "mff_auto-{version}"

    def __init__(self):
        """Class initialization."""
        self.source_code_archive = None
        self.source_folder = None
        self.new_version_file = None
        self.new_version = None
        self.current_version_module = current_version_module
        self.current_version = Version(version_module=self.current_version_module)
        self.is_new_updater = False
        logger.info(f"Loaded version: mff_auto={self.current_version.mff_auto}, game={self.current_version.mff}, "
                    f"updater={self.current_version.updater}")

    @staticmethod
    def import_version_file(version_file_path):
        """Import version file as module.

        :param version_file_path: path to version file.

        :return: imported module.
        """
        spec = importlib.util.spec_from_file_location("version", version_file_path)
        version_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version_module)
        return version_module

    def download_version_file(self):
        """Download version file from GitHub sources."""
        with open(self.NEW_VERSION_FILE, "wb") as file:
            req = request.Request(self.GITHUB_VERSION_LINK)
            req.add_header('Cache-Control', 'max-age=0')
            with request.urlopen(req) as url_file:
                content = url_file.read()
                file.write(content)
                return file.name

    def check_updates(self):
        """Check updates in GitHub.

        :return: True or False: was new version found or not.
        """
        self.new_version_file = self.download_version_file()
        new_version_module = self.import_version_file(version_file_path=self.new_version_file)
        self.new_version = Version(version_module=new_version_module)
        if self.new_version.updater > self.current_version.updater:
            logger.info(f"Found new version of Updater {self.new_version.updater}, cannot update. "
                        f"Download last release from project homepage.")
            self.is_new_updater = True
            return False
        if self.new_version.mff_auto > self.current_version.mff_auto:
            logger.info(f"Found new version {self.new_version.mff_auto} for MFF {self.new_version.mff}.")
            return True
        else:
            logger.info(f"Current version {self.new_version.mff_auto} is up to date for MFF {self.new_version.mff}.")
            return False

    def update_from_new_version(self):
        """Update project files from new version."""
        self.update_download_counter(version=self.new_version.mff_auto)
        self.source_code_archive = self.download_source_code(version=self.new_version.mff_auto)
        logger.info(f"Extracting zip-archive with {self.new_version.mff_auto} version.")
        with zipfile.ZipFile(self.source_code_archive, 'r') as zip_ref:
            zip_ref.extractall()
        self.source_folder = self.SOURCE_CODE_FOLDER_NAME.format(version=self.new_version.mff_auto)
        # Remove old libs and images to prevent intersection with new files
        if os.path.isdir("lib"):
            shutil.rmtree("lib")
        if os.path.isdir("images"):
            shutil.rmtree("images")
        logger.info("Updating files...")
        self.copy_project_files()
        self.clean()

    def update_download_counter(self, version):
        """Update download's counter."""
        try:
            download_counter_url = self.DOWNLOAD_COUNTER_LINK.format(version=version)
            req = request.Request(download_counter_url, headers={'User-Agent': 'Mozilla/5.0'})
            request.urlopen(req)
        except urlib_error.HTTPError as err:
            logger.error(f"Got error while updating download's counter: {err}")

    def download_source_code(self, version):
        """Download source code from GitHub by version tag."""
        download_url = self.GITHUB_SOURCE_CODE_URL.format(version=version)
        logger.info(f"Downloading new version from URL: {download_url}")
        with open(f"{version}.zip", "wb") as file:
            with request.urlopen(download_url) as url_file:
                content = url_file.read()
                file.write(content)
                return file.name

    def copy_project_files(self):
        """Copy project files from source codes."""
        copy_tree(src=os.path.join(self.source_folder, "lib"), dst="lib")
        copy_tree(src=os.path.join(self.source_folder, "images"), dst="images")
        copy_tree(src=os.path.join(self.source_folder, "settings"), dst="settings")
        copy_tree(src=os.path.join(self.source_folder, "tessdata"), dst=os.path.join("tesseract", "tessdata"))
        shutil.copy2(src=os.path.join(self.source_folder, "app_gui.py"), dst="app_gui.py")
        shutil.copy2(src=os.path.join(self.source_folder, "version.py"), dst="version.py")
        shutil.copy2(src=os.path.join(self.source_folder, "icon.ico"), dst="icon.ico")
        shutil.copy2(src=os.path.join(self.source_folder, "LICENSE"), dst="LICENSE")
        shutil.copy2(src=os.path.join(self.source_folder, "README.md"), dst="README.md")

    def clean(self):
        """Clean all files after updating."""
        if self.new_version_file:
            os.remove(self.new_version_file)
        if self.source_code_archive:
            os.remove(self.source_code_archive)
        if self.source_folder:
            shutil.rmtree(self.source_folder)
