"""

AOPM (Axok!_OS Package Manager) API
------------------------------------
Description: Used to make simple checks and display infos about AOPM.
Made by: GusDev
Version: 1.0.0

"""

# imports
import sys
from typing import NoReturn
from venv import logger

import gnupg
from pathlib import Path as p
from datetime import datetime

"""
#################
## PRINT INFOS ##
#################
"""

def info(msg: str, logger: Logger | None = None) -> None:
    """
    Display an info message.
    :param msg: The message to be displayed in console.
    :return: None
    """
    print(f"=> [\033[34mINFO\033[0m]: {msg}")
    if logger:
        logger.write(msg, "INFO")


def success(msg: str, logger: Logger | None = None) -> None:
    """
    Display a success message.
    :param msg: The message to be displayed in console.
    :return: None
    """
    print(f"==> [\033[32mSUCCESS\033[0m]: {msg}")
    if logger:
        logger.write(msg, "SUCCESS")



def target(msg: str, logger: Logger | None = None) -> None:
    """
    Display a target message.
    :param msg: The message to be displayed in console.
    :return: None
    """
    print(f"==> [\033[36mTARGET\033[0m]: {msg}")
    if logger:
        logger.write(msg, "TARGET")


def warn(msg: str, logger: Logger | None = None) -> None:
    """
    Display a warn message.
    :param msg: The message to be displayed in console.
    :return: None
    """
    print(f"=> [\033[33mWARNING\033[0m]: {msg}")
    if logger:
        logger.write(msg, "WARNING")



def error(msg: str, logger: Logger | None = None, exit: bool = True, exit_code: int = 1, sad_face: bool = False) -> None | NoReturn:
    """
    Display an error message.
    :param msg: The message to be displayed in console.
    :param exit: If ``True``, exit the program
    :param exit_code: if exit parameter is ``True``, exit the program with the specified exit code.
    :param sad_face: If ``True``, add a sad face at the end of the message
    :return: None | NoReturn
    """
    print(f"=> [\033[31mERROR\033[0m]: {msg}{":(" if sad_face else ""}")
    if logger:
        logger.write(msg, "ERROR")

    if exit:
       sys.exit(exit_code)


"""
 ###########
## LOGGER ##
###########
"""


class Logger:
    """
    Class used to manage logs for AOPM.
    """
    def __init__(self, log_path: str = f"/var/log/aopm.log", auto_init=True):
        """
        Open the logs file and prepare the logger.
        :param log_path: - If you don't change it will be written in ``/var/log/aopm.log``
        :param auto_init: - If ``True`` init a new logger session.
        """
        self.log_path = log_path
        self.datePreffix = "%Y-%m-%d"
        self.hourPreffix = "%H:%M:%S"
        self.log = open(self.log_path, "a")
        if auto_init:
            self.initLogger()

    def write(self, msg: str, log_type="INFO", end="\n", with_log_infos = True):
        """
        Write to the logger file.
        :param msg: - The message to be written
        :param log_type: - The log message type, use ``None`` if you don't want log type
        :param end: - If you don't change it will be "\n"
        :param with_log_infos: - If ``False`` will not be written the log type and the hour
        :return:
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if with_log_infos:
            if log_type == None:
                self.log.write(f"[{now}] {msg}{end}")
            else:
                self.log.write(f"[{now}] [{log_type}]: {msg}{end}")
        else:
            self.log.write(f"{msg}{end}")

    def initLogger(self):
        """
        Init the logger creating a new session
        :return:
        """
        self.write("", with_log_infos=False)
        self.write("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=", with_log_infos=False)
        self.write("AOPM LOGGER SESSION STARTED!", with_log_infos=False)
        self.write("----------------------------------------", with_log_infos=False)
        self.write("|  DATE  |  HOUR  |  TYPE  |  MESSAGE  |", with_log_infos=False)
        self.write("----------------------------------------", with_log_infos=False)
        self.write("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=", with_log_infos=False)
        self.write("AOPM logger session initialized!", None, with_log_infos=False)

    def closeLogger(self):
        """
        Close the logger file.
        :return:
        """
        self.log.close()



"""
 ################
## GPG CHECKER ##
################
"""


class GPGChecker:
	"""
    Class used to check GPG keys, can be used to check packages signatures or modules signatures.
    We recommend to use it as a temporary checker, so import your keys every time.
    """

	def __init__(self, home: str = "/tmp/.aopm-gpg"):
		"""
        Prepare the GPG checker
        :param home: The home directory for the GPG checker
        """
		self.home = home
		self.gpg = gnupg.GPG(gnupghome=self.home)

	def import_key(self, key: str, file: bool = False) -> bool:
		"""
        Import a GPG key, can be the path or the content
        :param key: The path or the content of the GPG key
        :param file: If ``True``, will open the file specified with the key parameter
        :return: None
        """
		if not p(file).is_file():
			return False

		if not file:
			keyData = key
		else:
			with open(key, "r", encoding="utf-8") as f:
				keyData = f.read()

		result = self.gpg.import_keys(keyData)
		return result.count > 0

	def verify_file(self, file_path: str, sig: str):
		if not p(file_path).is_file() or not p(sig).is_file():
			return False

		with open(sig, "rb") as f:
			verify = self.gpg.verify_file(f, data_filename=file_path)

		return verify


"""
 #########################
## API MANIFEST CHECKER ##
##########################
"""


class ApiChecker:
	def __init__(self, manifest: dict):
		self.header = manifest

	def check_manifest(self):
		header = self.manifest
		essentialKeys = ["name", "version", "author", "author_email", "api_version"]
		for key in essentialKeys:
			if key in header:
				continue
			else:
				error(
					f"The API header dont have the: '{key}' :( If you are creating a custom module, add the key to your manifest :)",
					True, 1)
