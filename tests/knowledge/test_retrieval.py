import pytest

from nanobot.agent.tools.knowledge_tool import KnowledgeRetrievalTool


def test_search_returns_fragment():
    tool = KnowledgeRetrievalTool()
    results = tool.search("睡眠", top_k=3)
    assert isinstance(results, list)
    assert len(results) >= 1
    first = results[0]
    assert first["source"] == "test_source"
    text = tool.get_fragment_text(first["path"])
    assert text is not None
    assert "睡眠建議" in text


def test_search_no_result():
    tool = KnowledgeRetrievalTool()
    results = tool.search("不存在的詞彙_測試_xyz", top_k=3)
    assert results == []
