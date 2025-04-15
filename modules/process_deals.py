import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from plotly.colors import get_colorscale
from plotly.colors import find_intermediate_color
import streamlit.components.v1 as components

def process_deals(data):
    st.header("Анализ данных Deals")

    # Уникальные фильтры для Deals
    st.sidebar.header("Фильтры для Deals")
    data['SLA'] = pd.to_timedelta(data['SLA'].astype(str))
    
    # Фильтр для категорий: любые категориальные поля, исключая содержащие "time", "date"
    category_column = st.sidebar.selectbox(
        "Выберите категориальную колонку", 
        [None] + [col for col in data.select_dtypes(include='object').columns 
                  if not any(keyword in col.lower() for keyword in ["time", "date"])],
        format_func=lambda x: "Выберите колонку" if x is None else x
    )


    # Фильтр для даты: только колонки с "time" или "date"
    date_column = st.sidebar.selectbox(
        "Выберите колонку с датами", 
        [None] + [col for col in data.columns if any(keyword in col.lower() for keyword in ["time", "date"])],
        format_func=lambda x: "Выберите колонку" if x is None else x
    )


    # # Заголовок
    # st.title("Мой интерактивный дашборд")
    
    # Улучшенная структура: вкладки заменены кнопками
    tab_selected = st.radio(
        "Выберите анализ:",
        options=[
            "📊 Данные и описательная статистика", 
            "📈 Визуализация категорий", 
            "📉 Анализ временных рядов", 
            "📋 Анализ эффективности кампаний и источников",
            "💼 Анализ эффективности работы отдела продаж",
            "💰 Анализ платежей и продуктов",
            "🌍 Географический анализ"
        ],
        horizontal=True
    )


    if tab_selected == "📊 Данные и описательная статистика":
        # Отображение данных
        st.subheader("📊 Данные и описательная статистика")
        st.dataframe(data.head())
    
        # Описательная статистика
        st.subheader("Описательная статистика")
        descriptive_stats = data.describe(include='all')
        
        # Указанные поля для отображения описательной статистики
        categorical_fields = [
            'Quality', 'Stage', 'Source', 'Product', 
            'Payment Type', 'Education Type', 'Lost Reason'
        ]
        
        # Фильтруем только указанные поля для описательной статистики
        descriptive_stats = data[categorical_fields].describe(include='all')
        
        # Выводим описательную статистику
        rows_to_keep = ["count", "unique", "top", "freq"]
        st.dataframe(descriptive_stats.loc[rows_to_keep])
    
    
        # Сводная статистика для исключенных числовых полей
        st.subheader("Сводная статистика для числовых полей")
        st.dataframe(data[['Course duration', 'Months of study', 'Initial Amount Paid', 'Offer Total Amount', 'SLA']].describe().T)

        data['SLA'] = pd.to_timedelta(data['SLA'].astype(str))
        # Фильтрация существующих числовых колонок из exclude_columns
        numerical_fields = ['Course duration', 'Months of study', 'Initial Amount Paid', 'Offer Total Amount']
        
        if not numerical_fields:
            st.warning("Нет числовых полей для анализа среди исключенных.")
        else:
            # Подготовка данных для таблицы
            summary_stats = []
            for field in numerical_fields:
                column_data = data[field].dropna()  # Убираем пропущенные значения
        
                # Вычисления
                mean_val = column_data.mean()
                median_val = column_data.median()
                mode_val = column_data.mode().iloc[0] if not column_data.mode().empty else "Нет моды"
                range_val = column_data.max() - column_data.min()
        
                # Добавляем данные в таблицу
                summary_stats.append({
                    "Поле": field,
                    "Среднее значение": mean_val,
                    "Медиана": median_val,
                    "Мода": mode_val,
                    "Диапазон": range_val
                })
        
            # Преобразуем список словарей в DataFrame
            summary_df = pd.DataFrame(summary_stats)
        
            # Вывод с помощью st.dataframe
            st.dataframe(summary_df.style.format({
                "Среднее значение": "{:.2f}",
                "Медиана": "{:.2f}",
                "Диапазон": "{:.2f}"
            }))



    elif tab_selected == "📈 Визуализация категорий":
        st.subheader("📈 Визуализация категорий")
        if category_column:
            with st.form(key="category_visualization_form"):
                col1, col2 = st.columns(2)
                with col1:
                    include_nan = st.radio(
                        "Включить значения NaN?",
                        options=["Без NaN", "С NaN"],
                        index=0,
                        horizontal=True,
                        key="include_nan_radio"  # Уникальный ключ
                    )
        
                with col2:
                    chart_type = st.radio(
                        "Выберите тип графика для категорий",
                        options=["BarH", "BarV", "Pie"],
                        index=0,
                        horizontal=True,
                        key="chart_type_radio"  # Уникальный ключ
                    )
        
                # Кнопка для подтверждения
                submit_button = st.form_submit_button("Обновить график")
        
            # Обновление только при нажатии на кнопку
            if submit_button:
                category_data = data[category_column].copy()
                if include_nan == "С NaN":
                    category_data = category_data.fillna("NaN")
                else:
                    category_data = category_data.dropna()
        
                category_counts = category_data.value_counts()
                if category_counts.empty:
                    st.warning(f"Колонка '{category_column}' не содержит данных для визуализации.")
                else:
                    # Ограничение до топ-10 категорий
                    if len(category_counts) > 10:
                        category_counts = category_counts.head(10)
                        st.info("Показаны только топ-10 категорий.")
        
                    if chart_type == "BarH":
                        fig_category = go.Figure(
                            go.Bar(
                                x=category_counts.values,
                                y=category_counts.index,
                                orientation="h",
                                marker=dict(color="royalblue"),
                                text=category_counts.values,
                                textposition="outside"
                            )
                        )
                        fig_category.update_layout(
                            title=f"Распределение {category_column}",
                            xaxis=dict(title="Количество"),
                            yaxis=dict(title="Категории", autorange="reversed"),
                            plot_bgcolor="white"
                        )
        
                    elif chart_type == "BarV":
                        fig_category = go.Figure(
                            go.Bar(
                                x=category_counts.index,
                                y=category_counts.values,
                                marker=dict(color="royalblue"),
                                text=category_counts.values,
                                textposition="outside"
                            )
                        )
                        fig_category.update_layout(
                            title=f"Распределение {category_column}",
                            xaxis=dict(title="Категории"),
                            yaxis=dict(title="Количество"),
                            plot_bgcolor="white"
                        )
        
                    elif chart_type == "Pie":
                        fig_category = px.pie(
                            values=category_counts.values,
                            names=category_counts.index,
                            title=f"Распределение {category_column}",
                            color_discrete_sequence=px.colors.qualitative.Plotly
                        )
        
                    st.plotly_chart(fig_category)
        else:
            st.write("Выберите категорию с левой панели")


    
    
    
    elif tab_selected == "📉 Анализ временных рядов":
        st.subheader("📉 Анализ временных рядов")
        if date_column:
            data[date_column] = pd.to_datetime(data[date_column])
            st.subheader("Тенденция создания сделок с течением времени")
            deal_filter = st.radio(
                "Выберите сделки для анализа",
                options=["Все сделки", "Успешные сделки"],
                index=0,
                horizontal=True
            )

            if deal_filter == "Успешные сделки":
                filtered_data = data[data['Months of study'].notnull()]
            else:
                filtered_data = data

            aggregation_level = st.radio(
                "Выберите уровень агрегации",
                options=["Месяц", "День"],
                index=0,
                horizontal=True
            )

            if aggregation_level == "День":
                time_series = filtered_data.groupby(filtered_data[date_column].dt.date).size()
                title = f"Тенденция сделок (ежедневно)"

                fig_time = px.line(
                    x=time_series.index.astype(str),
                    y=time_series.values,
                    title=title,
                    labels={"x": "Дата", "y": "Количество сделок"}
                )

            else:
                time_series = filtered_data.groupby(filtered_data[date_column].dt.to_period("M")).size()
                title = f"Тенденция сделок (ежемесячно)"

                fig_time = px.line(
                    x=time_series.index.astype(str),
                    y=time_series.values,
                    title=title,
                    labels={"x": "Дата", "y": "Количество сделок"},
                    text=time_series.values
                )

                fig_time.update_traces(textposition="top center")

            fig_time.update_layout(
                title=title,
                xaxis=dict(title="Дата"),
                yaxis=dict(title="Количество сделок"),
                plot_bgcolor="white"
            )

            st.plotly_chart(fig_time)
        else:
            st.write("Выберите колонку с датами с левой панели")            

        
        # --- Первый анализ: Связь между звонками и созданием сделок ---
        st.subheader("Связь между звонками и созданием успешных сделок")
        
        # Загрузка данных о звонках
        calls_data = pd.read_csv("demo_data/Cleaned_Calls.csv")
        
        # Приведение данных к единому формату
        calls_data['CONTACTID'] = calls_data['CONTACTID'].astype(str)
        data['Contact Name'] = data['Contact Name'].astype(str)
        
        # Приведение столбцов с датами к datetime
        calls_data['Call Start Time'] = pd.to_datetime(calls_data['Call Start Time'])
        data['Created Time'] = pd.to_datetime(data['Created Time'])
        
        # Фильтрация успешных сделок
        # successful_deals = data[data['Months of study'].notnull()]
        
        # Группировка звонков по месяцам
        monthly_calls = calls_data.resample('ME', on='Call Start Time').size().reset_index(name='Call Count')
        
        # Группировка успешных сделок по месяцам
        monthly_deals = data.resample('ME', on='Created Time').size().reset_index(name='Deal Count')

        # Объединение данных
        monthly_data = pd.merge(
            monthly_calls,
            monthly_deals,
            left_on='Call Start Time',
            right_on='Created Time',
            how='outer'
        ).fillna(0)
        
        # Переименование столбцов
        monthly_data.rename(columns={'Call Start Time': 'Date'}, inplace=True)
        
        # Рассчитываем корреляцию
        correlation = monthly_data['Call Count'].corr(monthly_data['Deal Count'])
        st.write(f"Корреляция между звонками и созданием сделок: {correlation:.2f}")

        fig_deals_calls = go.Figure()
        
        # Линия для количества звонков
        fig_deals_calls.add_trace(
            go.Scatter(
                x=monthly_data['Date'],
                y=monthly_data['Call Count'],
                mode='lines+markers',
                name='Количество звонков',
                line=dict(color='mediumorchid'),
                yaxis='y1'  # Связь с первой осью
            )
        )
        
        # Линия для количества успешных сделок
        fig_deals_calls.add_trace(
            go.Scatter(
                x=monthly_data['Date'],
                y=monthly_data['Deal Count'],
                mode="lines+markers",  # Добавляем текст
                name='Количество сделок',
                line=dict(color='royalblue'),
                yaxis='y2',  # Связь со второй осью
                # text=monthly_data['Deal Count'].round(),  # Отображаемое значение (округлено)
                # textposition="top center"  # Расположение текста
            )
        )
        
        # Настройка осей
        fig_deals_calls.update_layout(
            # title='Связь между звонками и созданием успешных сделок',
            xaxis=dict(title='Дата'),
            yaxis=dict(
                title='Количество звонков',
                titlefont=dict(color='mediumorchid'),
                tickfont=dict(color='mediumorchid'),
                showgrid=False  # Отключает горизонтальную сетку для основной оси Y
            ),
            yaxis2=dict(
                title='Количество сделок',
                titlefont=dict(color='royalblue'),
                tickfont=dict(color='royalblue'),
                showgrid=False,  # Отключает горизонтальную сетку для основной оси Y
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.5, xanchor='center', y=-0.2, orientation='h'),  # Легенда внизу
            plot_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # Отображение графика в Streamlit
        st.plotly_chart(fig_deals_calls)


        
        # --- Второй анализ: Связь между звонками и созданием успешных сделок ---
        st.subheader("Связь между звонками и созданием успешных сделок")
        
        # Загрузка данных о звонках
        calls_data = pd.read_csv("demo_data/Cleaned_Calls.csv")
        
        # Приведение данных к единому формату
        calls_data['CONTACTID'] = calls_data['CONTACTID'].astype(str)
        data['Contact Name'] = data['Contact Name'].astype(str)
        
        # Приведение столбцов с датами к datetime
        calls_data['Call Start Time'] = pd.to_datetime(calls_data['Call Start Time'])
        data['Created Time'] = pd.to_datetime(data['Created Time'])
        
        # Фильтрация успешных сделок
        successful_deals = data[data['Months of study'].notnull()]
        
        # Группировка звонков по месяцам
        monthly_calls = calls_data.resample('ME', on='Call Start Time').size().reset_index(name='Call Count')
        
        # Группировка успешных сделок по месяцам
        monthly_deals = successful_deals.resample('ME', on='Created Time').size().reset_index(name='Deal Count')

        # Объединение данных
        monthly_data = pd.merge(
            monthly_calls,
            monthly_deals,
            left_on='Call Start Time',
            right_on='Created Time',
            how='outer'
        ).fillna(0)
        
        # Переименование столбцов
        monthly_data.rename(columns={'Call Start Time': 'Date'}, inplace=True)
        
        # Рассчитываем корреляцию
        correlation = monthly_data['Call Count'].corr(monthly_data['Deal Count'])
        st.write(f"Корреляция между звонками и созданием успешных сделок: {correlation:.2f}")

        fig_deals_calls = go.Figure()
        
        # Линия для количества звонков
        fig_deals_calls.add_trace(
            go.Scatter(
                x=monthly_data['Date'],
                y=monthly_data['Call Count'],
                mode='lines+markers',
                name='Количество звонков',
                line=dict(color='mediumorchid'),
                yaxis='y1'  # Связь с первой осью
            )
        )
        
        # Линия для количества успешных сделок
        fig_deals_calls.add_trace(
            go.Scatter(
                x=monthly_data['Date'],
                y=monthly_data['Deal Count'],
                mode="lines+markers+text",  # Добавляем текст
                name='Количество успешных сделок',
                line=dict(color='green'),
                yaxis='y2',  # Связь со второй осью
                text=monthly_data['Deal Count'].round(),  # Отображаемое значение (округлено)
                textposition="top center"  # Расположение текста
            )
        )
        
        # Настройка осей
        fig_deals_calls.update_layout(
            # title='Связь между звонками и созданием успешных сделок',
            xaxis=dict(title='Дата'),
            yaxis=dict(
                title='Количество звонков',
                titlefont=dict(color='mediumorchid'),
                tickfont=dict(color='mediumorchid'),
                showgrid=False  # Отключает горизонтальную сетку для основной оси Y
            ),
            yaxis2=dict(
                title='Количество успешных сделок',
                titlefont=dict(color='green'),
                tickfont=dict(color='green'),
                showgrid=False,  # Отключает горизонтальную сетку для основной оси Y
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.5, xanchor='center', y=-0.2, orientation='h'),  # Легенда внизу
            plot_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # Отображение графика в Streamlit
        st.plotly_chart(fig_deals_calls)
       
        
        
        # --- Третий анализ: Сравнение длительности успешных и потерянных сделок ---
        st.subheader("Сравнение длительности успешных и потерянных сделок")
    
        df3 = data.copy()
        # Убедимся, что даты в нужном формате
        df3['Closing Date'] = pd.to_datetime(df3['Closing Date'], errors='coerce')
        df3['Created Time'] = pd.to_datetime(df3['Created Time'], errors='coerce')
        # Вычисляем продолжительность сделки
        df3['Deal Duration'] = (df3['Closing Date'] - df3['Created Time']).dt.days
        
        # Удаляем отрицательные значения
        df3 = df3[df3['Deal Duration'] >= 0]
        
        # Разделяем успешные и потерянные сделки
        successful_deals = df3[df3['Months of study'].notnull()]['Deal Duration']
        lost_deals = df3[~df3['Months of study'].notnull()]['Deal Duration']
        
        # Расчет средних значений
        avg_successful_duration = successful_deals.mean()
        avg_lost_duration = lost_deals.mean()
        overall_avg_duration = df3['Deal Duration'].mean()
    
        # Отображение средних значений
        st.write(f"Средняя продолжительность успешных сделок: {avg_successful_duration:.2f} дней")
        st.write(f"Средняя продолжительность потерянных сделок: {avg_lost_duration:.2f} дней")
        st.write(f"Общая средняя продолжительность сделок: {overall_avg_duration:.2f} дней")
        
        st.write(f"Успешные сделки по Closing Date: {len(successful_deals)}")
        st.write(f"Потерянные сделки по Closing Date: {len(lost_deals)}")
        
        # Кнопка для отображения графиков
        if st.button("Показать график"):
            # Проверяем наличие данных
            if not successful_deals.empty and not lost_deals.empty:
                # Нормализованные гистограммы
                fig_hist = go.Figure()
        
                fig_hist.add_trace(
                    go.Histogram(
                        x=successful_deals,
                        nbinsx=30,
                        name="Успешные сделки",
                        histnorm="probability",
                        marker=dict(color="green"),
                        opacity=0.7
                    )
                )
                fig_hist.add_trace(
                    go.Histogram(
                        x=lost_deals,
                        nbinsx=30,
                        name="Потерянные сделки",
                        histnorm="probability",
                        marker=dict(color="red"),
                        opacity=0.7
                    )
                )
        
                fig_hist.update_layout(
                    title="Сравнение длительности успешных и потерянных сделок (нормализовано)",
                    xaxis_title="Длительность сделки (в днях)",
                    yaxis_title="Плотность",
                    barmode="overlay",
                    legend_title="Тип сделки"
                )
        
                # KDE графики
                kde_fig = ff.create_distplot(
                    [successful_deals, lost_deals],
                    group_labels=["Успешные сделки", "Потерянные сделки"],
                    colors=["green", "red"],
                    show_hist=False
                )
        
                kde_fig.update_layout(
                    title="Сравнение длительности успешных и потерянных сделок (графики плотности)",
                    xaxis_title="Длительность сделки (в днях)",
                    yaxis_title="Плотность",
                    legend_title="Тип сделки"
                )
        
                # Отображение графиков
                st.plotly_chart(fig_hist, use_container_width=True)
                st.plotly_chart(kde_fig, use_container_width=True)
            else:
                st.warning("Недостаточно данных для построения графиков.")  
    
    
    
    
    elif tab_selected == "📋 Анализ эффективности кампаний и источников":
        st.subheader("📋 Анализ эффективности кампаний и источников")
        
        # Создание вкладок
        tab1, tab2 = st.tabs(["Advertising Campaigns",
                              "Marketing Sources"])

        # Вкладка 1:
        with tab1:        
        
            st.subheader("Эффективность различных кампаний с точки зрения генерации лидов и коэффициента конверсии")
        
            # --- Обработка данных ---
            df4 = data.dropna(subset=['Campaign', 'Stage'])
            leads_by_campaign = df4.groupby('Campaign')['Id'].count().reset_index(name='Leads')
            successful_deals = df4[df4['Months of study'].notnull()]
            successful_by_campaign = successful_deals.groupby('Campaign')['Id'].count().reset_index(name='Successful Deals')
        
            campaign_performance = pd.merge(leads_by_campaign, successful_by_campaign, on='Campaign', how='left')
            campaign_performance['Successful Deals'] = campaign_performance['Successful Deals'].fillna(0)
            campaign_performance['Conversion Rate (%)'] = (campaign_performance['Successful Deals'] / campaign_performance['Leads']) * 100
            campaign_performance = campaign_performance.sort_values(by=['Leads', 'Conversion Rate (%)'], ascending=False)
            filtered_data = campaign_performance[campaign_performance['Conversion Rate (%)'] >= 2]
        
            # --- Новые расчеты ---
            # Среднее количество обработанных сделок по кампаниям
            average_processed_deals = campaign_performance['Leads'].mean()
            
            # Среднее количество успешных сделок по кампаниям
            average_successful_deals = campaign_performance['Successful Deals'].mean()
            
            # Средний коэффициент конверсии по кампаниям
            average_conversion_rate = campaign_performance['Conversion Rate (%)'].mean()
            
            # --- Вывод новых данных ---
            st.markdown(f"**Среднее количество обработанных сделок по кампаниям:** {average_processed_deals:.2f}")
            st.markdown(f"**Среднее количество успешных сделок по кампаниям:** {average_successful_deals:.2f}")
            st.markdown(f"**Средний коэффициент конверсии по кампаниям:** {average_conversion_rate:.2f}%")

            
            
            # --- Первый график: Лиды и успешные сделки ---
            fig1 = make_subplots(specs=[[{"secondary_y": True}]], vertical_spacing=0.2)
        
            # Лиды
            fig1.add_trace(
                go.Bar(
                    x=filtered_data['Campaign'],
                    y=filtered_data['Leads'],
                    name="Leads",
                    marker_color="plum",
                ),
                secondary_y=False,
            )
        
            # Успешные сделки
            fig1.add_trace(
                go.Scatter(
                    x=filtered_data['Campaign'],
                    y=filtered_data['Successful Deals'],
                    name="Successful Deals",
                    mode="lines+markers+text",  # Добавляем текст
                    line=dict(color="cornflowerblue"),
                    marker=dict(size=7),
                    text=filtered_data['Successful Deals'],  # Отображаемое значение
                    textposition="top center"  # Расположение текста
                ),
                secondary_y=True,
            )
        
            fig1.update_layout(
                title="Лиды и успешные сделки по кампаниям (Конверсия > 2%)",
                height=600,
                xaxis=dict(title="Кампании", tickangle=45),  # Угол наклона подписей оси X),
                yaxis=dict(title="Количество лидов", 
                           titlefont=dict(color='mediumorchid'),
                           tickfont=dict(color='mediumorchid'), 
                           showgrid=False,  # Отключает горизонтальную сетку для основной оси Y
                           zeroline=False,
                           side="left"),
                yaxis2=dict(title="Количество успешных сделок", 
                            titlefont=dict(color='royalblue'),
                            tickfont=dict(color='royalblue'),
                            showgrid=False,  # Отключает горизонтальную сетку для основной оси Y
                            zeroline=False,
                            side="right", 
                            overlaying="y"),
                legend=dict(orientation="h", x=0.5, xanchor="center", y=1.1)
            )
        
            # --- Второй график: Лиды и коэффициент конверсии ---
            fig2 = make_subplots(specs=[[{"secondary_y": True}]], vertical_spacing=0.2)
        
            # Лиды
            fig2.add_trace(
                go.Bar(
                    x=filtered_data['Campaign'],
                    y=filtered_data['Leads'],
                    name="Leads",
                    marker_color="plum"
                ),
                secondary_y=False,
            )
        
            # Коэффициент конверсии
            fig2.add_trace(
                go.Scatter(
                    x=filtered_data['Campaign'],
                    y=filtered_data['Conversion Rate (%)'],
                    name="Conversion Rate",
                    mode="lines+markers+text",  # Добавляем текст
                    line=dict(color="mediumseagreen"), # dash="dash"),
                    marker=dict(size=7),
                    text=filtered_data['Conversion Rate (%)'].round(),  # Отображаемое значение (округлено)
                    textposition="top center"  # Расположение текста
                ),
                secondary_y=True,
            )
        
            fig2.update_layout(
                title="Лиды и коэффициент конверсии по кампаниям (Конверсия > 2%)",
                height=600,
                xaxis=dict(title="Кампании", tickangle=45),  # Угол наклона подписей оси X),
                yaxis=dict(title="Количество лидов",
                           titlefont=dict(color='mediumorchid'),
                           tickfont=dict(color='mediumorchid'),
                           showgrid=False,  # Отключает горизонтальную сетку для основной оси Y
                           zeroline=False,
                           side="left"),
                yaxis2=dict(title="Коэффициент конверсии (%)", 
                            titlefont=dict(color='green'),
                            tickfont=dict(color='green'),
                            showgrid=False,  # Отключает горизонтальную сетку для основной оси Y
                            zeroline=False,
                            side="right", 
                            overlaying="y"),
                legend=dict(orientation="h", x=0.5, xanchor="center", y=1.1)
            )
        
            # --- Вывод графиков ---
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)

        # Вкладка 2:
        with tab2: 
            st.subheader("Эффективность различных маркетинговых источников (Source) в генерировании качественных лидов")
            
            # Копируем DataFrame deals во временный df
            df5 = data.copy()
            
            # Группировка качественных сделок
            df5['Target Quality'] = df5['Quality'].map({
                'A - High': 'High',
                'B - Medium': 'Medium',
                'C - Low': 'Non-Target',
                'D - Non Target': 'Non-Target',
                'E - Non Qualified': 'Non-Target',
                'F': 'Non-Target'
            })
            
            # Общее количество сделок по каждому источнику
            source_total = df5['Source'].value_counts()
            
            # Количество High и Medium сделок по источникам
            high_deals = df5[df5['Target Quality'] == 'High']['Source'].value_counts()
            medium_deals = df5[df5['Target Quality'] == 'Medium']['Source'].value_counts()
            
            # Количество закрытых сделок (Payment Done) по источникам
            closed_won = df5[df5['Months of study'].notnull()]['Source'].value_counts()
            
            # Расчёт процентов
            high_percent = (high_deals / source_total) * 100
            medium_percent = (medium_deals / source_total) * 100
            conversion_rate = (closed_won / source_total) * 100
            
            # Итоговая таблица
            result = pd.DataFrame({
                'Total Deals': source_total,
                'High Deals': high_deals,
                'Medium Deals': medium_deals,
                'High Percent (%)': high_percent,
                'Medium Percent (%)': medium_percent,
                'Payment Done Deals': closed_won,
                'Conversion Rate (%)': conversion_rate
            }).fillna(0)
            
            # Сортируем по конверсии
            result = result.sort_values(by=['Conversion Rate (%)'], ascending=False)
            
            # --- Первый график: Коэффициент конверсии по источникам ---
            fig1 = go.Figure()
            
            fig1.add_trace(
                go.Bar(
                    x=result.index,
                    y=result['Conversion Rate (%)'],
                    name='Коэффициент конверсии (%)',
                    marker=dict(color='royalblue'),
                    text=result['Conversion Rate (%)'].round(2),  # Значения для отображения
                    textposition='outside'  # Расположение текста
                )
            )
            
            fig1.update_layout(
                title="Коэффициент конверсии по источникам (Conversion Rate by Source)",
                xaxis=dict(title="Источник", tickangle=45),
                yaxis=dict(title="Коэффициент конверсии (%)"),
                height=500,
                showlegend=False
            )
            
            # --- Второй график: Эффективность источников в генерации качественных лидов ---
            fig2 = go.Figure()
            
            fig2.add_trace(
                go.Bar(
                    x=result.index,
                    y=result['High Percent (%)'],
                    name='Процент High (%)',
                    marker=dict(color='green'),
                    text=result['High Percent (%)'].round(2),  # Значения для отображения
                    textposition='outside'
                )
            )
            
            fig2.add_trace(
                go.Bar(
                    x=result.index,
                    y=result['Medium Percent (%)'],
                    name='Процент Medium (%)',
                    marker=dict(color='orange'),
                    text=result['Medium Percent (%)'].round(2),  # Значения для отображения
                    textposition='outside'
                )
            )
            
            fig2.update_layout(
                title="Эффективность источников в генерации качественных лидов",
                xaxis=dict(title="Источник", tickangle=45),
                yaxis=dict(title="Процент"),
                height=500,
                barmode="stack",
                showlegend=True,
                legend=dict(orientation="v", x=1, xanchor="right", y=1)
            )
            
            # Выводим графики по очереди
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)



    # --- Анализ эффективности владельцев сделок ---
    elif tab_selected == "💼 Анализ эффективности работы отдела продаж":
        st.subheader("💼 Анализ эффективности работы отдела продаж")

        # Создание вкладок
        tab1, tab2 = st.tabs(["Deal Owners",
                              "Advertising Campaigns"])

        # Вкладка 1:
        with tab1:        

            st.subheader("Эффективность отдельных владельцев сделок с точки зрения количества обработанных сделок, коэффициента конверсии и общей суммы продаж")
        
            # Подготовка данных
            owners_total_deals = data['Deal Owner Name'].value_counts()
            owners_closed_won = data[data['Months of study'].notnull()]['Deal Owner Name'].value_counts()
            owners_conversion_rate = (owners_closed_won / owners_total_deals) * 100
            owners_total_sales = data[data['Months of study'].notnull()].groupby('Deal Owner Name')['Initial Amount Paid'].sum()
            
            owners_result = pd.DataFrame({
                'Total Deals': owners_total_deals,
                'Closed Deals': owners_closed_won,
                'Conversion Rate (%)': owners_conversion_rate,
                'Total Sales Amount': owners_total_sales
            }).fillna(0).sort_values(by='Total Sales Amount', ascending=False)
            
            # Средние показатели
            avg_conversion_rate = owners_conversion_rate.mean()
            avg_total_deals = owners_total_deals.mean()
            
            st.write(f"Среднее количество обработанных сделок: {avg_total_deals:.2f}")
            st.write(f"Средний коэффициент конверсии: {avg_conversion_rate:.2f}%")
            
            # Фильтрация владельцев с продажами
            owners_with_sales = owners_result[owners_result['Closed Deals'] > 0]
            
            # --- Построение графиков ---
            # График 1: Закрытые сделки и общая сумма продаж
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig1.add_trace(
                go.Bar(
                    x=owners_with_sales.index,
                    y=owners_with_sales['Closed Deals'],
                    name='Closed Deals',
                    marker_color='skyblue',
                    text=owners_with_sales['Closed Deals'],
                    textposition='inside'
                ),
                secondary_y=False,
            )
            
            fig1.add_trace(
                go.Scatter(
                    x=owners_with_sales.index,
                    y=owners_with_sales['Total Sales Amount'],
                    name='Total Sales Amount',
                    mode='lines+markers',
                    line=dict(color='purple'),
                    marker=dict(size=7)
                ),
                secondary_y=True,
            )
            
            fig1.update_layout(
                title='Effectiveness of Deal Owners: Sales & Closed Deals',
                xaxis_title='Deal Owner Name',
                yaxis=dict(
                    title='Closed Deals (Count)',
                    titlefont=dict(color='steelblue'),
                    tickfont=dict(color='steelblue'),
                    zeroline=False,
                    showgrid=False
                ),
                yaxis2=dict(
                    title='Total Sales Amount',
                    titlefont=dict(color='purple'),
                    tickfont=dict(color='purple'),
                    overlaying='y',
                    side='right',
                    zeroline=False,
                    showgrid=False
                ),
                legend=dict(x=0.5, xanchor='center', y=1.1, orientation="h"),
                template='plotly_white'
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # График 2: Закрытые сделки и коэффициент конверсии
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig2.add_trace(
                go.Bar(
                    x=owners_with_sales.index,
                    y=owners_with_sales['Closed Deals'],
                    name='Closed Deals',
                    marker_color='skyblue',
                    text=owners_with_sales['Closed Deals'],
                    textposition='inside'
                ),
                secondary_y=False,
            )
            
            fig2.add_trace(
                go.Scatter(
                    x=owners_with_sales.index,
                    y=owners_with_sales['Conversion Rate (%)'],
                    name='Conversion Rate',
                    mode='lines+markers',
                    line=dict(color='green', dash='dash'),
                    marker=dict(size=7)
                ),
                secondary_y=True,
            )
            
            fig2.update_layout(
                title='Effectiveness of Deal Owners: Conversion Rate & Closed Deals',
                xaxis_title='Deal Owner Name',
                yaxis=dict(
                    title='Closed Deals (Count)',
                    titlefont=dict(color='steelblue'),
                    tickfont=dict(color='steelblue'),
                    zeroline=False,
                    showgrid=False
                ),
                yaxis2=dict(
                    title='Conversion Rate (%)',
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                    overlaying='y',
                    side='right',
                    zeroline=False,
                    showgrid=False
                ),
                legend=dict(x=0.5, xanchor='center', y=1.1, orientation="h"),
                template='plotly_white'
            )
            
            st.plotly_chart(fig2, use_container_width=True)



        # Вкладка 2:
        with tab2:        

            st.subheader("Эффективность рекламных кампаний с точки зрения количества обработанных сделок, коэффициента конверсии и общей суммы продаж")
            # Анализ рекламных кампаний
            campaign_total_deals = data['Campaign'].value_counts()
            campaign_closed_won = data[data['Months of study'].notnull()]['Campaign'].value_counts()
            campaign_conversion_rate = (campaign_closed_won / campaign_total_deals) * 100
            campaign_total_sales = data[data['Months of study'].notnull()].groupby('Campaign')['Initial Amount Paid'].sum()
            
            campaign_result = pd.DataFrame({
                'Total Deals': campaign_total_deals,
                'Closed Deals (Payment Done)': campaign_closed_won,
                'Conversion Rate (%)': campaign_conversion_rate,
                'Total Sales Amount': campaign_total_sales
            }).fillna(0).sort_values(by='Total Sales Amount', ascending=False)
            
            campaigns_with_sales = campaign_result[campaign_result['Closed Deals (Payment Done)'] > 0]
            
            # --- Первый график: Закрытые сделки и Total Sales Amount ---
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Закрытые сделки
            fig1.add_trace(
                go.Bar(
                    x=campaigns_with_sales.index,
                    y=campaigns_with_sales['Closed Deals (Payment Done)'],
                    name='Closed Deals',
                    marker_color='skyblue',
                    text=campaigns_with_sales['Closed Deals (Payment Done)'],  # Добавление меток
                    textposition='inside'  # Позиция меток
                ),
                secondary_y=False,
            )
            
            # Total Sales Amount
            fig1.add_trace(
                go.Scatter(
                    x=campaigns_with_sales.index,
                    y=campaigns_with_sales['Total Sales Amount'],
                    name='Total Sales Amount',
                    mode='lines+markers',
                    line=dict(color='purple'),
                    # text=campaigns_with_sales['Total Sales Amount'],  # Значения меток
                    # textposition='top center'  # Позиция текста
                ),
                secondary_y=True,
            )
            
            fig1.update_layout(
                title='Effectiveness of Campaigns: Sales & Closed Deals',
                height=500,
                xaxis_title='Campaign',
                xaxis=dict(tickangle=45),  # Угол наклона подписей оси X
                yaxis=dict(
                    title='Closed Deals (Count)',
                    titlefont=dict(color='steelblue'),
                    tickfont=dict(color='steelblue'),
                    zeroline=False,
                    showgrid=False  # Отключает горизонтальную сетку для основной оси Y
                ),
                yaxis2=dict(
                    title='Total Sales Amount',
                    titlefont=dict(color='purple'),
                    tickfont=dict(color='purple'),
                    side='right',
                    overlaying='y',
                    zeroline=False,
                    showgrid=False  # Отключает горизонтальную сетку для второй оси Y
                ),
                legend=dict(x=0.5, xanchor='center', y=1.1, orientation="h"),
                template='plotly_white'
            )
            
            # --- Второй график: Закрытые сделки и Conversion Rate ---
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Закрытые сделки
            fig2.add_trace(
                go.Bar(
                    x=campaigns_with_sales.index,
                    y=campaigns_with_sales['Closed Deals (Payment Done)'],
                    name='Closed Deals',
                    marker_color='skyblue',
                    text=campaigns_with_sales['Closed Deals (Payment Done)'],  # Добавление меток
                    textposition='inside'  # Позиция меток
                ),
                secondary_y=False,
            )
            
            # Conversion Rate
            fig2.add_trace(
                go.Scatter(
                    x=campaigns_with_sales.index,
                    y=campaigns_with_sales['Conversion Rate (%)'],
                    name='Conversion Rate',
                    mode='lines+markers',
                    line=dict(color='green') #  dash='dash'
                    # text=campaigns_with_sales['Conversion Rate (%)'],  # Значения меток
                    # textposition='top center'  # Позиция текста
                ),
                secondary_y=True,
            )
            
            fig2.update_layout(
                title='Effectiveness of Campaigns: Conversion Rate & Closed Deals',
                height=500,
                xaxis_title='Campaign',
                xaxis=dict(tickangle=45),  # Угол наклона подписей оси X
                yaxis=dict(
                    title='Closed Deals (Count)',
                    titlefont=dict(color='steelblue'),
                    tickfont=dict(color='steelblue'),
                    zeroline=False,
                    showgrid=False  # Отключает горизонтальную сетку для основной оси Y
                ),
                yaxis2=dict(
                    title='Conversion Rate (%)',
                    titlefont=dict(color='green'),
                    tickfont=dict(color='green'),
                    side='right',
                    overlaying='y',
                    zeroline=False,
                    showgrid=False  # Отключает горизонтальную сетку для второй оси Y
                ),
                legend=dict(x=0.5, xanchor='center', y=1.1, orientation="h"),
                template='plotly_white'
            )
    
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)





    elif tab_selected == "💰 Анализ платежей и продуктов":
        st.subheader("💰 Анализ платежей и продуктов")
        
        # Создание вкладок
        tab1, tab2, tab3 = st.tabs(["Payment Types", 
                                    "Top Products",
                                    "Education Type"])

        # Вкладка 1: 
        with tab1:
        
            st.subheader("Распределение типов оплаты и их влияние на успешность сделок")
            # Копируем DataFrame deals во временный df
            df = data.copy()
            
            # Категоризация успешности сделок
            df['is_successful'] = (df['Months of study'].notnull()).astype(int)
            
            # --- Детализация успешных сделок ---
            detailed_summary = df.groupby('Payment Type').agg(
                total_deals=('is_successful', 'size'),
                successful_deals=('is_successful', 'sum'),
                avg_initial_payment=('Initial Amount Paid', 'mean'),
                avg_offer_amount=('Offer Total Amount', 'mean'),
                avg_study_months=('Months of study', 'mean')
            ).round(2)
            
            # Добавляем коэффициент конверсии
            detailed_summary['conversion_rate'] = (detailed_summary['successful_deals'] / detailed_summary['total_deals']).round(2)

            # --- Визуализация детализации ---
            detailed_fig = make_subplots(specs=[[{"secondary_y": True}]])
            # --- Таблица для отображения ---
            table_fig2 = go.Figure(data=[
                go.Table(
                    header=dict(
                        values=['Payment Type', 'Total Deals', 'Successful Deals', 'Conversion Rate',
                                'Average Initial Amount Paid', 'Average Offer Total Amount', 'Average Months of study'],
                        fill_color='lightgrey',
                        align='center'
                    ),
                    cells=dict(
                        values=[detailed_summary.index, detailed_summary['total_deals'], detailed_summary['successful_deals'],
                                detailed_summary['conversion_rate'], detailed_summary['avg_initial_payment'], 
                                detailed_summary['avg_offer_amount'], detailed_summary['avg_study_months']],
                        fill_color='white',
                        align='center',
                        height=30,  # Добавляем высоту ячейки
                    )
                )
            ])

            table_fig2.update_layout(
                height=200,  # Общая высота таблицы
                margin=dict(l=5, r=5, t=5, b=5)
            )
            st.plotly_chart(table_fig2, use_container_width=True)
            
            
            
            # --- Гистограмма успешных сделок ---
            bar_fig = px.bar(
                detailed_summary.reset_index(),
                x='Payment Type',
                y='successful_deals',
                title='Successful Deals by Payment Type',
                labels={'successful_deals': 'Successful Deals', 'Payment Type': 'Payment Type'},
                text='successful_deals'
            )
            bar_fig.update_traces(texttemplate='%{text}', textposition='outside', marker_color=px.colors.qualitative.Plotly)
            bar_fig.update_layout(
                yaxis=dict(title='Successful Deals'),
                xaxis=dict(title='Payment Type')
            )
            
            # --- Гистограмма коэффициентов конверсии ---
            bar_fig2 = px.bar(
                detailed_summary.reset_index(),
                x='Payment Type',
                y='conversion_rate',
                title='Conversion Rate by Payment Type',
                labels={'conversion_rate': 'Conversion Rate', 'Payment Type': 'Payment Type'},
                text='conversion_rate',
            )
            bar_fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside', marker_color=px.colors.qualitative.Plotly)
            bar_fig2.update_layout(
                yaxis=dict(title='Conversion Rate', range=[0, 1]),
                xaxis=dict(title='Payment Type')
            )


            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(bar_fig, use_container_width=True)
            with col2:
                st.plotly_chart(bar_fig2, use_container_width=True)
                
    
            # --- Анализ времени до закрытия сделки ---
            df['creation_to_closing_days'] = (pd.to_datetime(df['Closing Date']) - pd.to_datetime(df['Created Time'])).dt.days
            time_analysis = df.groupby('Payment Type').agg(
                avg_days_to_close=('creation_to_closing_days', 'mean'),
                median_days_to_close=('creation_to_closing_days', 'median')
            ).round(2)
            
            # --- Визуализация времени до закрытия ---
            time_fig = go.Figure()
            time_fig.add_trace(go.Bar(
                x=time_analysis.index,
                y=time_analysis['avg_days_to_close'],
                name='Average Days to Close',
                marker_color='orange',
                text=time_analysis['avg_days_to_close'],
            ))
            time_fig.add_trace(go.Bar(
                x=time_analysis.index,
                y=time_analysis['median_days_to_close'],
                name='Median Days to Close',
                marker_color='blue',
                text=time_analysis['median_days_to_close'],
            ))
            time_fig.update_layout(
                barmode='group',
                title='Average and Median Days to Close Deals by Payment Type',
                xaxis=dict(title='Payment Type'),
                yaxis=dict(title='Days'),
                legend=dict(x=0.2, xanchor='center', y=1),
            )
    
            st.plotly_chart(time_fig, use_container_width=True)
    
    
            
            # Средние платежи
            detailed_fig.add_trace(
                go.Bar(
                    x=detailed_summary.index,
                    y=detailed_summary['avg_initial_payment'],
                    name='Avg Initial Payment',
                    marker_color='blue',
                    text=detailed_summary['avg_initial_payment'],
                    textposition='inside',  # Позиция меток
                    opacity=0.6
                ),
                secondary_y=False
            )
            
            # Средняя длительность обучения
            detailed_fig.add_trace(
                go.Scatter(
                    x=detailed_summary.index,
                    y=detailed_summary['avg_study_months'],
                    name='Avg Study Months',
                    mode='lines+markers+text',
                    line=dict(color='orange', width=2),
                    text=detailed_summary['avg_study_months'],
                    textposition='top center',
                    textfont=dict(color='orange')  # Цвет текста
                ),
                secondary_y=True
            )
            
            detailed_fig.update_layout(
                title='Initial Payment and Study Months by Payment Type',
                xaxis=dict(title='Payment Type'),
                yaxis=dict(
                    title='Initial Payment',
                    titlefont=dict(color='royalblue'),
                    tickfont=dict(color='royalblue'),
                    zeroline=False,
                    showgrid=False
                ),
                yaxis2=dict(
                    title='Months of Study',
                    overlaying='y', 
                    side='right',
                    titlefont=dict(color='orange'),
                    tickfont=dict(color='orange'),
                    zeroline=False,
                    showgrid=False  
                ),
                legend=dict(x=0.8, xanchor='center', y=1),
                template='plotly_white'
            )
    
            st.plotly_chart(detailed_fig, use_container_width=True)

            


        
        # Вкладка 2: 
        with tab2:
            st.subheader("Анализ популярности и успешности различных продуктов")
        
            # Категоризация успешности сделок
            df['is_successful'] = (df['Months of study'].notnull()).astype(int)
            
            # Успешность по продуктам
            product_success = df.groupby('Product').agg(
                total_deals=('is_successful', 'size'),
                successful_deals=('is_successful', 'sum')
            )
            product_success['conversion_rate'] = (product_success['successful_deals'] / product_success['total_deals']).round(2)
            product_success = product_success.sort_values(by='total_deals', ascending=False).reset_index()
            
            # Таблица 1: Успешность по продуктам
            product_table = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Product</b>', '<b>Total Deals</b>', '<b>Successful Deals</b>', '<b>Conversion Rate</b>'],
                    fill_color='lightgrey',
                    align='left',
                    height=30  # Высота заголовка
                ),
                cells=dict(
                    values=[
                        product_success['Product'],
                        product_success['total_deals'],
                        product_success['successful_deals'],
                        product_success['conversion_rate']
                    ],
                    fill_color='white',
                    align='left',
                    height=25  # Высота строк
                )
            )])
            product_table.update_layout(
                height=200,  # Общая высота таблицы
                margin=dict(l=5, r=5, t=5, b=5)
            )
            st.plotly_chart(product_table, use_container_width=True)

            # Данные для топ-10 популярных продуктов
            product_popularity = product_success[['Product', 'total_deals']].sort_values(
                by='total_deals', ascending=False
            )
            
            # График 1: Топ-10 популярных продуктов
            popularity_fig = go.Figure(data=[
                go.Bar(
                    x=product_popularity['Product'],
                    y=product_popularity['total_deals'],
                    marker=dict(color='skyblue'),
                    text=product_popularity['total_deals'],
                    textposition="inside"
                )
            ])
            popularity_fig.update_layout(
                title='Top Most Popular Products',
                xaxis=dict(title='Product', tickangle=45),
                yaxis=dict(title='Number of Deals'),
                # margin=dict(l=10, r=10, t=40, b=10),
                height=400
            )
            
            # Данные для топ-10 продуктов по конверсии
            top_conversion = product_success.sort_values(by='conversion_rate', ascending=False)
            
            # График 2: Топ-10 продуктов по конверсии
            conversion_fig = go.Figure(data=[
                go.Bar(
                    x=top_conversion['Product'],
                    y=top_conversion['conversion_rate'],
                    marker=dict(color='orange'),
                    text=top_conversion['conversion_rate'],
                    textposition="inside"
                )
            ])
            conversion_fig.update_layout(
                title='Top Products by Conversion Rate',
                xaxis=dict(title='Product', tickangle=45),
                yaxis=dict(title='Conversion Rate'),
                # margin=dict(l=10, r=10, t=40, b=10),
                height=400
            )
            
          
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(popularity_fig, use_container_width=True)
            with col2:
                st.plotly_chart(conversion_fig, use_container_width=True)

        with tab3:
            st.subheader("Анализ популярности и успешности типов обучения")

            # Успешность по типам обучения
            education_type_success = df.groupby('Education Type').agg(
                total_deals=('is_successful', 'size'),
                successful_deals=('is_successful', 'sum')
            )
            education_type_success['conversion_rate'] = (education_type_success['successful_deals'] / education_type_success['total_deals']).round(2)
            education_type_success = education_type_success.sort_values(by='total_deals', ascending=False).reset_index()
            
            # Таблица 2: Успешность по типам обучения
            education_type_table = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Education Type</b>', '<b>Total Deals</b>', '<b>Successful Deals</b>', '<b>Conversion Rate</b>'],
                    fill_color='lightgrey',
                    align='left',
                    height=30
                ),
                cells=dict(
                    values=[
                        education_type_success['Education Type'],
                        education_type_success['total_deals'],
                        education_type_success['successful_deals'],
                        education_type_success['conversion_rate']
                    ],
                    fill_color='white',
                    align='left',
                    height=25
                )
            )])
            education_type_table.update_layout(
                height=100,  # Общая высота таблицы
                margin=dict(l=5, r=5, t=5, b=5)
            )
            
            st.plotly_chart(education_type_table, use_container_width=True)

            # Данные для топ-10 популярных типов обучения
            education_type_popularity = education_type_success[['Education Type', 'total_deals']].sort_values(
                by='total_deals', ascending=False
            ).head(10)
            
            # График 1: Топ-10 популярных типов обучения
            education_popularity_fig = go.Figure(data=[
                go.Bar(
                    x=education_type_popularity['Education Type'],
                    y=education_type_popularity['total_deals'],
                    marker=dict(color='lightgreen'),
                    text=education_type_popularity['total_deals'],
                    textposition="inside"
                )
            ])
            education_popularity_fig.update_layout(
                title='Top 10 Most Popular Education Types',
                xaxis=dict(title='Education Type'),
                yaxis=dict(title='Number of Deals'),
                # margin=dict(l=10, r=10, t=40, b=10),
                height=400
            )
            
            # Данные для топ-10 типов обучения по конверсии
            top_education_conversion = education_type_success.sort_values(by='conversion_rate', ascending=False).head(10)
            
            # График 2: Топ-10 типов обучения по конверсии
            education_conversion_fig = go.Figure(data=[
                go.Bar(
                    x=top_education_conversion['Education Type'],
                    y=top_education_conversion['conversion_rate'],
                    marker=dict(color='purple'),
                    text=top_education_conversion['conversion_rate'],
                    textposition="inside"
                )
            ])
            education_conversion_fig.update_layout(
                title='Top 10 Education Types by Conversion Rate',
                xaxis=dict(title='Education Type'),
                yaxis=dict(title='Conversion Rate'),
                # margin=dict(l=10, r=10, t=40, b=10),
                height=400
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(education_popularity_fig, use_container_width=True)
            with col2:
                st.plotly_chart(education_conversion_fig, use_container_width=True)

            product_education_analysis = df.groupby(['Product', 'Education Type']).agg(
                total_deals=('is_successful', 'size'),
                successful_deals=('is_successful', 'sum')
            )
            product_education_analysis["conversion_rate"] = (
                product_education_analysis["successful_deals"]
                / product_education_analysis["total_deals"]
            ).round(2)
            
            # Сброс индекса для удобного анализа
            product_education_analysis = product_education_analysis.reset_index()
            
            
            # Создание сводной таблицы для тепловой карты
            pivot_table = product_education_analysis.pivot(
                index='Product', 
                columns='Education Type', 
                values='conversion_rate'
            )
            
            # Вычисление яркости для определения цвета текста
            def calculate_text_color(value, zmin, zmax):
                normalized = (value - zmin) / (zmax - zmin)
                return 'white' if normalized < 0.5 else 'black'
            
            # Подготовка данных
            z_values = pivot_table.values
            x_labels = pivot_table.columns
            y_labels = pivot_table.index
            
            # Минимальное и максимальное значение для нормализации
            zmin, zmax = np.nanmin(z_values), np.nanmax(z_values)
            
            # Генерация аннотаций
            annotations = []
            for i, y_label in enumerate(y_labels):
                for j, x_label in enumerate(x_labels):
                    value = z_values[i][j]
                    color = calculate_text_color(value, zmin, zmax)
                    annotations.append(
                        dict(
                            x=x_label,
                            y=y_label,
                            text=str(round(value, 2)) if not np.isnan(value) else '',
                            showarrow=False,
                            font=dict(color=color, size=12),
                        )
                    )
            
            # Построение тепловой карты
            heatmap_fig = go.Figure(data=go.Heatmap(
                z=z_values,
                x=x_labels,
                y=y_labels,
                colorscale='Viridis',
                colorbar=dict(title='Conversion Rate'),
            ))
            
            # Добавление аннотаций
            heatmap_fig.update_layout(annotations=annotations)
            
            # Настройка оформления
            heatmap_fig.update_layout(
                title='Conversion Rate by Product and Education Type',
                xaxis=dict(title='Education Type'),
                yaxis=dict(title='Product'),
                # margin=dict(l=10, r=10, t=40, b=10),
                height=500
            )
            
            # Отображение тепловой карты в Streamlit
            st.subheader("Анализ тепловой карты")
            
            st.plotly_chart(heatmap_fig, use_container_width=True)            


    elif tab_selected == "🌍 Географический анализ":
        st.subheader("🌍 Географический анализ")
        # Создание вкладок
        tab1, tab2 = st.tabs(["Cities & Countries", 
                              "Level of Deutsch"])

        # Вкладка 1: 
        with tab1:
        
            st.subheader("Распределение сделок по городам")
 
            # Копируем DataFrame deals во временный df
            df = data.copy()
            
            # Категоризация успешности сделок
            df['is_successful'] = (df['Months of study'].notnull()).astype(int)
            
            # Агрегация данных по городам
            city_analysis = df.groupby('City').agg(
                total_deals=('is_successful', 'size'),
                successful_deals=('is_successful', 'sum')
            )
            city_analysis['conversion_rate'] = (city_analysis['successful_deals'] / city_analysis['total_deals']).round(2)
            
            # Сортировка по количеству сделок для анализа топ-городов
            top_cities = city_analysis.sort_values(by='total_deals', ascending=False).head(10)
            
            # Создание графика с двойной осью
            fig_city = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Гистограмма количества сделок (левая ось)
            fig_city.add_trace(
                go.Bar(
                    x=top_cities.index,
                    y=top_cities['total_deals'],
                    name='Total Deals',
                    marker_color='cornflowerblue',
                    text=top_cities['total_deals'],  # Добавление меток
                    textposition='outside',  # Позиция меток
                ),
                secondary_y=False
            )
            
            # Линейный график коэффициента конверсии (правая ось)
            fig_city.add_trace(
                go.Scatter(
                    x=top_cities.index,
                    y=top_cities['conversion_rate'],
                    name='Conversion Rate',
                    mode='lines+markers',
                    line=dict(color='magenta', dash="dash"),
                ),
                secondary_y=True
            )
            
            # Настройка осей
            fig_city.update_layout(
                title='Top 10 Cities: Deals and Conversion Rates',
                xaxis=dict(title='City', tickangle=45),
                yaxis = dict(
                    title="Number of Deals",
                    titlefont=dict(color="steelblue"),
                    tickfont=dict(color="steelblue"),
                    zeroline=False,
                    showgrid=False,
                ),
                yaxis2 = dict(
                    title="Conversion Rate",
                    titlefont=dict(color="magenta"),
                    tickfont=dict(color="magenta"),
                    zeroline=False,
                    showgrid=False,
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="white",
                height=500
            )

            # Отображение графика в Streamlit
            st.plotly_chart(fig_city, use_container_width=True)


            st.subheader("Распределение сделок по странам")

            # Радиокнопки для выбора включения/исключения Германии
            include_germany = st.radio(
                "Включить Германию в анализ?",
                ("Да", "Нет")
            )
            
            # Фильтрация данных на основе выбора
            if include_germany == "Нет":
                df_filtered = df[df['Country'] != 'Germany']
            else:
                df_filtered = df
            
            # Агрегация данных по странам
            country_analysis = df_filtered.groupby('Country').agg(
                total_deals=('is_successful', 'size'),
                successful_deals=('is_successful', 'sum')
            )
            country_analysis['conversion_rate'] = (country_analysis['successful_deals'] / country_analysis['total_deals']).round(2)
            
            # Сортировка по количеству сделок для анализа топ-городов
            top_countries = country_analysis.sort_values(by='total_deals', ascending=False).head(10)
            
            # Создание графика с двойной осью
            fig_countries = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Гистограмма количества сделок (левая ось)
            fig_countries.add_trace(
                go.Bar(
                    x=top_countries.index,
                    y=top_countries['total_deals'],
                    name='Total Deals',
                    marker_color='skyblue',
                    text=top_countries['total_deals'],  # Добавление меток
                    textposition='outside',  # Позиция меток
                ),
                secondary_y=False
            )
            
            # Линейный график коэффициента конверсии (правая ось)
            fig_countries.add_trace(
                go.Scatter(
                    x=top_countries.index,
                    y=top_countries['conversion_rate'],
                    name='Conversion Rate',
                    mode='lines+markers',
                    line=dict(color='green', dash="dash"),
                ),
                secondary_y=True
            )
            
            # Настройка осей
            fig_countries.update_layout(
                title='Top 10 Countries: Deals and Conversion Rates',
                xaxis=dict(title='Country', tickangle=45),
                yaxis=dict(
                    title="Number of Deals",
                    titlefont=dict(color="steelblue"),
                    tickfont=dict(color="steelblue"),
                    zeroline=False,
                    showgrid=False,
                ),
                yaxis2=dict(
                    title="Conversion Rate",
                    titlefont=dict(color="green"),
                    tickfont=dict(color="green"),
                    zeroline=False,
                    showgrid=False,
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="white",
                height=500
            )
            
            # Отображение графика в Streamlit
            st.plotly_chart(fig_countries, use_container_width=True)
            
            # Заголовок для раздела
            st.title("Распределение сделок на карте")
            
            # Загрузка HTML-файла карты
            with open("deals_map.html", "r", encoding="utf-8") as f:
                map_html = f.read()
            
            # Встраивание карты в дашборд
            components.html(map_html, height=600, scrolling=False)



        # Вкладка 2: 
        with tab2:
        
            st.subheader("Анализ влияние уровня знания немецкого языка на успешность сделок в разных городах")
 
            # Копируем DataFrame deals во временный df
            df = data.copy()

            # Категоризация успешности сделок
            df['is_successful'] = (df['Months of study'].notnull()).astype(int)
            
            # Агрегация данных по уровню Level of Deutsch
            level_analysis = df.groupby('Level of Deutsch').agg(
                total_deals=('is_successful', 'size'),  # Общее количество сделок
                successful_deals=('is_successful', 'sum')  # Количество успешных сделок
            )
            
            # Расчет успешности
            level_analysis['success_rate'] = (level_analysis['successful_deals'] / level_analysis['total_deals']).round(2)
            
            # **Добавляем тоггл-кнопку для выбора сортировки**
            sort_by = st.radio(
                "Сортировать по:",
                ('success_rate', 'total_deals'),
                index=1,
                format_func=lambda x: "Успешность сделок" if x == 'success_rate' else "Общее количество сделок"
            )
            
            # Сортировка данных по выбранному параметру
            level_analysis_sorted = level_analysis.sort_values(by=sort_by, ascending=False)
            
            # Данные для графика
            levels = level_analysis_sorted.index
            success_rate = level_analysis_sorted['success_rate']
            total_deals = level_analysis_sorted['total_deals']
            
            # Создание фигуры Plotly
            fig = go.Figure()
            
            # Добавление бара для успешности сделок
            fig.add_trace(
                go.Bar(
                    x=levels,
                    y=success_rate,
                    name='Success Rate',
                    marker_color='royalblue',
                    opacity=0.7,
                    yaxis='y1',
                    text=level_analysis['successful_deals'],  # Добавление меток
                    textposition='inside',  # Позиция меток
                    textfont=dict(color='deepskyblue'),  # Цвет текста
                )
            )
            
            # Добавление линии для общего количества сделок
            fig.add_trace(
                go.Scatter(
                    x=levels,
                    y=total_deals,
                    name='Total Deals',
                    mode='lines+markers+text',
                    line=dict(color='violet', width=2, dash='dot'),
                    yaxis='y2',
                    text=total_deals,  # Значения для отображения
                    textposition='top center',  # Позиция текста
                    textfont=dict(color='violet'),  # Цвет текста
                )
            )
            
            # Настройки осей и оформление
            fig.update_layout(
                title='Успешность сделок и общее количество по уровням знания языка',
                xaxis=dict(title='Level of Deutsch'),
                yaxis=dict(
                    title='Success Rate',
                    range=[0, 1],
                    titlefont=dict(color='royalblue'),
                    tickfont=dict(color='royalblue'),
                    showgrid=False
                ),
                yaxis2=dict(
                    title='Total Deals',
                    overlaying='y',
                    side='right',
                    titlefont=dict(color='violet'),
                    tickfont=dict(color='violet'),
                    showgrid=False,
                    zeroline=False
                ),
                legend=dict(
                    x=0.5,
                    y=1.1,
                    orientation="h"
                ),
                bargap=0.2,
                plot_bgcolor='white',
                hovermode='x unified',
            )
            
            # Добавление сетки для удобства
            # fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgrey')
            # fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgrey')
            
            # Встраивание графика в Streamlit
            st.plotly_chart(fig, use_container_width=True)



            # Рассчитать среднюю успешность сделок по уровням и городам
            city_level_success = df.groupby(['City', 'Level of Deutsch'])['is_successful'].mean().reset_index()
            
            # Отобрать топ-10 городов с наибольшей успешностью по каждому уровню
            top_cities = city_level_success.groupby('Level of Deutsch').apply(
                lambda x: x.nlargest(10, 'is_successful')
            ).reset_index(drop=True)

            fig3 = px.bar(
                top_cities,
                x='is_successful',
                y='City',
                facet_col='Level of Deutsch',
                orientation='h',
                title="Успешность сделок в городах по уровням знания языка",
                color='City',  # Добавляем разделение цвета по городам
                color_discrete_sequence=px.colors.qualitative.Set2
                # color_discrete_sequence=px.px.colors.sequential.Viridis
                # color_discrete_sequence=px.colors.qualitative.Plotly
            )

            # Убираем "Level of Deutsch=" из заголовков фасетов
            fig3.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))

            # Убираем только названия осей X, оставляя значения
            fig3.for_each_xaxis(lambda xaxis: xaxis.update(title_text=''))


            # Добавляем аннотацию как глобальное название оси X
            fig3.add_annotation(
                text="Success Rate",
                x=0.5, y=-0.11,  # Расположение относительно графика
                showarrow=False,
                xref="paper", yref="paper",  # Координаты в масштабе всего графика
                font=dict(size=14)
            )
            
            fig3.update_layout(
                title_x=0,
                height=800,
                plot_bgcolor="white",
                # showlegend=False
                # margin=dict(t=50, b=80)  # Увеличиваем отступ снизу для аннотации
            )

            st.plotly_chart(fig3, use_container_width=True)



            city_level_success = df.groupby(['City', 'Level of Deutsch']).agg(
                is_successful=('is_successful', 'mean'),
                total_deals=('is_successful', 'size')  # Добавляем количество сделок
            ).reset_index()

            fig4 = px.scatter(
                city_level_success,
                x='is_successful',
                y='City',
                size='total_deals',  # Размер пузырька по количеству сделок
                color='Level of Deutsch',
                title="Успешность сделок в городах с учетом уровня языка",
                size_max=15,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            
            fig4.update_layout(
                xaxis_title="Success Rate",
                yaxis_title="City",
                plot_bgcolor="white"
            )

            st.plotly_chart(fig4, use_container_width=True)




