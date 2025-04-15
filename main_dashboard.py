import streamlit as st
import pandas as pd

# Импорт модулей для обработки данных
from modules.process_contacts import process_contacts
from modules.process_calls import process_calls
from modules.process_spend import process_spend
from modules.process_deals import process_deals

# Заголовок приложения
st.title("Дашборд аналитики CRM: Метрики и тренды")

# Загрузка данных
st.sidebar.header("Загрузка данных")
uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type=["csv"])

if uploaded_file is not None:
    # Чтение данных
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("Данные успешно загружены!")

    # Проверка имени датасета и вызов соответствующего модуля
    if "cont" in uploaded_file.name.lower():
        process_contacts(data)
    elif "calls" in uploaded_file.name.lower():
        process_calls(data)
    elif "spend" in uploaded_file.name.lower():
        process_spend(data)
    elif "deals" in uploaded_file.name.lower():
        process_deals(data)
    else:
        st.error("Неизвестный тип данных. Убедитесь, что название файла содержит 'contacts', 'calls', 'spend' или 'deals'.")

else:
    st.warning("Загрузите файл, чтобы начать анализ!")
