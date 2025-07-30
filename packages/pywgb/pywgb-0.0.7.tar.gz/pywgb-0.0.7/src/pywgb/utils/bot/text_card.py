#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Card type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/6/4 10:09
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from functools import partial
from typing import List

from jmespath import search

from . import AbstractWeComGroupBot, ConvertedData


class TextCardWeComGroupBot(AbstractWeComGroupBot):
    """Text Card type message Wecom Group Bot"""

    _VALID_KEYS: List[str] = [
        "source",
        "main_title",
        "emphasis_content",
        "quote_area",
        "sub_title_text",
        "horizontal_content_list",
        "jump_list",
        "card_action",
    ]

    @property
    def _doc_key(self) -> str:
        return "文本通知模版卡片"

    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify the arguments passed.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return:
        """
        reqs = {
            "Either `main_title.title` should be existed or `sub_title_text` be existed":
                partial(
                    search, """
                    (main_title.title == null || main_title.title == '') &&
                    (sub_title_text == null || sub_title_text == '')
                """),
            "When `quote_area.type` is 1, the `quote_area.url` must be existed":
                partial(
                    search, """
                    quote_area.type == `1` &&
                    (quote_area.url == null || quote_area.url == '')
                """),
            "When `quote_area.type` is 2, the `quote_area.appid` must be existed":
                partial(
                    search, """
                    quote_area.type == `2` &&
                    (quote_area.appid == null || quote_area.appid == '')
                """),
            "The `horizontal_content_list.keyname` must be existed":
                partial(
                    search, """
                    length(
                        horizontal_content_list[?
                            keyname == null || keyname == ''
                        ]
                    ) != `0`
                """),
            "When `horizontal_content_list.type` is 1, "
            "the `horizontal_content_list.url` must be existed":
                partial(
                    search, """
                    length(
                        horizontal_content_list[?
                            type == `1` && (url == null || url == '')
                        ]
                    ) != `0`
                """),
            "When `horizontal_content_list.type` is 2, "
            "the `horizontal_content_list.media_id` must be existed":
                partial(
                    search, """
                    length(
                        horizontal_content_list[?
                            type == `2` && (media_id == null || media_id == '')
                        ]
                    ) != `0`
                """),
            "When `horizontal_content_list.type` is 3, "
            "the `horizontal_content_list.userid` must be existed":
                partial(
                    search, """
                    length(
                        horizontal_content_list[?
                            type == `3` && (userid == null || userid == '')
                        ]
                    ) != `0`
                """),
            "The `jump_list.title` must be existed":
                partial(
                    search, """
                    length(
                        jump_list[?
                            title == null || title == ''
                        ]
                    ) != `0`
                """),
            "When `jump_list.type` is 1, the `jump_list.url` must be existed":
                partial(
                    search, """
                    length(
                        jump_list[?
                            type == `1` && (url == null || url == '')
                        ]
                    ) != `0`
                """),
            "When `jump_list.type` is 2, the `jump_list.appid` must be existed":
                partial(
                    search, """
                    length(
                        jump_list[?
                            type == `2` && (appid == null || appid == '')
                        ]
                    ) != `0`
                """),
            "The `card_action` and `card_action.type` must be existed":
                partial(
                    search, """
                    card_action == null ||
                    card_action.type == null ||
                    card_action.type == ''
                """),
            "When `card_action.type` is 1, the `card_action.url` must be existed":
                partial(
                    search, """
                card_action.type == `1` &&
                (card_action.url == null || card_action.url == '')
            """),
            "When `card_action.type` is 2, the `card_action.appid` must be existed":
                partial(
                    search, """
                card_action.type == `2` &&
                (card_action.appid == null || card_action.appid == '')
            """),
        }
        for msg, cmd in reqs.items():
            if cmd(kwargs):
                raise ValueError(msg)

    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Convert the message to text card format data.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Converted data.
        """
        kw_ = {
            key: val for key, val in kwargs.items() if key in self._VALID_KEYS
        }
        result = ({
            "msgtype": "template_card",
            "template_card": {
                "card_type": "text_notice",
                **kw_,
            }
        },)
        return result, kwargs
