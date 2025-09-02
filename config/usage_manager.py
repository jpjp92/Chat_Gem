# config/usage_manager.py
# 사용량 추적 및 관리 전담 모듈

from datetime import datetime, timezone
import streamlit as st

def get_usage_count():
    """일일 사용량 추적"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if "usage_data" not in st.session_state:
        st.session_state.usage_data = {"date": today, "count": 0}
    if st.session_state.usage_data["date"] != today:
        st.session_state.usage_data = {"date": today, "count": 0}
    return st.session_state.usage_data["count"]

def increment_usage():
    """사용량 증가"""
    if "usage_data" in st.session_state:
        st.session_state.usage_data["count"] += 1
    else:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        st.session_state.usage_data = {"date": today, "count": 1}
