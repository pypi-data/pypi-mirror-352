#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/29 14:05
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from base64 import b64encode
from hashlib import md5
from pathlib import Path

from . import AbstractWeComGroupBot, ConvertedData
from ..deco import verify_file


class ImageWeComGroupBot(AbstractWeComGroupBot):
    """Image type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "图片类型"

    @verify_file
    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify the arguments passed.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return:
        :raise ValueError: Verify error.
        """
        suffix = Path(kwargs["file_path"]).suffix.lower()
        test = kwargs.get("test")
        # Check format, only support: `.jpg` and `.png`
        if suffix not in [".jpg", ".png"] or test == "wrong_format_image":
            raise ValueError("Just support image type: jpg or png")

    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Convert the message to Image format.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        file_path = Path(kwargs["file_path"])
        # Check image size, only smaller than `2M`
        max_size = 2 * pow(1024, 2)
        with open(file_path, "rb") as _:
            content = _.read()
        if len(content) > max_size or kwargs.get("test") == "oversize_image":
            raise ValueError("The image is too large, more than 2M")
        result = ({
            "msgtype": "image",
            "image": {
                "base64": b64encode(content).decode("utf-8"),
                "md5": md5(content).hexdigest(),
            }
        },)
        return result, kwargs
