# knowledge_tool.py - Multi-RAG Knowledge Search

import os
from pathlib import Path

def search_resources(query: str) -> str:
    """Search for center locations, contact info, transport, and opening hours."""
    results = []
    knowledge_dir = Path(os.environ.get("USERPROFILE", ".")) / ".nanobot" / "knowledge"
    
    for file in knowledge_dir.glob("*.txt"):
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if query.lower() in content.lower():
                lines = content.split('\n')
                for line in lines:
                    if query.lower() in line.lower():
                        results.append(f"📄 {file.name}: {line.strip()}")
        except:
            continue
    
    return "\n\n".join(results[:2]) if results else "小安暫時冇呢個資源資訊。請聯絡中心查詢。"

def search_medication(query: str) -> str:
    """Search for medication information, side effects, dosage, and interactions."""
    results = []
    knowledge_dir = Path(os.environ.get("USERPROFILE", ".")) / ".nanobot" / "knowledge"
    
    for file in knowledge_dir.glob("*.txt"):
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if query.lower() in content.lower():
                lines = content.split('\n')
                for line in lines:
                    if query.lower() in line.lower():
                        results.append(f"📄 {file.name}: {line.strip()}")
        except:
            continue
    
    return "\n\n".join(results[:2]) if results else "小安暫時冇呢個藥物資訊。請諮詢醫生或藥劑師。"

def search_cognitive(query: str) -> str:
    """Search for cognitive training exercises and activity plans."""
    results = []
    knowledge_dir = Path(os.environ.get("USERPROFILE", ".")) / ".nanobot" / "knowledge"
    
    for file in knowledge_dir.glob("*.txt"):
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if query.lower() in content.lower():
                lines = content.split('\n')
                for line in lines:
                    if query.lower() in line.lower():
                        results.append(f"📄 {file.name}: {line.strip()}")
        except:
            continue
    
    return "\n\n".join(results[:2]) if results else "小安暫時冇呢個認知訓練資訊。請諮詢職業治療師。"

def search_psychological(query: str) -> str:
    """Search for psychological support, coping strategies, and anxiety management."""
    results = []
    knowledge_dir = Path(os.environ.get("USERPROFILE", ".")) / ".nanobot" / "knowledge"
    
    for file in knowledge_dir.glob("*.txt"):
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if query.lower() in content.lower():
                lines = content.split('\n')
                for line in lines:
                    if query.lower() in line.lower():
                        results.append(f"📄 {file.name}: {line.strip()}")
        except:
            continue
    
    return "\n\n".join(results[:2]) if results else "小安暫時冇呢個心理支援資訊。請聯絡專業人士。"

# Register all tools
TOOLS = [
    {
        "name": "search_resources",
        "description": "Search for center locations, contact info, transport, and opening hours",
        "function": search_resources,
    },
    {
        "name": "search_medication",
        "description": "Search for medication information, side effects, dosage, and interactions",
        "function": search_medication,
    },
    {
        "name": "search_cognitive",
        "description": "Search for cognitive training exercises and activity plans",
        "function": search_cognitive,
    },
    {
        "name": "search_psychological",
        "description": "Search for psychological support, coping strategies, and anxiety management",
        "function": search_psychological,
    },
]