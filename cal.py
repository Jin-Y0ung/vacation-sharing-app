import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime
import dateutil.parser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets 인증 설정
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "qcells schedule"  # 사용할 Google Sheet 이름

# Streamlit secrets 사용
credentials = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]

# Google Sheets 인증
client = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_dict(
        credentials,
        SCOPE
    )
)

# Google Sheet에 연결
sheet = client.open(SPREADSHEET_NAME).sheet1

# Google Sheet에서 데이터 읽기
def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Google Sheet에 데이터 추가
def add_data(name, start_date, end_date, description):
    sheet.append_row([name, start_date, end_date, description])

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
        # 날짜와 시간을 결합하여 ISO 8601 형식으로 저장
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

# 캘린더 이벤트 변환
calendar_events = []
if not data.empty:
    for _, row in data.iterrows():
        try:
            start = dateutil.parser.isoparse(row["start_date"]).isoformat()
            end = dateutil.parser.isoparse(row["end_date"]).isoformat()
            calendar_events.append({
                "title": row["name"],
                "start": start,
                "end": end,
                "description": row.get("description", "")
            })
        except Exception as e:
            st.error(f"캘린더 이벤트 변환 중 오류: {e}")

# 디버깅용 데이터 출력
st.write("캘린더 이벤트 데이터:", calendar_events)

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

# 캘린더 렌더링
calendar_response = calendar(events=calendar_events, options=calendar_options)
st.write("캘린더 상호작용:", calendar_response)
