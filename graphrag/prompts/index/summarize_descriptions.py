# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A file containing prompts definition."""

SUMMARIZE_PROMPT = """
您是一位负责生成以下所提供数据的全面总结的助手。
给定一个或两个实体，以及一系列与同一实体或一组实体相关的描述。
请将所有这些内容合并成一个全面的、综合性的描述。务必包含从所有描述中收集到的信息。
如果所提供的描述相互矛盾，请解决这些矛盾并提供一个单一、连贯的总结。
确保使用第三人称表述，并包含实体名称，以便我们了解完整的上下文。
#######
## 数据
实体: {entity_name}
描述列表: {description_list}
#######
输出:
"""
