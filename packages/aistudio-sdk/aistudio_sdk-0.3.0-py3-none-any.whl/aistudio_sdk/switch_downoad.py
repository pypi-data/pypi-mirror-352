# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2025 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
本文件实现了sdk cdn下载的功能

Authors: zhaoqingtao(zhaoqingtaog@baidu.com)
Date:    2025/05/23
"""
import copy
import requests
from urllib.parse import urlparse, urlunparse
from aistudio_sdk import config


def switch_cdn(url, headers, get_headers):
    """
    switch to cdn host
    """
    headers_range = {} if headers is None else copy.deepcopy(headers)
    headers_range['Range'] = f'bytes=0-1'
    response = requests.get(url, headers=headers_range, stream=True,
                            timeout=config.CONNECTION_TIMEOUT, allow_redirects=False)
    if response.is_redirect:
        redirect_url = response.headers.get("Location")
        parsed = urlparse(redirect_url)
        parsed = parsed._replace(netloc=config.STUDIO_CDN_HOST)
        new_url = urlunparse(parsed)
        get_headers.pop("Authorization", None)
        return new_url
    return url