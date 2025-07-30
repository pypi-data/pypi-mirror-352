#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown type message sender


- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 15:12
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from enum import Enum
from typing import Union, Callable
from functools import partial

from . import AbstractWeComGroupBot, ConvertedData


class MarkdownWeComGroupBot(AbstractWeComGroupBot):
    """Markdown type message Wecom Group Bot"""

    class _Color(Enum):
        """Markdown color enum"""
        INFO = "green"
        COMMENT = "gray"
        WARNING = "orange"

        @classmethod
        def get_valid_colors(cls):
            """Return list of valid colors"""
            return [_.value for _ in cls]

    @property
    def _doc_key(self) -> str:
        return "markdown类型"

    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify the arguments passed.
        :param args: Positional arguments passed.
        :param kwargs: Keyword arguments passed.
        :return:
        """
        try:
            args[0]
        except IndexError as error:
            raise ValueError("The msg parameter is required.") from error

    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Convert the message to Markdown format data.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Converted data.
        """
        result = ({
            "msgtype": "markdown",
            "markdown": {
                "content": args[0].strip()
            }
        },)
        return result, kwargs

    def color(self, raw: str, color: Union[str, _Color]) -> str:
        """
        Convert normal string to colorful string.
        :param raw: Raw string.
        :param color: Specify color. Support: green | gray | orange
        :return: Colorized string.
        """
        if isinstance(color, str):
            try:
                color = self._Color(color.lower())
            except ValueError as error:
                valid_colors = self._Color.get_valid_colors()
                raise ValueError(
                    f"Invalid color '{color}'. Valid options: {valid_colors}"
                ) from error
        result = f'<font color="{color.name.lower()}">{raw}</font>'
        return result

    @property
    def green(self) -> Callable:
        """
        Return a function that green text
        :return: 
        """
        return partial(self.color, color=self._Color.INFO)

    @property
    def gray(self) -> Callable:
        """
        Return a function that gray text
        :return:
        """
        return partial(self.color, color=self._Color.COMMENT)

    @property
    def orange(self) -> Callable:
        """
        Return a function that orange text
        :return:
        """
        return partial(self.color, color=self._Color.WARNING)
