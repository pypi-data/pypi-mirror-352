#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/30 14:40
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from . import AbstractWeComGroupBot, ConvertedData, MediaUploader
from ..deco import verify_file


class FileWeComGroupBot(AbstractWeComGroupBot):
    """File type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "文件类型"

    @verify_file
    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify the arguments passed.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return:
        """

    # pylint:disable=unused-argument
    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Convert the message to File format.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        file_path = kwargs["file_path"]
        result = MediaUploader(self.key).upload(file_path, **kwargs)
        return (result,), kwargs
