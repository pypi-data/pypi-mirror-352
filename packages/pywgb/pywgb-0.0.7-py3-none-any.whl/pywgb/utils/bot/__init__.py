#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract classes

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 13:54
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
__all__ = ["AbstractWeComGroupBot", "FilePathLike", "MediaUploader"]

from abc import ABC, abstractmethod
from logging import getLogger
from os import PathLike
from pathlib import Path
from typing import Tuple, Dict, Union, List
from urllib.parse import quote, urlparse, parse_qs, urljoin
from uuid import UUID
from functools import partial

from requests import Session, session

from ..deco import verify_and_convert_arguments, verify_file
from ..deco import detect_overheat, handle_request_exception

logger = getLogger(__name__)
FilePathLike = Union[str, PathLike]
ConvertedData = Tuple[Tuple[Dict[str, str]], Dict[str, str]]


class _BotBasic(ABC):
    """Private bot basic class"""

    # The base path of the document
    _DOC_URL: str = "https://developer.work.weixin.qq.com/document/path/99110"
    # API Endpoint base url
    _API_END_POINT: str = 'https://qyapi.weixin.qq.com'

    def __init__(self, key: str) -> None:
        """
        Initialize the class.
        :param key: The key of group bot webhook url.
        """
        if key is None:
            raise ValueError("Key is required")
        self.key = self._verify_uuid(key.strip())
        self.session: Session = session()

    @staticmethod
    def _parse_webhook_url(url: str) -> str:
        """
        Parse webhook url into key string.
        :param url: Webhook url.
        :return: Key string.
        """
        # If the key passed by url, split and parse it.
        try:
            query = urlparse(url).query
            params = parse_qs(query)
            if "key" not in params or not params["key"]:
                raise ValueError("Missing 'key' parameter in URL")
            return params["key"][0]
        except Exception as error:
            msg = f"Invalid webhook URL {url}."
            logger.critical(msg)
            raise ValueError(msg) from error

    def _verify_uuid(self, key: Union[str, UUID], max_attempts: int = 2) -> str:
        """
        Verify the key weather is UUID format.
        :param key: Key string
        :param max_attempts: Max number of attempts.
        :return: Result bool
        """
        if max_attempts <= 0:  # pragma: no cover
            raise ValueError("Maximum verification attempts exceeded")
        # The standard key format is UUID format.
        if isinstance(key, UUID):  # pragma: no cover
            return str(key)
        try:
            UUID(key)
            return key
        except (ValueError, TypeError, AttributeError) as error:
            try:
                key = self._parse_webhook_url(key)
                return self._verify_uuid(key, max_attempts - 1)
            except ValueError:
                ...
            raise ValueError(f"Invalid key format: {key}") from error

    def __repr__(self) -> str:
        """
        Return the class name.
        :return: Class name.
        """
        return f"{self.__class__.__name__}({self.key})"

    @property
    def api_end_point(self) -> str:
        """
        Returns the address of the spliced endpoint url.
        :return: Endpoint url
        """
        end_point = urljoin(self._API_END_POINT, self._api_end_point_path)
        return end_point

    @property
    @abstractmethod
    def _api_end_point_path(self) -> str:
        """
        The path of the API Endpoint.
        :return: path of the API Endpoint.
        """

    @property
    @abstractmethod
    def _doc_key(self) -> str:
        """
        The key of the document description.
        :return: key of the document description
        """

    @property
    def doc(self) -> str:
        """
        API URL of the document description
        :return: URL of the document
        """
        url = f"{self._DOC_URL}#{quote(self._doc_key)}"
        return url


class AbstractWeComGroupBot(_BotBasic, ABC):
    """Abstract class of Wecom group bot."""

    # Default requests headers
    _HEADERS: dict = {"Content-Type": "application/json"}
    # Class level variable for detect overheat
    OVERHEAT: int = -1

    def __init__(self, key: str) -> None:
        _BotBasic.__init__(self, key)
        ABC.__init__(self)
        self.session.headers = self._HEADERS

    @property
    def _api_end_point_path(self) -> str:
        """
        The path of the API Endpoint.
        :return: path of the API Endpoint.
        """
        return "cgi-bin/webhook/send"

    @property
    @abstractmethod
    def _doc_key(self) -> str:
        """
        The key of the document description.
        :return: key of the document description
        """

    # pylint:disable=unused-argument
    @handle_request_exception
    @detect_overheat
    @verify_and_convert_arguments
    def send(self,
             msg: str = None,
             /,
             articles: List[Dict[str, str]] = None,
             file_path: FilePathLike = None,
             **kwargs) -> dict:
        """
        Method of sending a message. `Refer`_

        .. _`Refer`: https://developer.work.weixin.qq.com/document/path/91770

        :param msg: Message body.
        :param articles: List of articles. Used for send news.
        :param file_path: File path. Used for send image/voice/file.
        :return: Result dict.
        """
        logger.debug("~~~~ %s ~~~~", self.send.__name__)
        logger.debug("Message: %s", msg)
        logger.debug("Articles: %s", articles)
        logger.debug("File path: %s", file_path)
        logger.debug("Other kwargs: %s", kwargs)
        logger.debug("API endpoint URL: %s", self.api_end_point)
        response = self.session.post(self.api_end_point,
                                     params={"key": self.key},
                                     json=msg)
        result = response.json()
        logger.debug("~~~~ %s ~~~~", self.send.__name__)
        logger.info("Message has been sent: %s", result)
        return result

    @abstractmethod
    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify arguments methods. Subclasses must complete specific implementations
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: None
        """

    @abstractmethod
    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Prepare data methods, subclasses must complete specific implementations
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Result dict.
        """


class MediaUploader(_BotBasic):
    """Upload voice and file class"""

    @property
    def _api_end_point_path(self) -> str:
        """
        The path of the API Endpoint.
        :return: path of the API Endpoint.
        """
        return "cgi-bin/webhook/upload_media"

    @property
    def _doc_key(self) -> str:
        """
        The key of the document description.
        :return: key of the document description
        """
        return "文件上传接口"

    @handle_request_exception
    def _upload_temporary_file(self, file_path: Path, file_type: str) -> dict:
        """
        Upload temporary file from file path.
        :param file_path: File path.
        :param file_type: File type.
        :return:
        """
        kwargs = {
            "url": self.api_end_point,
            "params": {
                "key": self.key,
                "type": file_type
            }
        }
        cmd = partial(self.session.post, **kwargs)
        with open(file_path, "rb") as files:
            response = cmd(files={"media": files})
        result = response.json()
        return result

    @verify_file
    def upload(self, file_path: FilePathLike, /, **kwargs) -> dict:
        """
        Upload voice and file.
        :param file_path: The path of the file.
        :param kwargs: Other keyword arguments.
        :return: Result dict.
        """
        file_path: Path = Path(file_path)
        # Only support `AMR` format for voice, others must be file type
        file_type: str = "voice" if file_path.suffix == ".amr" else "file"
        logger.debug("~~~~ %s ~~~~", self.upload.__name__)
        logger.debug("File path: %s", file_path)
        logger.debug("Other kwargs: %s", kwargs)
        logger.debug("API endpoint URL: %s", self.api_end_point)
        result = self._upload_temporary_file(file_path, file_type)
        logger.debug("~~~~ %s ~~~~", self.upload.__name__)
        logger.info("%s has been uploaded: %s", file_type.capitalize(), result)
        result = {
            "msgtype": file_type,
            file_type: {
                "media_id": result["media_id"]
            }
        }
        return result
