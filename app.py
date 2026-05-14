import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, time
import plotly.express as px

# 1. 페이지 설정 및 아이콘 수정 (🌟 -> ☀️)
st.set_page_config(page_title="하루로그", layout="wide")
st.title("☀️ 하루로그: 활동 별 기분과 성취감 기록하기")

# 2. 격려 메시지 로직 (기존 동일)
REFLECTION_MESSAGES = {
    # ... (생략 - 기존 내용 유지) ...
}
def get_bucket(score):
    if score >= 4: return "high"
    elif score >= 2: return "mid"
    else: return "low"

# 3. 데이터 로드/저장 (기존 동일)
DATA_FILE = "tracker_data_v3.json"
def load_data():
    # ... (생략 - 기존 내용 유지) ...
    pass

def save_data(entries):
    # ... (생략 - 기존 내용 유지) ...
    pass

entries = load_data()

# --------------------------------------------------
# 4. [복구] 활동 기록 입력창 (Sidebar) - 사라진 부분
with st.sidebar:
    st.header("📝 오늘 활동 기록")
    record_date = st.date_input("활동 날짜", datetime.now())
    col1, col2 = st.columns(2)
    with col1: start_t = st.time_input("시작 시각", time(9, 0))
    with col2: end_t = st.time_input("종료 시각", time(10, 0))
    category = st.selectbox("대분류", ["업무/연구", "강의/상담", "운동", "식사/휴식", "자기계발", "인간관계", "기타"])
    sub_activity = st.text_input("세부 활동 명")
    st.divider()
    mood = st.slider("기분 점수", 1, 5, 3)
    ach = st.slider("성취감 점수", 1, 5, 3)
    notes = st.text_area("메모/느낀 점")
    
    if st.button("기록 저장 및 분석"):
        # 저장 로직은 복구했습니다.
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        activity_dt = datetime.combine(record_date, start_t)
        
        m_bucket, a_bucket = get_bucket(mood), get_bucket(ach)
        reflection = random.choice(REFLECTION_MESSAGES.get((m_bucket, a_bucket), ["오늘도 수고하셨습니다."]))
        
        new_entry = {
            "id": datetime.now().timestamp(),
            "sort_key": activity_dt.strftime("%Y-%m-%d %H:%M"),
            "date": record_date.strftime("%Y-%m-%d"),
            "day_of_week": weekdays[record_date.weekday()],
            "display_time": f"{record_date.strftime('%m/%d')} {start_t.strftime('%H:%M')}",
            "start": start_t.strftime("%H:%M"),
            "end": end_t.strftime("%H:%M"),
            "category": category,
            "sub_activity": sub_activity,
            "mood": mood,
            "achievement": ach,
            "notes": notes,
            "reflection": reflection
        }
        entries.append(new_entry)
        save_data(entries)
        st.balloons()
        st.rerun()
# --------------------------------------------------

# 5. 메인 화면 분석 (기능 유지 및 아이콘 수정)
if entries:
    df = pd.DataFrame(entries)
    df = df.sort_values(by="sort_key")

    # 교수님 요청 사항: 그래프 제목 아이콘 변경 (☀️ -> 🌙)
    st.subheader("🌙 활동 시각별 마음의 변화")
    
    fig = px.line(df, x="display_time", y=["mood", "achievement"], 
                  markers=True, 
                  hover_data={"display_time": True, "sub_activity": True},
                  labels={"value": "점수", "display_time": "활동 시각", "variable": "항목"})
    fig.update_yaxes(range=[0.5, 5.5])
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    # 다차원 데이터 필터링 (생략 - 기존 내용 유지)
    # ... (이하 필터링 및 리스트 로직 동일) ...
