#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Store successful test units.

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/6/3 10:41
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from logging import DEBUG, basicConfig
from os import getenv
from pathlib import Path
from random import randint
from urllib.parse import urlparse, unquote

from dotenv import load_dotenv
from pytest import raises

# pylint: disable=import-error
from src.pywgb import FileWeComGroupBot
from src.pywgb import ImageWeComGroupBot
from src.pywgb import MarkdownWeComGroupBot
from src.pywgb import NewsWeComGroupBot
from src.pywgb import TextWeComGroupBot
from src.pywgb import VoiceWeComGroupBot
from src.pywgb.utils import MediaUploader
from tests.test_main import VALID_KEY, env_file, TEST_VALID_ARTICLES

basicConfig(level=DEBUG, format="%(levelname)s %(name)s %(lineno)d %(message)s")
load_dotenv(env_file, override=True)


def test_text_initial() -> None:
    """
    Test TextWeComGroupBot initialisation.
    :return:
    """
    valid_url = getenv("VALID_URL")
    print()
    print("Check valid key:", VALID_KEY)
    print("Check valid url:", valid_url)
    # Verify valid key and url
    bot = TextWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key
    assert f"TextWeComGroupBot({VALID_KEY})" == str(bot)
    assert valid_url.split("=")[-1] == TextWeComGroupBot(valid_url).key
    # Verify invalid key and url
    invalids = {
        getenv("INVALID_KEY"): "Invalid key format",
        getenv("INVALID_URL"): "Invalid key format",
        None: "Key is required",
    }
    for code, msg in invalids.items():
        with raises(ValueError) as exception_info:
            TextWeComGroupBot(code)
        assert msg in str(exception_info.value)


def test_markdown_initial() -> None:
    """
    Test MarkdownWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = MarkdownWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_image_initial() -> None:
    """
    Test ImageWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = ImageWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_news_initial() -> None:
    """
    Test NewsWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = NewsWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_file_initial() -> None:
    """
    Test NewsWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = FileWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key
    uploader = MediaUploader(VALID_KEY)
    assert urlparse(unquote(uploader.doc)).fragment == uploader._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == uploader.key


def test_voice_initial() -> None:
    """
    Test VoiceWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = VoiceWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_successful_send() -> None:
    """
    Test send message function
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(f"This is a test TEXT message: {randint(1, 100)}")
    print(result)
    assert result["errcode"] == 0
    bot = MarkdownWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(f"## This is a test Markdown message: {randint(1, 100)}")
    print(result)
    assert result["errcode"] == 0
    bot = ImageWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(file_path=Path(__file__).with_name("test.png"))
    print(result)
    assert result["errcode"] == 0
    bot = NewsWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(articles=TEST_VALID_ARTICLES)
    print(result)
    assert result["errcode"] == 0
    bot = FileWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(file_path=Path(__file__).with_name("test.png"))
    print(result)
    assert result["errcode"] == 0
    bot = VoiceWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(file_path=Path(__file__).with_name("test.amr"))
    print(result)
    assert result["errcode"] == 0
