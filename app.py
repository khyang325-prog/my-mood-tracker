import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, time
import plotly.express as px

# 1. 페이지 설정 및 제목 수정
st.set_page_config(page_title="하루로그", layout="wide")
st.markdown("<h2 style='font-size: 24px; margin-bottom: 5px;'>🌷 하루로그 v1.0 <span style='font-size: 14px; color: gray; font-weight: normal;'>by 그냥쌤</span></h2>", unsafe_allow_html=True)

# 2. 교수님의 세분화된 격려 메시지 (완벽 이식)
REFLECTION_MESSAGES = {
    ("high", "high"): ["기분도 좋고 성취감도 높은 활동이었네요. 이런 순간을 잘 기억해 두세요.", "에너지가 넘쳤던 활동이었네요. 스스로를 충분히 칭찬해도 좋습니다."],
    ("high", "mid"): ["기분 좋게 활동을 마쳤군요. 꾸준히 이어가다 보면 성취감도 자연스럽게 따라올 거예요.", "이 활동이 즐거웠다면 그것만으로도 충분해요."],
    ("high", "low"): ["마음 편하게 쉬어가는 시간이었군요. 가끔은 그런 여유도 필요합니다.", "부담 없이 즐긴 활동이었군요. 그런 여백이 있어야 더 잘 달릴 수 있어요."],
    ("mid", "high"): ["기분은 평소와 비슷했지만 활동에서 뿌듯함을 느꼈군요. 그 성취감을 소중히 여겨 보세요.", "묵묵히 해냈군요. 감정과 무관하게 무언가를 이뤄낸 스스로를 인정해 주세요."],
    ("mid", "mid"): ["무난한 활동이었군요. 평범함이 쌓여 큰 변화를 만듭니다.", "특별하지 않아도 괜찮아요. 꾸준함이 가장 강한 힘입니다."],
    ("mid", "low"): ["가볍게 지나간 시간이었군요. 더 집중해 볼 기회가 있을 거예요.", "쉬어가는 시간도 필요해요. 이번이 그런 시간이었을 수 있습니다."],
    ("low", "high"): ["기분이 조금 가라앉아 있었지만, 그 안에서도 의미 있는 일을 해냈군요. 정말 대단합니다.", "마음은 무거웠지만 성취감을 느낀 활동이었군요."],
    ("low", "mid"): ["기분이 조금 가라앉은 시간에도 활동을 이어갔군요. 그것만으로도 충분합니다.", "힘든 때에도 기록을 남긴 자신을 격려해 주세요."],
    ("low", "low"): ["몸도 마음도 조금 지쳐있는 시간이었군요. 충분히 쉬고 다음을 기대해 보세요.", "기분도 성취감도 낮은 시간이었지만, 기록으로 남긴 것 자체가 다음을 위한 발걸음이에요."]
}

def get_bucket(score):
    if score >= 4: return "high"
    elif score >= 2: return "mid"
    else: return "low"

# 3. 데이터 로드/저장 (KeyError 방어 로직 추가)
DATA_FILE = "tracker_data_v3.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # 하위 호환성 유지: user_id나 sort_key가 없는 과거 데이터 보정
                for entry in data:
                    if "user_id" not in entry: entry["user_id"] = "unknown"
                    if "sort_key" not in entry:
                        entry["sort_key"] = f"{entry.get('date', '2026-05-15')} {entry.get('start', '00:00')}"
                return data
            except: return []
    return []

def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

entries = load_data()

# 4. 사이드바: 사용자 확인 및 기록 입력
with st.sidebar:
    st.header("👤 사용자 확인")
    user_id = st.text_input("학번 또는 ID를 입력하세요", placeholder="예: 20260123")
    
    if not user_id:
        st.info("💡 왼쪽 칸에 ID를 입력하시면 기록을 시작할 수 있습니다.")
        st.stop()

    st.divider()
    st.header("📝 오늘의 활동 기록")
    record_date = st.date_input("활동 날짜", datetime.now())
    col1, col2 = st.columns(2)
    with col1: start_t = st.time_input("시작 시각", time(9, 0))
    with col2: end_t = st.time_input("종료 시각", time(10, 0))
    
    category = st.selectbox("대분류", [
        "🏠 일상생활", 
        "✍️ 업무/공부", 
        "🏃 신체활동/운동", 
        "🍱 식사/휴식", 
        "🎨 취미/여가", 
        "🤝 만남/소통", 
        "✨ 기타"
    ])
    sub_activity = st.text_input("세부 활동 명")
    
    st.divider()
    mood = st.slider("🔴 기분 점수", 1, 5, 3)
    ach = st.slider("🔵 성취감 점수", 1, 5, 3)
    notes = st.text_area("메모/느낀 점")
    
    if st.button("기록 저장 및 분석"):
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        activity_dt = datetime.combine(record_date, start_t)
        
        # 교수님의 세분화된 코멘트 로직 실행
        m_bucket, a_bucket = get_bucket(mood), get_bucket(ach)
        reflection = random.choice(REFLECTION_MESSAGES.get((m_bucket, a_bucket), ["오늘도 수고하셨습니다."]))
        
        new_entry = {
            "user_id": user_id,
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

# 5. 메인 화면: 시각화 및 필터링
if entries:
    df = pd.DataFrame(entries)
    # 입력한 ID의 데이터만 필터링
    my_df = df[df['user_id'] == user_id].sort_values(by="sort_key")

    if not my_df.empty:
        st.markdown(f"### 🍀 {user_id}님의 마음지도  \n<sub style='font-size: 16px; color: #555555; font-weight: normal;'>(기분 & 성취감)</sub>", unsafe_allow_html=True)
        
        fig = px.line(my_df, x="display_time", y=["mood", "achievement"], 
                      markers=True, 
                      hover_data={"sub_activity": True},
                      labels={"value": "점수", "display_time": "활동 시각", "variable": "항목"},
                      # 교수님 제안 반영: 기분(mood)은 빨간색, 성취감(achievement)은 파란색
                      color_discrete_map={"mood": "#EF553B", "achievement": "#636EFA"})
        
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(range=[0.5, 5.5])
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("🔍 내 기록 찾아보기")
        c1, c2, c3, c4 = st.columns(4)
        with c1: f_cat = st.multiselect("활동 종류", my_df['category'].unique())
        with c2: f_day = st.multiselect("요일 선택", ['월', '화', '수', '목', '금', '토', '일'])
        with c3: f_mood = st.multiselect("기분 수준", [1, 2, 3, 4, 5])
        with c4: f_ach = st.multiselect("성취감 수준", [1, 2, 3, 4, 5])

        f_df = my_df.copy()
        if f_cat: f_df = f_df[f_df['category'].isin(f_cat)]
        if f_day: f_df = f_df[f_df['day_of_week'].isin(f_day)]
        if f_mood: f_df = f_df[f_df['mood'].isin(f_mood)]
        if f_ach: f_df = f_df[f_df['achievement'].isin(f_ach)]

        st.write(f"결과: {len(f_df)}건의 기록이 있습니다.")

        for _, row in f_df.iloc[::-1].iterrows():
            with st.expander(f"[{row['date']}({row.get('day_of_week', '-')})] {row['start']}~{row['end']} | {row['category']} - {row['sub_activity']}"):
                st.write(f"**기분:** {row['mood']} / **성취감:** {row['achievement']}")
                st.write(f"**메모:** {row['notes']}")
                # 교수님의 따뜻한 성찰 메시지 출력
                st.info(f"💡 {row.get('reflection', '오늘도 수고하셨습니다.')}")
                if st.button("삭제", key=f"del_{row['id']}"):
                    entries = [e for e in entries if e['id'] != row['id']]
                    save_data(entries)
                    st.rerun()
    else:
        st.info(f"'{user_id}'님으로 등록된 기록이 없습니다. 왼쪽에서 첫 기록을 남겨보세요!")
else:
        st.info("왼쪽 사이드바에서 오늘 첫 활동을 기록해 보세요!")

st.divider()
with st.expander("📊 관리자용 데이터 전체 백업"):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data_str = f.read()
            st.download_button(
                label="📥 전체 기록 다운로드 (JSON)",
                data=data_str,
                file_name="mood_tracker_backup.json",
                mime="application/json"
            )
    else:
        st.info("아직 저장된 데이터 파일이 없습니다.")
