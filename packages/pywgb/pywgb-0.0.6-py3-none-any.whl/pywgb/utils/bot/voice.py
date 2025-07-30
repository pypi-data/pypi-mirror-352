#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/30 16:49
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from pathlib import Path
from logging import getLogger

from . import AbstractWeComGroupBot, ConvertedData, MediaUploader
from ..deco import verify_file

logger = getLogger(__name__)


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
        # Check voice size, only smaller than `2M` and large than `5B`
        with open(file_path, "rb") as _:
            content = _.read()
        size_range = 5 < len(content) < 2 * pow(1024, 2)
        test = kwargs.get("test")
        if not size_range or test == "oversize_voice":
            raise ValueError("The voice size is out of range: 5B < SIZE < 2M")
        # Check voice duration, only less than `60s`
        try:
            # pylint: disable=import-outside-toplevel
            from pydub import AudioSegment
            audio = AudioSegment.from_file(file_path, format="amr")
            if len(audio) / 1000 > 60 or test == "overlong_voice":
                raise ValueError("The voice duration is longer than 60s")
        except ImportError:  # pragma: no cover
            logger.warning("Full feature requires `pydub` to be installed.")
            logger.warning(
                'Re-install this package using `pip install "pywgb[all]"` will fix this warning.'
            )
        result = MediaUploader(self.key).upload(file_path, **kwargs)
        return (result,), kwargs
