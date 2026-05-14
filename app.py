import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, time
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="하루로그", layout="wide")
# 메인 제목은 원래대로 유지합니다.
st.title("🌟 하루로그: 활동 별 기분과 성취감 기록하기")

# 2. 데이터 로드/저장 (안전장치 강화)
DATA_FILE = "tracker_data_v3.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # [복구 포인트] 기존 데이터에 sort_key가 없어도 에러가 나지 않게 함
                for entry in data:
                    if "sort_key" not in entry:
                        entry["sort_key"] = f"{entry.get('date', '2026-05-14')} {entry.get('start', '00:00')}"
                return data
            except:
                return []
    return []

def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

entries = load_data()

# 3. 사이드바 입력 (생략 - 기존과 동일)
# ... (중략) ...

# 4. 메인 화면 분석 및 필터링
if entries:
    df = pd.DataFrame(entries)
    # [해결] 이제 KeyError 없이 시간 순서대로 정렬됩니다.
    df = df.sort_values(by="sort_key")

    # 교수님께서 요청하신 그래프 전용 제목
    st.subheader("📊 활동 시각별 마음의 변화")
    
    fig = px.line(df, x="display_time", y=["mood", "achievement"], 
                  markers=True, 
                  hover_data={"sub_activity": True},
                  labels={"value": "점수", "display_time": "활동 시각", "variable": "항목"})
    fig.update_yaxes(range=[0.5, 5.5])
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    # [복구] 사라졌던 필터링 장치와 리스트 섹션
    st.subheader("🔍 다차원 데이터 필터링")
    c1, c2, c3, c4 = st.columns(4)
    with c1: f_cat = st.multiselect("활동 종류", df['category'].unique())
    with c2: f_day = st.multiselect("요일 선택", ['월', '화', '수', '목', '금', '토', '일'])
    with c3: f_mood = st.multiselect("기분 수준", [1, 2, 3, 4, 5])
    with c4: f_ach = st.multiselect("성취감 수준", [1, 2, 3, 4, 5])

    # 필터링 로직 적용
    f_df = df.copy()
    if f_cat: f_df = f_df[f_df['category'].isin(f_cat)]
    if f_day: f_df = f_df[f_df['day_of_week'].isin(f_day)]
    if f_mood: f_df = f_df[f_df['mood'].isin(f_mood)]
    if f_ach: f_df = f_df[f_df['achievement'].isin(f_ach)]

    st.write(f"결과: {len(f_df)}건의 기록이 있습니다.")

    # 상세 기록 리스트 출력
    for i, row in f_df.iloc[::-1].iterrows(): # 최신순 출력
        with st.expander(f"[{row['date']}({row.get('day_of_week', '-')})] {row['start']}~{row['end']} | {row['category']} - {row['sub_activity']}"):
            st.write(f"**기분:** {row['mood']} / **성취감:** {row['achievement']}")
            st.write(f"**메모:** {row['notes']}")
            if st.button("삭제", key=f"del_{row['id']}"):
                entries = [e for e in entries if e['id'] != row['id']]
                save_data(entries)
                st.rerun()
else:
    st.info("데이터를 입력하면 시간 순으로 정렬된 그래프와 필터링 도구가 나타납니다.")
