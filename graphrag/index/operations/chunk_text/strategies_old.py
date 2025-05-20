# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing chunk strategies."""

from collections.abc import Iterable
from typing import Any

import nltk
import tiktoken
from datashaper import ProgressTicker

# import graphrag.config.defaults as defs
from graphrag.index.operations.chunk_text.typing_ import TextChunk
from graphrag.index.text_splitting.text_splitting import Tokenizer


def run_tokens(
    input: list[str], args: dict[str, Any], tick: ProgressTicker
) -> Iterable[TextChunk]:
    """Chunks text into chunks based on encoding tokens."""
    # tokens_per_chunk = args.get("chunk_size", defs.CHUNK_SIZE)
    # chunk_overlap = args.get("chunk_overlap", defs.CHUNK_OVERLAP)
    # encoding_name = args.get("encoding_name", defs.ENCODING_MODEL)
    tokens_per_chunk = args.get("chunk_size", 200)
    chunk_overlap = args.get("chunk_overlap", 50)
    encoding_name = args.get("encoding_name", 'cl100k_base')
    enc = tiktoken.get_encoding(encoding_name)

    def encode(text: str) -> list[int]:
        if not isinstance(text, str):
            text = f"{text}"
        return enc.encode(text)

    def decode(tokens: list[int]) -> str:
        return enc.decode(tokens)

    return _split_text_on_tokens(
        input,
        Tokenizer(
            chunk_overlap=chunk_overlap,
            tokens_per_chunk=tokens_per_chunk,
            encode=encode,
            decode=decode,
        ),
        tick,
    )


# Adapted from - https://github.com/langchain-ai/langchain/blob/77b359edf5df0d37ef0d539f678cf64f5557cb54/libs/langchain/langchain/text_splitter.py#L471
# So we could have better control over the chunking process
def _split_text_on_tokens(
    texts: list[str], enc: Tokenizer, tick: ProgressTicker
) -> list[TextChunk]:
    """Split incoming text and return chunks."""
    result = []
    mapped_ids = []

    for source_doc_idx, text in enumerate(texts):
        encoded = enc.encode(text)
        tick(1)
        mapped_ids.append((source_doc_idx, encoded))

    input_ids: list[tuple[int, int]] = [
        (source_doc_idx, id) for source_doc_idx, ids in mapped_ids for id in ids
    ]

    start_idx = 0
    cur_idx = min(start_idx + enc.tokens_per_chunk, len(input_ids))
    chunk_ids = input_ids[start_idx:cur_idx]
    while start_idx < len(input_ids):
        chunk_text = enc.decode([id for _, id in chunk_ids])
        doc_indices = list({doc_idx for doc_idx, _ in chunk_ids})
        result.append(
            TextChunk(
                text_chunk=chunk_text,
                source_doc_indices=doc_indices,
                n_tokens=len(chunk_ids),
            )
        )
        start_idx += enc.tokens_per_chunk - enc.chunk_overlap
        cur_idx = min(start_idx + enc.tokens_per_chunk, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]

    return result


def run_sentences(
    input: list[str], _args: dict[str, Any], tick: ProgressTicker
) -> Iterable[TextChunk]:
    """Chunks text into multiple parts by sentence."""
    for doc_idx, text in enumerate(input):
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            yield TextChunk(
                text_chunk=sentence,
                source_doc_indices=[doc_idx],
            )
        tick(1)


if __name__ == '__main__':

    # 模拟 ProgressTicker
    def mock_tick(count):
        print(f"Processed {count} items.")


    # 准备中文测试文本
    test_text = '''
    ### 揭开古人类生活的更多谜底
本报记者 周飞亚
“西南地区的旧石器越来越多,长江流 域日益支撑起史前考古的新天地…… 祝贺!”2024 年度全国十大考古新发现公布后, 一位考古人在朋友圈发出这样的感叹｡ 资阳濛溪河遗址群是四川第二个获此殊荣的旧石器考古项目｡2022 年,位于川西高原的稻城皮洛遗址也曾入选｡两个项目的领队,都是四川省文物考古研究院旧石器考古研究所所长郑喆轩｡

成为“十大”仅仅是开始｡评选结果公布当天,郑喆轩就匆匆赶回濛溪河遗址｡皮洛､濛溪河､射洪桃花河等重要遗址还有大量工作要做,资阳､内江等地的田野考古调查也在同步开展,整理研究也不能停下,考古队员们忙并快乐着｡

搁在几年前,现在这种状态,对于郑喆轩还是“不敢想象的幸福”｡
四川处于高原与平原之间,华南与华北之间,温带与亚热带之间,是古人类迁徙和文化交流十分重要的“十字路口”｡然而,在2019 年以前,四川比较明确的旧石器遗址仅有10 余处,国内外学者们只能被迫接受四川盆地和川西高原没有或者很晚才有少量古人类存在的“苦涩现实”,四川成为国际旧石器研究的“盆地” “洼地”｡

“如果能够扎实开展一些有针对性的工作,可能会有填补空白的重要突破!”11 年前,郑喆轩硕士毕业,带着“开疆拓土”的目标和期待来到四川｡然而,没有旧石器专业的人手,没有工作基础,缺乏可靠线索,工作的开展如“盲人摸象”,一度十分艰难｡头几年,郑喆轩只能通过翻阅历史资料､利用其他任务间隙“搭便车”做一点旧石器考古调查,收效甚微｡他做得最多的是配合基建开展的抢救性考古,参与发掘的遗址年代“从新石器直到建国后,偏偏没有旧石器”｡但在这个过程中,他也大致摸清了四川不同区域的地质地貌特点,为后面的工作积累了经验｡

短短五六年间,局面发生了“天翻地覆的变化”｡2019 年以来,四川逐步启动旧石器时代考古专项调查,取得了阶段性重大成果｡调查新发现旧石器遗址点300 余处,多个地区从无到有､从点到面,形成旧石器遗址群落,宛如漫天群星｡遗址的文化面貌也显示出独特性､多样性｡这证明,早在旧石器时代,四川就是现在东西方及中国南北方文化交流､人群迁徙的重要区域｡

“漫天群星”中,有两颗最为耀眼,那就是皮洛遗址､濛溪河遗址｡
皮洛遗址发现于2020 年｡遗址发现数量丰富､技术成熟的手斧和薄刃斧,是目前东亚地区形态最典型､技术最成熟､组合最完备的阿舍利晚期阶段文化遗存,对研究早期人类东西方文化交流､阿舍利技术传播路线等问题都提供了关键性证据｡据最新研究,皮洛遗址的年代最早已超过了距今20 万年,这意味着,人类至迟在20 万年前就登上了青藏高原东部｡

濛溪河遗址发现于2021 年,特殊的饱水埋藏环境,极为罕见地较完整保存了一个6 万-8 万年前的远古社会,从多方面改写了国际学术界对旧石器社会的认知｡其中以丰富的植物遗存最为特殊｡遗址发现的木器是世界罕见的早期加工利用有机质材料的实证,仿佛见证了一个“木器时代”｡遗存包含丰富的树木､果实和种子,核桃､花椒､接骨草等不少植物是在考古中最早的发现｡遗址还发现了用火､切割､琢制､刻划等多种行为的证据,穿孔的石头和橡果､石块骨片木头上的系列刻划痕,展现了远古人类的精神世界｡经过调查,考古队已确认了86 个濛溪河文化类型的遗址点,广泛分布在沱江和涪江流域的浅丘地貌区,形成濛溪河遗址群｡

2022 年发现的桃花河遗址也令人惊喜｡遗址发现上万件大中型石器,其丰富程度在南方地区的旧石器遗址中前所未见,还发现了石器加工厂､古人类活动面及其他罕见的复杂遗迹,应为早期人类的一个中心营地｡测年表明,最早的遗迹距今约30 万年｡

五六年,300 余个遗址,多个世界级的发现｡6 年前四川省文物考古研究院旧石器研究室成立时,仅有郑喆轩一人,如今已经有了11 名成员｡这个平均年龄30 岁的年轻团队,将在天府之国继续探索,揭开古人类生活的更多谜底｡

    '''
    test_input = [test_text]

    # 设置参数
    args = {
        "chunk_size": 200,
        "chunk_overlap": 50,
        "encoding_name": "cl100k_base"
    }


    # 测试当前文件中的 run_tokens 方法
    print("Testing current file's run_tokens method:")
    result_run_tokens = run_tokens(test_input, args, mock_tick)
    for chunk in result_run_tokens:
        print(f"文本块: {chunk.text_chunk}")
        print(f"源文档索引: {chunk.source_doc_indices}")
        print(f"令牌数量: {chunk.n_tokens}")
        print("-" * 20)

    # 测试当前文件中的 run_sentences 方法
    print("Testing current file's run_sentences method:")
    result_run_sentences = run_sentences(test_input, args, mock_tick)
    for chunk in result_run_sentences:
        print(f"Text chunk: {chunk.text_chunk}")
        print(f"Source doc indices: {chunk.source_doc_indices}")
        print("-" * 20)