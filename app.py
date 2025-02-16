import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Функция для загрузки данных из Google Sheets
def load_data_from_gsheets(sheet_url):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url).sheet1  # Открываем первую страницу
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки из Google Sheets: {e}")
        return None

# Интерфейс приложения
st.title("Анализ динамики стоимости актива")

# Кнопка для загрузки данных из Google Sheets
sheet_url = st.text_input("Введите ссылку на Google Sheets")
if st.button("Загрузить данные из Google Sheets"):
    if sheet_url:
        data = load_data_from_gsheets(sheet_url)
        if data is not None:
            st.write("## Данные из Google Sheets")
            st.write(data.head())
        else:
            st.error("Не удалось загрузить данные. Проверьте ссылку и права доступа.")
    else:
        st.error("Введите ссылку на Google Sheets!")

# Загрузка данных вручную через файл
uploaded_file = st.file_uploader("Загрузите Excel или CSV", type=["xlsx", "csv"])
if uploaded_file:
    data = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    st.write("## Данные из файла")
    st.write(data.head())
