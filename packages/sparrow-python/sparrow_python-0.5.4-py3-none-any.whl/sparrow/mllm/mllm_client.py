#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MLLM client
"""

import pandas as pd
from typing import List, Callable, Optional, Any, Union
from sparrow.llm.openaiclient import OpenAIClient
from sparrow.vllm.client.image_processor_helper import batch_process_messages
from sparrow.vllm.client.image_processor import ImageCacheConfig
from abc import ABC, abstractmethod

class MllmClientBase(ABC):
    """
    MLLM客户端抽象基类
    定义了所有MLLM客户端必须实现的核心接口
    """
    
    @abstractmethod
    async def call_llm(
        self,
        messages_list,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        调用LLM的抽象方法
        
        Args:
            messages_list: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数
            
        Returns:
            response_list: 响应列表
        """
        pass
    
    # 移除process_text和process_image抽象方法 - 它们现在是数据处理的工具方法


class MllmClient(MllmClientBase):
    """
    MLLM客户端实现类
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key="EMPTY",
        concurrency_limit=10,
        max_qps=50,
        timeout=60,
        retry_times=3,
        retry_delay=0.55,
        cache_image=False,
        **kwargs,
    ):
        """
        初始化MLLM客户端
        
        Args:
            model: 模型名称
            base_url: API基础URL
            api_key: API密钥
            concurrency_limit: 并发限制
            max_qps: 最大QPS
            timeout: 超时时间（秒）
            retry_times: 重试次数
            retry_delay: 重试延迟（秒）
            cache_image: 是否缓存图片
            **kwargs: 其他参数
        """
        self.client = OpenAIClient(
            api_key=api_key,
            base_url=base_url,
            concurrency_limit=concurrency_limit,
            max_qps=max_qps,
            timeout=timeout,
            retry_times=retry_times,
            retry_delay=retry_delay,
            **kwargs,
        )
        self.model = model
        self.cache_config = ImageCacheConfig(
            enabled=cache_image,
            cache_dir="image_cache",
            force_refresh=False,
            retry_failed=False,
        )
        
        # 延迟导入避免循环引用
        from .table_processor import MllmTableProcessor
        from .folder_processor import MllmFolderProcessor
        self.table = MllmTableProcessor(self)
        self.folder = MllmFolderProcessor(self)
    
    async def call_llm(
        self,
        messages_list,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        调用LLM
        
        Args:
            messages_list: 消息列表
            model: 模型名称，默认使用初始化时指定的模型
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数
            
        Returns:
            response_list: 响应列表
        """
        if model is None:
            model = self.model

        messages_list = await batch_process_messages(
            messages_list,
            preprocess_msg=True,
            max_concurrent=8,
            cache_config=self.cache_config,
        )
        response_list, _ = await self.client.chat_completions_batch(
            messages_list=messages_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            return_summary=True,
            safety_level=safety_level,
            **kwargs,
        )
        return response_list
    
    async def call_llm_with_selection(
        self,
        messages_list,
        n_predictions: int = 3,
        selector_fn: Optional[Callable[[List[Any]], Any]] = None,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        增强版LLM调用方法，对每条消息进行n次预测，并使用选择函数选择最佳结果
        
        Args:
            messages_list: 消息列表
            n_predictions: 每条消息预测次数
            selector_fn: 选择函数，接收n个响应列表，返回选中的响应
                         如果为None，默认返回第一个响应
            model: 模型名称，默认使用初始化时指定的模型
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数
            
        Returns:
            response_list: 选择后的响应列表
        """
        if model is None:
            model = self.model
            
        # 默认选择函数(如果未提供)，简单返回第一个响应
        if selector_fn is None:
            selector_fn = lambda responses: responses[0]
            
        # 为每条消息创建n个副本
        expanded_messages_list = []
        for messages in messages_list:
            for _ in range(n_predictions):
                expanded_messages_list.append(messages)
                
        # 调用模型获取所有响应
        messages_list = await batch_process_messages(
            expanded_messages_list,
            preprocess_msg=True,
            max_concurrent=8,
            cache_config=self.cache_config,
        )
        all_responses, _ = await self.client.chat_completions_batch(
            messages_list=messages_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            return_summary=True,
            safety_level=safety_level,
            **kwargs,
        )
        
        # 重组响应并应用选择函数
        selected_responses = []
        for i in range(0, len(all_responses), n_predictions):
            message_responses = all_responses[i:i+n_predictions]
            print(f"{message_responses=}")
            selected_response = selector_fn(message_responses)
            selected_responses.append(selected_response)
            
        return selected_responses

    async def call_llm_nested(
        self,
        messages_list_list,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        处理嵌套的messages_list_list结构
        将messages_list_list展平为messages_list，调用call_llm获取结果，再重组为response_list_list
        这样做可以提高整体调用性能

        Args:
            messages_list_list: 嵌套的消息列表列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数

        Returns:
            response_list_list: 嵌套的响应列表列表，与输入结构对应
        """
        # 记录每个子列表的长度，用于之后重组结果
        lengths = [len(messages_list) for messages_list in messages_list_list]
        
        # 展平messages_list_list
        flattened_messages_list = []
        for messages_list in messages_list_list:
            flattened_messages_list.extend(messages_list)
        
        # 调用call_llm获取展平后的response_list
        flattened_response_list = await self.call_llm(
            flattened_messages_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safety_level=safety_level,
            **kwargs,
        )
        
        # 根据之前记录的长度，将展平的response_list重组为response_list_list
        response_list_list = []
        start_idx = 0
        for length in lengths:
            response_list_list.append(flattened_response_list[start_idx:start_idx + length])
            start_idx += length
        
        return response_list_list
    
    async def call_llm_nested_with_selection(
        self,
        messages_list_list,
        n_predictions: int = 3,
        selector_fn: Optional[Callable[[List[Any]], Any]] = None,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        处理嵌套的messages_list_list结构，并对每条消息进行多次预测和选择
        
        Args:
            messages_list_list: 嵌套的消息列表列表
            n_predictions: 每条消息预测次数
            selector_fn: 选择函数，接收n个响应列表，返回选中的响应
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数

        Returns:
            response_list_list: 嵌套的响应列表列表，与输入结构对应
        """
        # 记录每个子列表的长度，用于之后重组结果
        lengths = [len(messages_list) for messages_list in messages_list_list]
        
        # 展平messages_list_list
        flattened_messages_list = []
        for messages_list in messages_list_list:
            flattened_messages_list.extend(messages_list)
        
        # 调用enhanced_call_llm获取展平后的response_list
        flattened_response_list = await self.call_llm_with_selection(
            flattened_messages_list,
            n_predictions=n_predictions,
            selector_fn=selector_fn,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safety_level=safety_level,
            **kwargs,
        )
        
        # 根据之前记录的长度，将展平的response_list重组为response_list_list
        response_list_list = []
        start_idx = 0
        for length in lengths:
            response_list_list.append(flattened_response_list[start_idx:start_idx + length])
            start_idx += length
        
        return response_list_list

    # 所有table和dataframe相关方法已移至TableProcessor类

