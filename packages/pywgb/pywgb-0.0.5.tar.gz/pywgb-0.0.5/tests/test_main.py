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
from src.pywgb import VoiceWeComGroupBot
from src.pywgb.utils import MediaUploader

basicConfig(level=DEBUG, format="%(levelname)s %(name)s %(lineno)d %(message)s")
env_file = Path(__file__).parent.with_name(".env")
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


def main():  # pragma: no cover
    """
    For unit testing
    :return:
    """
    bot = VoiceWeComGroupBot(getenv("VALID_KEY"))
    uploader = MediaUploader(getenv("VALID_KEY"))
    print(bot)
    file_path = Path(__file__).with_name("test.amr")
    result = uploader.upload(file_path)
    print(result)
    result = bot.send(file_path=file_path)
    print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
