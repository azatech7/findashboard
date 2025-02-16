try:
    import streamlit as st
    import pandas as pd
    import plotly.express as px
except ModuleNotFoundError as e:
    print("Ошибка: Не установлен модуль Streamlit. Попробуйте выполнить: pip install streamlit pandas plotly")
    raise e

# Функция загрузки и обработки данных
def load_data(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        df = df.fillna(method='ffill').fillna(method='bfill')  # Интерполяция пропущенных значений
        date_col, value_col = df.columns[:2]  # Первые две колонки - даты и котировки
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df.dropna(subset=[date_col, value_col], inplace=True)  # Удаляем некорректные даты
        df = df.sort_values(by=date_col)
        df['% Change'] = (df[value_col] / df[value_col].iloc[0]) * 100
        return df, date_col, value_col
    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")
        return None, None, None

# Интерфейс приложения
st.title("Анализ динамики стоимости актива")

uploaded_file = st.file_uploader("Загрузите Excel или CSV", type=["xlsx", "csv"])

if uploaded_file:
    data, date_col, value_col = load_data(uploaded_file)
    if data is not None:
        st.write("## Данные")
        st.write(data.head())
        
        # Выбор типа графика
        chart_type = st.radio("Выберите тип графика", ["Абсолютные значения", "Процентные изменения"])
        
        fig = px.line(data, x=date_col, y=value_col if chart_type == "Абсолютные значения" else "% Change",
                      title=f"{chart_type} стоимости актива")
        st.plotly_chart(fig)
        
        # Рассчет изменений
        def calc_change(df, value_col, periods):
            changes = {}
            last_value = df[value_col].iloc[-1]
            for label, days in periods.items():
                past_date = df.iloc[0][date_col] if days == "first" else df[date_col].max() - pd.Timedelta(days=days)
                past_value = df.loc[df[date_col] <= past_date, value_col].iloc[-1] if not df.loc[df[date_col] <= past_date].empty else None
                changes[label] = ((last_value / past_value) - 1) * 100 if past_value else None
            return changes
        
        periods = {"Неделя": 7, "Месяц": 30, "3 месяца": 90, "Полгода": 180, "Год": 365, "С первой даты": "first"}
        changes = calc_change(data, value_col, periods)
        
        # Отображение таблицы с изменениями
        changes_df = pd.DataFrame([(k, v if v is not None else "Недостаточно данных") for k, v in changes.items()], columns=["Период", "Изменение, %"])
        st.write("## Динамика стоимости актива по периодам")
        st.table(changes_df)
        
        # Скачивание обработанных данных
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("Скачать обработанные данные", data=csv, file_name="processed_data.csv", mime="text/csv")
      
