#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decorators module

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/29 14:48
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from functools import wraps
from logging import getLogger
from pathlib import Path
from time import sleep

from requests import RequestException

logger = getLogger(__name__)


def verify_and_convert_arguments(function):
    """
    Verify and convert the arguments to standard format.
    :param function: Callable object.
    :return: Result dict.
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs) -> dict:
        logger.debug("---- %s ----", verify_and_convert_arguments.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        try:
            self.verify_arguments(*args, **kwargs)
        except ValueError as error:
            logger.critical("Verification of arguments failed: %s", error)
            raise error
        try:
            args, kwargs = self.convert_arguments(*args, **kwargs)
        except ValueError as error:
            logger.critical("Convertion of arguments failed: %s", error)
            raise error
        logger.debug("Converted arguments: %s", args)
        logger.debug("Converted other kwargs: %s", kwargs)
        logger.debug("---- %s ----", verify_and_convert_arguments.__name__)
        return function(self, *args, **kwargs)

    return wrapper


def detect_overheat(function):
    """
    Detect overheat.
    :param function: Callable object.
    :return: Result dict.
    """
    overheat_threshold: int = 60
    overheat_error_code: int = 45009

    @wraps(function)
    def wrapper(self, *args, **kwargs) -> dict:
        """
        Detect overheat.
        :param self: Object instance.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result dict.
        """
        logger.debug("==== %s ====", detect_overheat.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        if kwargs.get("test") == "overheat":
            kwargs.pop("test")
            threshold = 0
            result = {"errcode": overheat_error_code}
        else:
            threshold = overheat_threshold
            if self.OVERHEAT >= 0:
                logger.warning("Overheat detected.")
                while self.OVERHEAT >= 0:
                    print(f"\rCooling down: {self.OVERHEAT:02d}s",
                          end='',
                          flush=True)
                    sleep(1)
                    self.OVERHEAT -= 1
                print()
            result = function(self, *args, **kwargs)
        if result.get("errcode") == overheat_error_code:
            self.OVERHEAT = threshold
            result = wrapper(self, *args, **kwargs)
        logger.debug("==== %s ====", detect_overheat.__name__)
        return result

    return wrapper


def handle_request_exception(function):
    """
    Handle request exception.
    :param function: Callable object.
    :return:
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        """
        Handle request exception.
        :param self: Object instance.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result dict.
        """
        logger.debug("#### %s ####", handle_request_exception.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        try:
            if (test := kwargs.get("test")) == "request_error":
                raise RequestException
            if test == "api_error":
                result = {"errcode": -1}
            else:
                result = function(self, *args, **kwargs)
            if result.get("errcode") != 0:
                msg = f"Request failed, please refer to the official manual: {self.doc}"
                logger.error(msg)
                logger.error("Error message: %s", result)
                raise IOError(msg)
        except RequestException as error:
            msg = f"Unable to initiate API request correctly: {error}"
            logger.error(msg)
            raise ConnectionRefusedError(msg) from error
        logger.debug("#### %s ####", handle_request_exception.__name__)
        return result

    return wrapper


def verify_file(function):
    """
    Verify file, include: amr / png / jpg or other type files.
    :param function: Callable function.
    :return:
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        logger.debug("$$$$ %s $$$$", verify_file.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        file_path = kwargs.get("file_path")
        try:
            file_path = file_path if file_path else args[0]
        except IndexError as error:
            raise ValueError("The file_path parameter is required.") from error
        if not Path(file_path).exists():
            raise ValueError("The file_path parameter not exists.")
        logger.debug("$$$$ %s $$$$", verify_file.__name__)
        return function(self, *args, **kwargs)

    return wrapper
