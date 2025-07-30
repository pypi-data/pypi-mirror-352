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
        # Check file size, only smaller than `20M` and large than `5B`
        with open(file_path, "rb") as _:
            content = _.read()
        size_range = 5 < len(content) < 20 * pow(1024, 2)
        if not size_range or kwargs.get("test") == "oversize_file":
            raise ValueError("The file size is out of range: 5B < SIZE < 20M")
        result = MediaUploader(self.key).upload(file_path, **kwargs)
        return (result,), kwargs
