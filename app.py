import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, time
import plotly.express as px

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="하루로그", layout="wide")

# 교수님이 요청하신 제목으로 변경
st.title("🌟 하루로그: 활동 별 기분과 성취감 기록하기")

# 2. 교수님의 격려 메시지 딕셔너리
REFLECTION_MESSAGES = {
    ("high", "high"): [
        "오늘은 기분도 좋고 성취감도 높은 날이었네요. 이런 순간을 잘 기억해 두세요.",
        "에너지가 넘쳤던 하루였군요. 스스로를 충분히 칭찬해도 좋습니다.",
        "기분과 성취감이 모두 빛나는 날이었어요. 오늘의 흐름을 내일도 이어가 보세요.",
    ],
    ("high", "mid"): [
        "기분 좋게 활동을 마쳤군요. 꾸준히 이어가다 보면 성취감도 자연스럽게 따라올 거예요.",
        "오늘 활동이 즐거웠다면 그것만으로도 충분해요.",
        "기분이 좋은 날은 작은 일도 더 빛나 보이죠. 오늘을 잘 보냈습니다.",
    ],
    ("high", "low"): [
        "오늘은 마음 편하게 쉬어가는 시간이었군요. 가끔은 그런 여유도 꼭 필요합니다.",
        "기분 좋게 가볍게 보낸 시간이에요. 충전의 시간이었을 수 있습니다.",
        "부담 없이 즐긴 활동이었군요. 그런 여백이 있어야 더 잘 달릴 수 있어요.",
    ],
    ("mid", "high"): [
        "기분은 평소와 비슷했지만 활동에서 뿌듯함을 느꼈군요. 그 성취감을 소중히 여겨 보세요.",
        "묵묵히 해낸 날이에요. 감정과 무관하게 무언가를 이뤄낸 스스로를 인정해 주세요.",
        "마음이 무거워도 해낸 일에는 의미가 있어요. 잘 하셨습니다.",
    ],
    ("mid", "mid"): [
        "오늘은 무난하게 흘러간 하루였군요. 평범한 하루가 쌓여 큰 변화를 만듭니다.",
        "특별하지 않아도 괜찮아요. 꾸준함이 가장 강한 힘입니다.",
        "잔잔한 하루였어요. 오늘도 기록해 줘서 고마워요.",
    ],
    ("mid", "low"): [
        "오늘은 가볍게 지나간 시간이었군요. 내일 더 집중해 볼 기회가 있을 거예요.",
        "쉬어가는 날도 필요해요. 오늘은 그런 날이었을 수 있습니다.",
        "활동이 가볍게 느껴졌더라도, 기록하는 습관 자체가 이미 가치 있어요.",
    ],
    ("low", "high"): [
        "기분이 조금 가라앉아 있었지만, 그 안에서도 의미 있는 일을 해냈군요. 정말 대단합니다.",
        "마음이 무거운 날에도 성취감을 느낀 활동이었군요. 스스로에게 수고했다고 말해 주세요.",
        "기분이 조금 가라앉았지만 활동 자체는 보람이 있었네요. 그 힘이 오늘을 버티게 해줬을 그려요.",
    ],
    ("low", "mid"): [
        "기분이 조금 가라앉은 날이었지만 그래도 활동을 이어갔군요. 그것만으로도 충분합니다.",
        "힘든 날에도 기록을 남긴 자신을 격려해 주세요.",
        "쉽지 않은 하루였을 텐데 잘 버텨 주었어요.",
    ],
    ("low", "low"): [
        "오늘은 몸도 마음도 조금 지쳐있는 날이었군요. 충분히 쉬고 내일을 기대해 보세요.",
        "누구에게나 그런 날이 있어요. 오늘 하루도 지나갈 거예요. 수고했습니다.",
        "기분도 성취감도 낮은 날이지만, 기록으로 남긴 것 자체가 내일을 위한 발걸음이에요.",
    ],
}

def get_bucket(score):
    if score >= 4: return "high"
    elif score >= 2: return "mid"
    else: return "low"

# 3. 데이터 로드/저장 함수
DATA_FILE = "tracker_data_v2.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

entries = load_data()

# 4. 사이드바 입력창 (기능 강화)
with st.sidebar:
    st.header("📝 활동 기록")
    
    # 시간 입력
    col1, col2 = st.columns(2)
    with col1:
        start_t = st.time_input("시작 시각", time(9, 0))
    with col2:
        end_t = st.time_input("종료 시각", time(10, 0))
    
    category = st.selectbox("대분류", ["업무/연구", "강의/상담", "운동", "식사/휴식", "자기계발", "기타"])
    sub_activity = st.text_input("세부 활동 (예: 논문 읽기)")
    
    st.divider()
    
    mood = st.slider("기분 점수", 1, 5, 3)
    ach = st.slider("성취감 점수", 1, 5, 3)
    notes = st.text_area("추가 메모")
    
    if st.button("기록 저장 및 분석"):
        # 점수에 따른 멘트 선정
        m_bucket = get_bucket(mood)
        a_bucket = get_bucket(ach)
        reflection = random.choice(REFLECTION_MESSAGES[(m_bucket, a_bucket)])
        
        new_entry = {
            "id": datetime.now().timestamp(),
            "date": datetime.now().strftime("%Y-%m-%d"),
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
        
        # 동기 강화 멘트 출력
        st.balloons()
        st.info(f"✨ {reflection}")
        st.success("데이터가 안전하게 저장되었습니다.")
        st.rerun()

# 5. 메인 화면 - 분석 및 필터링
if entries:
    df = pd.DataFrame(entries)
    
    # 그래프 시각화
    st.subheader("📊 기분 및 성취감 변화 추이")
    fig = px.line(df, x="date", y=["mood", "achievement"], markers=True,
                  labels={"value": "점수", "date": "날짜", "variable": "항목"})
    st.plotly_chart(fig, use_container_width=True)
    
    # 필터링 기능
    st.divider()
    st.subheader("🔍 기록 찾아보기")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        sel_cat = st.multiselect("카테고리 선택", df['category'].unique())
    with f_col2:
        min_mood = st.number_input("최소 기분 점수", 1, 5, 1)
    
    filtered_df = df.copy()
    if sel_cat:
        filtered_df = filtered_df[filtered_df['category'].isin(sel_cat)]
    filtered_df = filtered_df[filtered_df['mood'] >= min_mood]
    
    st.write(f"검색 결과: {len(filtered_df)}건")
    
    # 수정 및 삭제 기능이 포함된 목록
    for i, row in filtered_df.iloc[::-1].iterrows():
        with st.expander(f"[{row['date']}] {row['start']}~{row['end']} | {row['category']}: {row['sub_activity']}"):
            st.write(f"**기분:** {row['mood']} | **성취감:** {row['achievement']}")
            st.write(f"**메모:** {row['notes']}")
            st.caption(f"💭 {row['reflection']}")
            
            # 삭제 버튼 (간이 구현)
            if st.button(f"삭제하기", key=f"del_{row['id']}"):
                entries = [e for e in entries if e['id'] != row['id']]
                save_data(entries)
                st.rerun()
else:
    st.info("아직 기록이 없습니다. 왼쪽 사이드바에서 오늘 첫 활동을 기록해 보세요!")
