#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/11/2 18:07
@Author  : thezehui@gmail.com
@File    : account_entity.py
"""
from enum import Enum


class AccountStatus(str, Enum):
    """账户状态类型枚举"""
    ACTIVE = "active"  # 激活账号
    BANNED = "banned"  # 封禁账号
