import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 페이지 설정
st.set_page_config(page_title="하루로그 (Mood Tracker)", layout="wide")

# 데이터 파일 경로
DATA_FILE = "tracker_data.json"

# 기본 옵션 설정
MOOD_OPTIONS = ["1 - 매우 나쁨", "2 - 나쁨", "3 - 보통", "4 - 좋음", "5 - 매우 좋음"]
CATEGORIES = ["업무/학업", "식사", "휴식", "운동", "사람 만남", "자기계발", "기타"]
ACHIEVEMENT_OPTIONS = ["1 - 전혀 없음", "2 - 낮음", "3 - 보통", "4 - 높음", "5 - 매우 좋음"]

# 데이터 로드/저장 함수
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

# 메인 화면 구성
st.title("🌟 하루로그: 기분 & 성취감 트래커")
st.markdown("오늘의 활동과 기분을 기록하고 나만의 패턴을 찾아보세요.")

entries = load_data()

# 사이드바 - 기록하기
with st.sidebar:
    st.header("📝 새 활동 기록")
    cat = st.selectbox("카테고리", CATEGORIES)
    detail = st.text_input("세부 활동 (선택 사항)")
    mood = st.select_slider("오늘의 기분", options=[1, 2, 3, 4, 5], value=3, 
                            format_func=lambda x: MOOD_OPTIONS[x-1])
    ach = st.select_slider("오늘의 성취감", options=[1, 2, 3, 4, 5], value=3,
                           format_func=lambda x: ACHIEVEMENT_OPTIONS[x-1])
    notes = st.text_area("메모")
    
    if st.button("기록 저장하기"):
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": cat,
            "detail": detail,
            "activity": f"[{cat}] {detail}" if detail else f"[{cat}]",
            "mood": mood,
            "mood_label": MOOD_OPTIONS[mood - 1].split(" - ")[1],
            "achievement": ach,
            "achievement_label": ACHIEVEMENT_OPTIONS[ach - 1].split(" - ")[1],
            "notes": notes
        }
        entries.append(new_entry)
        save_data(entries)
        st.success("기록이 저장되었습니다!")
        st.rerun()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 통계 및 그래프", "📜 전체 기록", "⚙️ 관리"])

with tab1:
    if entries:
        df = pd.DataFrame(entries)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 기록 수", f"{len(df)}개")
            st.metric("평균 기분 점수", f"{df['mood'].mean():.1f} / 5.0")
        with col2:
            st.metric("평균 성취감 점수", f"{df['achievement'].mean():.1f} / 5.0")
        
        # 기분 변화 그래프
        st.subheader("기분 및 성취감 추이")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['timestamp'], df['mood'], marker='o', label='기분', color='#3498db')
        ax.plot(df['timestamp'], df['achievement'], marker='s', label='성취감', color='#2ecc71')
        ax.set_ylim(0.5, 5.5)
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(fig)
        
        # 카테고리별 분석
        st.subheader("카테고리별 평균 기분")
        cat_avg = df.groupby('category')['mood'].mean().sort_values()
        st.bar_chart(cat_avg)
    else:
        st.info("아직 기록이 없습니다. 사이드바에서 첫 기록을 남겨보세요!")

with tab2:
    if entries:
        for e in reversed(entries):
            with st.expander(f"{e['timestamp']} - {e['activity']} (기분: {e['mood']})"):
                st.write(f"**성취감:** {e['achievement_label']}")
                st.write(f"**메모:** {e['notes'] if e['notes'] else '없음'}")
    else:
        st.write("표시할 기록이 없습니다.")

with tab3:
    if st.button("데이터 CSV로 다운로드"):
        df = pd.DataFrame(entries)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("CSV 파일 받기", csv, "mood_data.csv", "text/csv")
    
    if st.button("⚠️ 모든 기록 삭제", help="주의! 복구할 수 없습니다."):
        if st.checkbox("정말로 삭제하시겠습니까?"):
            save_data([])
            st.warning("모든 데이터가 삭제되었습니다.")
            st.rerun()