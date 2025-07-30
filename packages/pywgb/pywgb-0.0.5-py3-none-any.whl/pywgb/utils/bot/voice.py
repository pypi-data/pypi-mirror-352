#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/30 16:49
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from pathlib import Path

from . import AbstractWeComGroupBot, ConvertedData, MediaUploader
from ..deco import verify_file


class VoiceWeComGroupBot(AbstractWeComGroupBot):
    """Voice type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "语音类型"

    @verify_file
    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify the arguments passed.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return:
        """
        file_path = Path(kwargs["file_path"])
        test = kwargs.get("test")
        # Check format, only support: `.amr`
        if file_path.suffix.lower() != ".amr" or test == "wrong_format_voice":
            raise ValueError("Just support voice type: amr")

    # pylint:disable=unused-argument
    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Convert the message to Voice format.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        file_path = kwargs["file_path"]
        result = MediaUploader(self.key).upload(file_path, **kwargs)
        return (result,), kwargs
