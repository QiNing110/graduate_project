### 目标  
给定一个可能与该活动相关的文本文档及实体类型列表，从文本中识别所有指定类型的实体及这些实体之间的关系。  

### 步骤  
1. **识别所有实体**  
   对每个实体提取以下信息：  
   - **实体名称**（文中的实体）  
   - **实体类型**（从 `{entity_types}` 中选择）  
   - **实体描述**（详细描述属性及活动）  
   格式：`("entity"{tuple_delimiter}<实体名称>{tuple_delimiter}<实体类型>{tuple_delimiter}<实体描述>)`  

2. **识别实体关系**  
   从步骤1的实体中，识别所有**明确相关**的（源实体，目标实体）关系对。  
   对每对关系提取以下信息：  
   - **源实体**（步骤1中的名称）  
   - **目标实体**（步骤1中的名称）  
   - **关系描述**（解释两者如何关联）  
   - **关系强度**（数值，表示关联强度，范围1-10）  
   格式：`("relationship"{tuple_delimiter}<源实体>{tuple_delimiter}<目标实体>{tuple_delimiter}<关系描述>{tuple_delimiter}<关系强度>)`  

3. **输出格式**  
   将步骤1和2的结果合并为一个列表，用 `{record_delimiter}` 分隔每条记录，最终以 `{completion_delimiter}` 结尾。  

### 关键注意事项  
- 仅识别**明确提及**的实体和关系。  
- 关系强度需基于上下文逻辑评分（如直接隶属关系为9，间接关联为2）。  
- 保留占位符符号（如 `|`），勿替换为其他字符。确保分隔符和结构正确。  
- 仅输出按照要求格式的实体及其关系，不得输出其他任何无关内容。 

######################

### 示例  
**示例1**  
实体类型：`ORGANIZATION, PERSON`  
文本：  
维达尼斯公司的中央机构定于周一和周四举行会议，该机构计划于太平洋夏令时周四下午 1 点 30 分发布其最新的政策决定，随后将召开新闻发布会，届时中央机构主席马丁·史密斯将回答问题。投资者预计市场策略委员会将把基准利率维持在 3.5%-3.75%的区间内不变。
######################  
输出：
```
("entity"{tuple_delimiter}中央机构{tuple_delimiter}ORGANIZATION{tuple_delimiter}中央机构是位于维德纳蒂斯的联邦储备银行，它会在周一和周四设定利率。)
{record_delimiter}
("entity"{tuple_delimiter}马丁·史密斯{tuple_delimiter}PERSON{tuple_delimiter}马丁·史密斯是中央机构的主席。)
{record_delimiter}
("entity"{tuple_delimiter}市场策略委员会{tuple_delimiter}ORGANIZATION{tuple_delimiter}中央机构委员会负责做出有关利率以及维达尼斯货币供应量增长的关键决策。)
{record_delimiter}
("relationship"{tuple_delimiter}马丁·史密斯{tuple_delimiter}中央机构{tuple_delimiter}马丁·史密斯是中央机构的主席，他将在新闻发布会上回答问题。{tuple_delimiter}9)
{completion_delimiter}
```

**示例2**  
实体类型：`ORGANIZATION`  
文本： 
周四，在全球交易所上市交易的 TechGlobal（TG）公司的股票在开盘首日飙升。但首次公开募股（IPO）专家警告称，这家半导体公司的首次公开上市表现并不能代表其他新上市公司的表现情况。

TechGlobal 原是一家上市公司，于 2014 年被 Vision Holdings 收购转为私有企业。这家成熟的芯片设计公司表示，其产品为 85%的高端智能手机提供动力支持。
######################  
输出：
("entity"{tuple_delimiter}TechGlobal{tuple_delimiter}ORGANIZATION{tuple_delimiter}TechGlobal 是一家现已在环球交易所上市的公司，其产品为 85% 的高端智能手机提供动力支持。)
{record_delimiter}
("entity"{tuple_delimiter}Vision Holdings{tuple_delimiter}ORGANIZATION{tuple_delimiter}Vision Holdings是一家此前拥有TechGlobal公司的企业。)
{record_delimiter}
("relationship"{tuple_delimiter}TechGlobal{tuple_delimiter}Vision Holdings{tuple_delimiter}Vision Holdings公司自 2014 年起就一直拥有TechGlobal公司，直至目前。{tuple_delimiter}5)
{completion_delimiter}
######################


######################
### 实际数据  
实体类型：`{entity_types}`  
文本：`{input_text}`  
######################
输出:

