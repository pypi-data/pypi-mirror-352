#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit test

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/6/3 14:42
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from logging import basicConfig, DEBUG
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

# pylint: disable=import-error
from src.pywgb import TextCardWeComGroupBot

basicConfig(level=DEBUG, format="%(levelname)s %(name)s %(lineno)d %(message)s")
env_file = Path(__file__).parent.with_name(".env")
errors_file = Path(__file__).with_name("card_errors.yml")
load_dotenv(env_file, override=True)
VALID_KEY = getenv("VALID_KEY")
TEST_VALID_ARTICLES = [{
    "title":
        "中秋节礼品领取",
    "description":
        "今年中秋节公司有豪礼相送",
    "url":
        "www.qq.com",
    "picurl":
        "http://res.mail.qq.com/node/ww/wwopenmng/images/independent/doc/test_pic_msg1.png"
}]
TEST_VALID_TEXT_CARD = {
    "main_title": {
        "title": "欢迎使用企业微信",
        "desc": "您的好友正在邀请您加入企业微信"
    },
    "emphasis_content": {
        "title": "100",
        "desc": "数据含义"
    },
    "quote_area": {
        "type": 1,
        "url": "https://work.weixin.qq.com/?from=openApi",
        "title": "引用文本标题",
        "quote_text": "Jack：企业微信真的很好用~\nBalian：超级好的一款软件！"
    },
    "sub_title_text": "下载企业微信还能抢红包！",
    "horizontal_content_list": [{
        "keyname": "邀请人",
        "value": "张三"
    }, {
        "keyname": "企微官网",
        "value": "点击访问",
        "type": 1,
        "url": "https://work.weixin.qq.com/?from=openApi"
    }],
    "jump_list": [{
        "type": 1,
        "url": "https://work.weixin.qq.com/?from=openApi",
        "title": "企业微信官网"
    }],
    "card_action": {
        "type": 1,
        "url": "https://work.weixin.qq.com/?from=openApi",
    }
}


def main():  # pragma: no cover
    """
    For unit testing
    :return:
    """
    bot = TextCardWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(**TEST_VALID_TEXT_CARD)
    print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
