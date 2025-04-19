# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Global Search system prompts."""

GENERAL_KNOWLEDGE_INSTRUCTION = """
该回复还可能包含数据集之外的相关现实世界知识，但必须明确标注验证标签 [LLM: verify] 。例如：
"这是一个由现实世界知识支持的示例句子 [LLM: verify]."
"""
