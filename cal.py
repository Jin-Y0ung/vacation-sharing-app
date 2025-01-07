import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime, timedelta

# 앱 제목
st.title("사내 휴가 공유 웹 앱")

# 휴가 데이터 초기화
if "vacation_data" not in st.session_state:
    st.session_state["vacation_data"] = []

# 휴가 추가 폼
st.header("휴가 등록하기")
with st.form("vacation_form"):
    name = st.text_input("이름을 입력하세요", key="name_input")
    start_date = st.date_input("휴가 시작 날짜를 선택하세요", key="start_date_input")
    start_time = st.time_input("휴가 시작 시간을 선택하세요", key="start_time_input")
    end_date = st.date_input("휴가 끝나는 날짜를 선택하세요", key="end_date_input")
    end_time = st.time_input("휴가 끝나는 시간을 선택하세요", key="end_time_input")
    description = st.text_area("휴가 설명 (선택 사항)", key="description_input")
    submit_button = st.form_submit_button("휴가 추가")

    if submit_button:
        # 입력 데이터 검증
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        if start_datetime > end_datetime:
            st.error("시작 시간이 종료 시간보다 늦을 수 없습니다.")
        elif not name.strip():
            st.error("이름을 입력해주세요.")
        else:
            # 데이터 저장
            st.session_state["vacation_data"].append({
                "title": f"{name}의 휴가",
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat(),
                "description": description
            })
            st.success("휴가가 성공적으로 추가되었습니다!")

# 캘린더 표시
st.header("휴가 캘린더")
calendar_events = st.session_state["vacation_data"]

# streamlit-calendar 옵션
calendar_options = {
    "editable": False,  # 이벤트 편집 비활성화
    "selectable": True,  # 날짜 선택 활성화
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",  # 초기 뷰
    "events": calendar_events,
}

custom_css = """
.fc-event-title {
    font-weight: bold;
    color: #4CAF50;
}
.fc-toolbar-title {
    font-size: 1.5rem;
}
"""

# 캘린더 컴포넌트 추가
calendar_response = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
)

# 사용자의 캘린더 상호작용 확인
st.write("캘린더 상호작용 데이터:", calendar_response)
