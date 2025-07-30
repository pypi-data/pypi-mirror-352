#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/30 10:31
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from . import AbstractWeComGroupBot, ConvertedData


class NewsWeComGroupBot(AbstractWeComGroupBot):
    """News type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "图文类型"

    def verify_arguments(self, *args, **kwargs) -> None:
        """
        Verify the arguments passed.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return:
        """
        try:
            articles = kwargs["articles"]
        except KeyError as error:
            raise ValueError("The articles parameter is required.") from error
        if not articles:
            raise ValueError("The articles parameter is empty.")
        if len(articles) > 8:
            raise ValueError("Too many articles. The maximum limit is 8")
        # Check the article's required parameters
        test = kwargs.get("test")
        for index, article in enumerate(articles):
            if not isinstance(article, dict) or test == "article_data_error":
                msg_ = f"The No.{index + 1} article data is not a dict"
                raise ValueError(msg_)
            for param in ["title", "url"]:
                if param not in article or not article[
                        param] or test == "article_parameter_error":
                    msg_ = f"The No.{index + 1} article lack required parameter: {param}"
                    raise ValueError(msg_)

    # pylint:disable=unused-argument
    def convert_arguments(self, *args, **kwargs) -> ConvertedData:
        """
        Convert the message to News format.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        result = ({
            "msgtype": "news",
            "news": {
                "articles": kwargs["articles"]
            }
        },)
        return result, kwargs
