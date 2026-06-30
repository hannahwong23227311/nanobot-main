import streamlit as st
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

# Try to import RAG search tools
try:
    from knowledge_tool import TOOLS, search_resources, search_medication, search_cognitive, search_psychological
    RAG_AVAILABLE = True
except Exception:
    TOOLS = []
    RAG_AVAILABLE = False

# --- Helper Functions ---

def get_telegram_messages():
    """Extract Telegram conversation data from the session file."""
    home = Path(os.environ.get("USERPROFILE", "."))
    session_dir = home / ".nanobot" / "workspace" / "sessions"
    
    telegram_files = list(session_dir.glob("telegram_*.jsonl"))
    if not telegram_files:
        return []
    
    messages = []
    for file in telegram_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if 'content' in data and data.get('content'):
                            messages.append({
                                'role': 'user' if data.get('role') == 'user' else 'assistant',
                                'content': data.get('content', ''),
                                'time': data.get('timestamp', datetime.now().isoformat())
                            })
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue
    
    return messages

def get_message_count():
    """Get the number of messages in the Telegram session file."""
    home = Path(os.environ.get("USERPROFILE", "."))
    session_dir = home / ".nanobot" / "workspace" / "sessions"
    
    telegram_files = list(session_dir.glob("telegram_*.jsonl"))
    if not telegram_files:
        return 0
    
    count = 0
    for file in telegram_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if 'content' in data and data.get('content'):
                            count += 1
                    except:
                        continue
        except:
            continue
    return count

def filter_messages_by_query(messages, query):
    """Filter messages that contain the query string."""
    if not query:
        return messages
    filtered = []
    for msg in messages:
        content = msg.get('content', '')
        if query.lower() in content.lower():
            filtered.append(msg)
    return filtered

def find_knowledge_dir() -> Path:
    env = os.environ.get("NANOBOT_KNOWLEDGE_DIR")
    if env:
        p = Path(env)
        if p.exists():
            return p
    try:
        repo_root = Path(__file__).resolve().parent
        repo_k = repo_root / "knowledge"
        if repo_k.exists():
            return repo_k
    except Exception:
        pass
    up = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    p = Path(up) / ".nanobot" / "knowledge"
    return p

# --- Smart Refresh: Check for new data ---

def check_for_new_messages():
    """Check if there are new messages since last check."""
    current_count = get_message_count()
    
    if 'last_message_count' not in st.session_state:
        st.session_state.last_message_count = current_count
        return False
    
    if current_count > st.session_state.last_message_count:
        st.session_state.last_message_count = current_count
        return True
    
    return False

# --- Load Data ---
if 'messages' not in st.session_state:
    st.session_state.messages = get_telegram_messages()
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_active' not in st.session_state:
    st.session_state.search_active = False
if 'last_message_count' not in st.session_state:
    st.session_state.last_message_count = get_message_count()

# Check for new messages
if check_for_new_messages():
    # New messages found! Refresh the data
    st.session_state.messages = get_telegram_messages()
    st.rerun()

def refresh_data():
    st.session_state.messages = get_telegram_messages()
    st.session_state.last_message_count = get_message_count()
    st.rerun()

# Set page config
st.set_page_config(
    page_title="小安 - 照顧者儀表板",
    page_icon="📊",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.header("👤 患者選擇")
    
    knowledge_dir = find_knowledge_dir()
    patient_files = []
    if knowledge_dir and knowledge_dir.exists():
        patient_files = list(knowledge_dir.glob("patient_*.txt"))
    
    if patient_files:
        patient_names = [f.stem.replace("patient_", "") for f in patient_files]
        selected_patient = st.selectbox("選擇患者", patient_names)
    else:
        st.info("使用示範數據 (陳婆婆)")
        selected_patient = "陳婆婆"
    
    # Smart refresh status
    st.caption("🔍 智能監測：有新對話時自動更新")
    
    if st.button("🔄 立即重新整理", use_container_width=True):
        refresh_data()
    
    st.markdown("---")
    st.header("🔎 搜尋對話")
    
    search_input = st.text_input("關鍵字", value=st.session_state.search_query, placeholder="例如: 耆智園, 藥物")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔎 搜尋", use_container_width=True):
            st.session_state.search_query = search_input
            st.session_state.search_active = True
            st.rerun()
    with col2:
        if st.button("🔄 清除", use_container_width=True):
            st.session_state.search_query = ""
            st.session_state.search_active = False
            st.rerun()
    
    st.markdown("---")
    st.header("📚 知識庫搜尋")
    
    if RAG_AVAILABLE:
        func_map = {
            "search_resources": search_resources,
            "search_medication": search_medication,
            "search_cognitive": search_cognitive,
            "search_psychological": search_psychological,
        }
        
        rag_names = [t["name"] for t in TOOLS]
        selected_rag = st.selectbox("選擇工具", rag_names)
        rag_query = st.text_input("查詢內容", placeholder="例如: 多奈哌齊副作用")
        
        if st.button("📚 搜尋知識庫", use_container_width=True):
            fn = func_map.get(selected_rag)
            if fn and rag_query:
                with st.spinner("搜尋中…"):
                    try:
                        res = fn(rag_query)
                        st.markdown("---")
                        st.markdown(f"**工具:** `{selected_rag}`")
                        st.markdown(f"**查詢:** `{rag_query}`")
                        st.markdown("---")
                        if res:
                            st.text_area("結果", res, height=150)
                        else:
                            st.info("沒有找到相關資訊")
                    except Exception as e:
                        st.error(f"檢索失敗: {e}")
    else:
        st.info("未偵測到 RAG 工具")

# --- Main Content ---
st.title("📊 小安 - 照顧者儀表板")

# Show last update time and message count
messages = st.session_state.messages
message_count = len(messages)

st.caption(f"📱 總對話數：{message_count}")

# --- Filter messages ---
if st.session_state.search_active and st.session_state.search_query:
    filtered_messages = filter_messages_by_query(messages, st.session_state.search_query)
    st.info(f"🔍 顯示 {len(filtered_messages)} 條相關對話 (關鍵字: '{st.session_state.search_query}')")
else:
    filtered_messages = messages

# --- Row 1: Key Metrics ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💬 總對話", message_count)

with col2:
    if st.session_state.search_active and st.session_state.search_query:
        st.metric("🔍 相關對話", len(filtered_messages))
    else:
        st.metric("🧠 認知表現", "78%", "+5%")

with col3:
    st.metric("💊 用藥依從", "92%", "+3%")

with col4:
    st.metric("❤️ 情緒狀態", "良好")

# --- Row 2: Two Columns ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 認知訓練表現（過去7天）")
    cognitive_data = pd.DataFrame({
        "日期": ["一", "二", "三", "四", "五", "六", "日"],
        "記憶力": [70, 75, 72, 80, 85, 82, 78],
        "語言": [65, 70, 68, 75, 80, 78, 76],
        "計算": [80, 82, 85, 83, 88, 85, 82]
    })
    st.line_chart(cognitive_data.set_index("日期"), height=250)

with col2:
    st.subheader("💊 用藥記錄")
    medication_data = pd.DataFrame({
        "藥物": ["多奈哌齊", "卡巴拉汀"],
        "今日": ["✅ 已服", "⏳ 未服"],
        "依從率": ["100%", "85%"]
    })
    st.table(medication_data)

# --- Row 3: Warnings ---
st.subheader("⚠️ 警示")
warnings = [
    ("⚠️ 患者過去3日有2次未按時服藥", "warning"),
    ("ℹ️ 認知訓練分數持續上升 +5%", "info"),
    ("✅ 情緒狀態保持穩定", "success")
]
for msg, level in warnings:
    if level == "warning":
        st.warning(msg)
    elif level == "info":
        st.info(msg)
    else:
        st.success(msg)

# --- Row 4: Conversation History ---
st.subheader("💬 對話記錄")

if filtered_messages:
    for msg in filtered_messages[-15:]:
        role = "🧑 患者" if msg.get('role') == 'user' else "🤖 小安"
        content = str(msg.get('content', ''))
        if content:
            st.text(f"{role}: {content}")
else:
    st.info("暫無對話記錄。請先在 Telegram 與小安對話！")

# --- Patient Profile (Collapsible) ---
with st.expander("👤 患者檔案"):
    st.write(f"**姓名：** {selected_patient}")
    st.write("**年齡：** 72歲")
    st.write("**診斷：** 輕度認知障礙 (MCI)")
    st.write("**照顧者：** 陳先生 (兒子)")
    st.write("**最近更新：** 2026-06-30")

# --- Footer ---
st.divider()
st.caption(f"小安 - 認知健康助理 | 💬 {message_count} 條對話 | 🔍 智能監測中")