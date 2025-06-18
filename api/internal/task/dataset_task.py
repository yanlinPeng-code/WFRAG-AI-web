#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/09/21 23:10
@Author  : thezehui@gmail.com
@File    : dataset_task.py
"""
from uuid import UUID

from celery import shared_task


@shared_task
def delete_dataset(dataset_id: UUID) -> None:
    """根据传递的知识库id删除特定的知识库信息"""
    from app.http.module import injector
    from internal.service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_dataset(dataset_id)
