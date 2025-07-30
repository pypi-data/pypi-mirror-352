#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown type message sender


- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 15:12
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from . import AbstractWeComGroupBot, ConvertedData


class MarkdownWeComGroupBot(AbstractWeComGroupBot):
    """Markdown type message Wecom Group Bot"""

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
