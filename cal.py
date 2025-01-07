import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets 인증 설정
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "qcells schedule"

# Google Sheets 인증
credentials = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
client = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_dict(
        credentials,
        SCOPE
    )
)

# Google Sheet에 연결
try:
    sheet = client.open(SPREADSHEET_NAME).sheet1
except Exception as e:
    st.error(f"Google Sheet 연결 실패: {e}")

# Google Sheet에서 데이터 읽기
def load_data():
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

# Google Sheet에 데이터 추가
def add_data(name, start_date, end_date, description):
    try:
        sheet.append_row([name, start_date, end_date, description])
    except Exception as e:
        st.error(f"데이터 추가 실패: {e}")

# 앱 제목
st.title("사내 휴가 공유 웹 앱")

# 휴가 추가 폼
st.header("휴가 등록하기")
with st.form("vacation_form"):
    name = st.text_input("이름을 입력하세요")
    start_date = st.date_input("휴가 시작 날짜")
    start_time = st.time_input("휴가 시작 시간")
    end_date = st.date_input("휴가 끝나는 날짜")
    end_time = st.time_input("휴가 끝나는 시간")
    description = st.text_area("휴가 설명 (선택 사항)")
    submit_button = st.form_submit_button("휴가 추가")

    if submit_button:
        start_datetime = datetime.combine(start_date, start_time).isoformat()
        end_datetime = datetime.combine(end_date, end_time).isoformat()
        if start_datetime > end_datetime:
            st.error("시작 날짜/시간이 종료 날짜/시간보다 늦을 수 없습니다.")
        else:
            add_data(name, start_datetime, end_datetime, description)
            st.success("휴가가 성공적으로 추가되었습니다!")

# 데이터 로드
st.header("휴가 캘린더")
data = load_data()
if not data.empty:
    calendar_events = [
        {
            "title": row["name"],
            "start": row["start_date"],
            "end": row["end_date"],
            "description": row["description"]
        }
        for _, row in data.iterrows()
    ]
else:
    calendar_events = []

# 캘린더 옵션
calendar_options = {
    "editable": False,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "initialView": "dayGridMonth"
}

calendar_response = calendar(events=calendar_events, options=calendar_options)
st.write("캘린더 상호작용:", calendar_response)
