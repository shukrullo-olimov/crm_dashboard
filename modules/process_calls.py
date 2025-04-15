import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

def process_calls(data):
    st.header("Анализ данных Calls")

    # Преобразование значений в Scheduled in CRM
    data['Scheduled in CRM'] = data['Scheduled in CRM'].map({0: False, 1: True})
    
    # Уникальные фильтры для Calls
    st.sidebar.header("Фильтры для Calls")

    # Фильтр для категорий: любые категориальные поля, исключая "Call Start Time"
    category_column = st.sidebar.selectbox(
        "Выберите категориальную колонку", 
        [None] + [col for col in data.select_dtypes(include='object').columns if col != "Call Start Time"], 
        format_func=lambda x: "Выберите колонку" if x is None else x
    )

    # Фильтр для даты: только колонки с "time" или "date"
    date_column = st.sidebar.selectbox(
        "Выберите колонку с датами", 
        [None] + [col for col in data.columns if any(keyword in col.lower() for keyword in ["time", "date"])],
        format_func=lambda x: "Выберите колонку" if x is None else x
    )

    # Отображение данных
    st.subheader("📊 Данные и описательная статистика")
    st.dataframe(data.head())

    # Описательная статистика
    st.subheader("Описательная статистика")
    descriptive_stats = data.describe(include='all')
    
    # Исключаем поля ID и Call Duration (in seconds)
    exclude_columns = ["id", "contactid", "call duration (in seconds)"]
    descriptive_stats = descriptive_stats.drop(
        columns=[col for col in descriptive_stats.columns if col.lower() in exclude_columns], 
        errors='ignore'
    )
    rows_to_keep = ["count", "unique", "top", "freq"]
    st.dataframe(descriptive_stats.loc[rows_to_keep])

    # Сводная статистика для числового поля "Call Duration (in seconds)"
    if "Call Duration (in seconds)" in data.columns:
        st.subheader("Сводная статистика для `Call Duration (in seconds)`")

        # Вычисления
        call_duration = data["Call Duration (in seconds)"].dropna()
        mean_val = call_duration.mean()
        median_val = call_duration.median()
        mode_val = call_duration.mode().iloc[0]
        # # Обработка мода с учётом возможных изменений в scipy.stats.mode
        # mode_result = stats.mode(call_duration, keepdims=True)  # Обработка в безопасном режиме
        # mode_val = mode_result.mode[0] if mode_result.mode.size > 0 else None

        range_val = call_duration.max() - call_duration.min() # if not call_duration.empty else None

        # Вывод результатов
        st.write(
            f"""
            - **Среднее значение:** {mean_val:.2f}  
            - **Медиана:** {median_val:.2f}  
            - **Мода:** {mode_val}  
            - **Диапазон:** {range_val:.2f}  
            """
        )

    
    # Основной блок визуализации категорий
    st.subheader("📈 Визуализация категорий")
    if category_column:
        # Радиокнопка для включения/исключения NaN
        include_nan = st.radio(
            "Включить значения NaN?",
            options=["Без NaN", "С NaN"],
            index=0,  # По умолчанию — без NaN
            horizontal=True
        )
    
        # Подготовка данных
        category_data = data[category_column].copy()
        if include_nan == "С NaN":
            category_data = category_data.fillna("NaN")  # Заменяем NaN на строку "NaN"
        else:
            category_data = category_data.dropna()  # Убираем NaN
    
        # Получаем данные для графика
        category_counts = category_data.value_counts()
    
        # Проверка на пустые данные
        if category_counts.empty:
            st.warning(f"Колонка '{category_column}' не содержит данных для визуализации.")
        else:
            # Выбор типа графика
            chart_type = st.radio(
                "Выберите тип графика для категорий",
                options=["BarH", "BarV", "Pie"],
                index=0,  # По умолчанию выбран BarH
                horizontal=True
            )
    
            # Построение графика
            if chart_type == "BarH":
                fig_category = go.Figure(
                    go.Bar(
                        x=category_counts.values,
                        y=category_counts.index,
                        orientation="h",
                        marker=dict(color="royalblue"),
                        text=category_counts.values,  # Значения для отображения
                        textposition="outside"  # Автоматическое позиционирование текста
                    )
                )
    
                # Настройки оформления
                fig_category.update_layout(
                    title=f"Распределение {category_column}",
                    xaxis=dict(title="Количество", tickfont=dict(size=10)),
                    yaxis=dict(title="Категории", tickfont=dict(size=10), autorange="reversed"),  # Инверсия оси Y
                    plot_bgcolor="white"
                )
    
            elif chart_type == "BarV":
                fig_category = go.Figure(
                    go.Bar(
                        x=category_counts.index,
                        y=category_counts.values,
                        marker=dict(color="royalblue"),
                        text=category_counts.values,  # Значения для отображения
                        textposition="outside"  # Автоматическое позиционирование текста
                    )
                )
    
                # Настройки оформления
                fig_category.update_layout(
                    title=f"Распределение {category_column}",
                    xaxis=dict(title="Категории", tickfont=dict(size=10)),
                    yaxis=dict(title="Количество", tickfont=dict(size=10)),
                    plot_bgcolor="white"
                )
    
            elif chart_type == "Pie":
                fig_category = px.pie(
                    category_counts,
                    values=category_counts.values,
                    names=category_counts.index,
                    title=f"Распределение {category_column}",
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
    
            # Отображение графика
            st.plotly_chart(fig_category)
    else:
        st.write("Выберите категорию с левой панели")

    

    # Анализ временных рядов
    st.subheader("📉 Анализ временных рядов")
    
    if date_column:
        # Преобразование даты в формат datetime
        data[date_column] = pd.to_datetime(data[date_column])
        
        # Радио-кнопка для выбора агрегации
        aggregation_level = st.radio(
            "Выберите уровень агрегации",
            options=["Месяц", "Неделя", "День"],
            index=0,  # По умолчанию "Месяц"
            horizontal=True
        )
        
        # Агрегация данных
        if aggregation_level == "День":
            time_series = data.groupby(data[date_column].dt.date).size()
            title = "Ежедневный тренд звонков"
            show_markers = False  # Маркеры не нужны для ежедневного графика
        elif aggregation_level == "Неделя":
            time_series = data.groupby(data[date_column].dt.to_period("W")).size()
            title = "Еженедельный тренд звонков"
            show_markers = False  # Маркеры не нужны для еженедельного графика
        else:  # "Месяц"
            time_series = data.groupby(data[date_column].dt.to_period("M")).size()
            title = "Ежемесячный тренд звонков"
            show_markers = True  # Добавляем маркеры для ежемесячного графика
        
        # Построение графика
        fig_time = px.line(
            x=time_series.index.astype(str),  # Преобразование для Plotly
            y=time_series.values,
            title=title,
            labels={"x": "Дата", "y": "Количество звонков"},
            markers=show_markers  # Включаем маркеры для ежемесячного графика
        )
        
        # Настройка высоты графика
        fig_time.update_layout(height=500)
        
        # Добавляем подписи значений только для ежемесячного графика
        if aggregation_level == "Месяц":
            fig_time.update_traces(
                text=time_series.values,  # Значения для подписей
                textposition="top center",  # Позиция подписи
                mode="lines+markers+text"  # Линии, маркеры и подписи
            )
        if aggregation_level == "Неделя":
            fig_time.update_traces(
                mode="lines+markers"  # Линии, маркеры
            )
            fig_time.update_layout(
                xaxis=dict(tickangle=45)  # Угол наклона подписей оси X
            )
        
        st.plotly_chart(fig_time)
    else:
        st.write("Выберите колонку с датами с левой панели")


    
    
