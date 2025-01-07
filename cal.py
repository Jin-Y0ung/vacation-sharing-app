import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets 인증 설정
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "qcells schedule"  # 사용할 Google Sheet 이름

credentials = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]

# Google Sheets 인증
client = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_dict(
        dict(credentials),
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

def delete_data(index):
    sheet.delete_row(index + 2)

# 앱 제목
st.title("Qcells DP Team Time Off Schedule")

# 휴가 추가 폼
st.header("Add Time Off")
with st.form("vacation_form"):
    name = st.text_input("Name")
    start_date = st.date_input("Start Date of Time Off")
    start_time = st.time_input("Start Time of Time Off")
    end_date = st.date_input("End Date of Time Off")
    end_time = st.time_input("End Time of Time Off")
    description = st.text_area("Description (Optional)")
    submit_button = st.form_submit_button("Add your time off")

    if submit_button:
        start_datetime = datetime.combine(start_date, start_time).isoformat()
        end_datetime = datetime.combine(end_date, end_time).isoformat()
        if start_datetime > end_datetime:
            st.error("Start date/time cannot be later than the end date/time.")
        else:
            add_data(name, start_datetime, end_datetime, description)
            st.success("Added successfully!")

# 데이터 로드
st.header("Calander")
data = load_data()

if not data.empty:
    try:
        calendar_events = [
            {
                "title": row["name"],
                "start": datetime.fromisoformat(row["start_date"]).isoformat(),
                "end": datetime.fromisoformat(row["end_date"]).isoformat(),
                "description": row["description"]
            }
            for _, row in data.iterrows()
        ]
    except KeyError as e:
        st.error(f"Keyerror {e}")
        calendar_events = []
    except Exception as e:
        st.error(f"Data Error {e}")
        calendar_events = []
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

st.markdown(
    "[View or Modify the schedule in Google Sheets](https://docs.google.com/spreadsheets/d/16SKKKKYU-z9il5GILvPV3uyjQRbNSvipOuLMyUD6XkI/edit?usp=sharing)"
)
