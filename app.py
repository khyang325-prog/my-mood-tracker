import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, time
import plotly.express as px

# 1. 페이지 설정 (이전과 동일하게 유지)
st.set_page_config(page_title="하루로그", layout="wide")
st.title("🌟 하루로그: 활동 별 기분과 성취감 기록하기")

# 2. 격려 메시지 로직 (생략 - 기존과 동일)
# ... (중략) ...

# 3. 데이터 로드/저장 (에러 방지 로직 추가)
DATA_FILE = "tracker_data_v3.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # 이전 데이터에 sort_key가 없을 경우를 대비한 보정
                for entry in data:
                    if "sort_key" not in entry:
                        # 날짜와 시작시간을 조합해 임시 sort_key 생성
                        entry["sort_key"] = f"{entry.get('date', '2026-01-01')} {entry.get('start', '00:00')}"
                return data
            except:
                return []
    return []

def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

entries = load_data()

# 4. 사이드바 입력 (기존 로직 유지)
with st.sidebar:
    st.header("📝 활동 기록")
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
        # ... (중략: 데이터 저장 로직은 이전과 동일) ...
        st.rerun()

# 5. 메인 화면 분석
if entries:
    df = pd.DataFrame(entries)
    # 정렬 전 데이터 확정
    df = df.sort_values(by="sort_key")

    # 교수님 요청 사항: 그래프 섹션 제목만 변경
    st.subheader("📊 활동 시각별 마음의 변화")
    
    fig = px.line(df, x="display_time", y=["mood", "achievement"], 
                  markers=True, 
                  hover_data={"display_time": True, "sub_activity": True},
                  labels={"value": "점수", "display_time": "활동 시각", "variable": "항목", "sub_activity": "상세 활동"})
    
    fig.update_yaxes(range=[0.5, 5.5])
    st.plotly_chart(fig, use_container_width=True)

    # ... (이하 필터링 및 리스트 로직 동일) ...
