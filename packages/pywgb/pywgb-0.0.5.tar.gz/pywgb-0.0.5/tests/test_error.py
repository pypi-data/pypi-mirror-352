#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test error module

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 14:58
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from logging import DEBUG, basicConfig
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from pytest import raises

# pylint: disable=import-error
from src.pywgb import FileWeComGroupBot
from src.pywgb import ImageWeComGroupBot
from src.pywgb import MarkdownWeComGroupBot
from src.pywgb import NewsWeComGroupBot
from src.pywgb import TextWeComGroupBot
from src.pywgb import VoiceWeComGroupBot
from tests.test_main import env_file, TEST_VALID_ARTICLES

basicConfig(level=DEBUG, format="%(levelname)s %(name)s %(lineno)d %(message)s")
load_dotenv(env_file, override=True)


def test_overheat() -> None:
    """
    Test overheat function
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    bot.send("This message was delayed by overheat", test="overheat")


def test_request_exception() -> None:
    """
    Test request exception
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    with raises(ConnectionRefusedError) as exception_info:
        bot.send("This message WON'T be sent, cause by request error",
                 test="request_error")
    assert "Unable to initiate API request correctly" in str(
        exception_info.value)
    with raises(IOError) as exception_info:
        bot.send("This message WON'T be sent, cause by API error",
                 test="api_error")
    assert "Request failed, please refer to the official manual" in str(
        exception_info.value)


def test_verify_text_error() -> None:
    """
    Test TEXT verification error.
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    with raises(ValueError) as error:
        bot.send()
    assert "The msg parameter is required" in str(error.value)
    err_msg = "parameter should be a list of strings"
    tests = [
        [123],
        (123,),
    ]
    for test in tests:
        with raises(ValueError) as error:
            bot.send("This message won't be sent, cause verify error.",
                     mentioned_mobile_list=test)
        assert err_msg in str(error.value)


def test_verify_markdown_error() -> None:
    """
    Test MARKDOWN verification error.
    :return:
    """
    bot = MarkdownWeComGroupBot(getenv("VALID_KEY"))
    with raises(ValueError) as error:
        bot.send()
    assert "The msg parameter is required" in str(error.value)


def test_verify_news_error() -> None:
    """
    Test News verification error.
    :return:
    """
    bot = NewsWeComGroupBot(getenv("VALID_KEY"))
    # Test empty articles
    with raises(ValueError) as exception_info:
        bot.send()
    assert "The articles parameter is required" in str(exception_info.value)
    with raises(ValueError) as exception_info:
        bot.send(articles=[])
    assert "The articles parameter is empty" in str(exception_info.value)
    # Test oversize articles
    with raises(ValueError) as exception_info:
        articles = [TEST_VALID_ARTICLES[0] for _ in range(9)]
        bot.send(articles=articles)
    assert "Too many articles." in str(exception_info.value)
    # Test data error and parameter error
    tests = {
        "article_data_error": "data is not a dict",
        "article_parameter_error": "lack required parameter",
    }
    for code, msg in tests.items():
        with raises(ValueError) as exception_info:
            bot.send(articles=TEST_VALID_ARTICLES, test=code)
        assert msg in str(exception_info.value)


def test_verify_image_error() -> None:
    """
    Test image verification error.
    :return:
    """
    bot = ImageWeComGroupBot(getenv("VALID_KEY"))
    with raises(ValueError) as exception_info:
        bot.send()
    assert "The file_path parameter is required" in str(exception_info.value)
    file = Path(__file__).with_name("test.png")
    mapper = {
        "wrong_format_image": "Just support image type: jpg or png",
        "oversize_image": "The image is too large, more than 2M",
    }
    for code, msg in mapper.items():
        with raises(ValueError) as exception_info:
            bot.send(file_path=file, test=code)
        assert msg in str(exception_info.value)


def test_verify_file_error() -> None:
    """
    Test verify file error.
    :return:
    """
    bot = FileWeComGroupBot(getenv("VALID_KEY"))
    # Test lack file
    with raises(ValueError) as exception_info:
        bot.send()
    assert "The file_path parameter is required" in str(exception_info.value)
    # Test empty file
    with raises(ValueError) as exception_info:
        bot.send(file_path=None)
    assert "The file_path parameter is required" in str(exception_info.value)
    # Test invalid file
    with raises(ValueError) as exception_info:
        bot.send(file_path="234234234.txt")
    assert "The file_path parameter not exists" in str(exception_info.value)


def test_verify_voice_error() -> None:
    """
    Test voice verification error.
    :return:
    """
    bot = VoiceWeComGroupBot(getenv("VALID_KEY"))
    # Test lack file
    with raises(ValueError) as exception_info:
        bot.send()
    assert "The file_path parameter is required" in str(exception_info.value)
    # Test invalid file format
    file = Path(__file__).with_name("test.png")
    with raises(ValueError) as exception_info:
        bot.send(file_path=file, test="wrong_format_voice")
    assert "Just support voice type: amr" in str(exception_info.value)
