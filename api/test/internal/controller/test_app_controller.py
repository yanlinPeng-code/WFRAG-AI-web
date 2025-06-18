#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/4 16:29
@Author  : thezehui@gmail.com
@File    : test_app_controller.py
"""
import pytest

from pkg.response import HttpCode


class TestAppController:
    """app控制器的测试类"""

    @pytest.mark.parametrize(
        "app_id,query",
        [
            ("e1e8267d-da3d-4093-9f12-70c5a9bccaf0", None),
            ("e1e8267d-da3d-4093-9f12-70c5a9bccaf0", "你好，你是"),
        ]
    )
    def test_completion(self, app_id, query, client):
        resp = client.post(f"/apps/{app_id}/debug", json={"query": query})
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATE_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
