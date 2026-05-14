import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px  # 한글 깨짐 방지를 위해 Plotly 사용

# 1. 페이지 설정
st.set_page_config(page_title="하루로그", layout="wide")

# 2. 데이터 파일 설정
DATA_FILE = "tracker_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

# 3. 메인 화면
st.title("🌟 하루로그: 기분 & 성취감 트래커")
entries = load_data()

# 4. 사이드바 입력
with st.sidebar:
    st.header("📝 오늘의 기록")
    cat = st.selectbox("카테고리", ["업무/학업", "식사", "휴식", "운동", "사람 만남", "자기계발", "기타"])
    mood = st.slider("기분 점수", 1, 5, 3)
    ach = st.slider("성취감 점수", 1, 5, 3)
    notes = st.text_area("메모")
    
    if st.button("데이터 저장하기"):
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": cat,
            "mood": mood,
            "achievement": ach,
            "notes": notes
        }
        entries.append(new_entry)
        save_data(entries)
        st.success("저장되었습니다!")
        st.rerun()

# 5. 메인 화면 - 그래프 및 목록
if entries:
    df = pd.DataFrame(entries)
    
    st.subheader("📊 기분 및 성취감 변화")
    # 한글 깨짐 없는 Plotly 차트 사용
    fig = px.line(df, x="timestamp", y=["mood", "achievement"], 
                  labels={"value": "점수", "timestamp": "시간", "variable": "항목"},
                  markers=True)
    fig.update_layout(legend_title_text='구분')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📜 최근 기록")
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.info("왼쪽 사이드바에서 오늘 첫 번째 기분을 기록해 보세요!")
