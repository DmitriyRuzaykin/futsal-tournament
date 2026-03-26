import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import os

# Настройка страницы
st.set_page_config(
    page_title="Кубок Elita по футзалу",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
<style>
    /* Общие стили для карточек матчей */
    .match-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #2e7d32;
    }
    
    .match-card.scheduled {
        border-left-color: #ed6c02;
    }
    
    .match-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 14px;
        color: #666;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .match-teams {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .team-name {
        flex: 2;
        font-size: 16px;
    }
    
    .team-name.left {
        text-align: right;
        padding-right: 10px;
    }
    
    .team-name.right {
        text-align: left;
        padding-left: 10px;
    }
    
    .match-score {
        flex: 1;
        font-size: 24px;
        font-weight: bold;
        background: white;
        padding: 5px 15px;
        border-radius: 25px;
        margin: 0 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .match-status {
        text-align: center;
        margin-top: 12px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 20px;
        border-radius: 25px;
        color: white;
        font-size: 14px;
        font-weight: bold;
    }
    
    .status-badge.completed {
        background-color: #2e7d32;
    }
    
    .status-badge.scheduled {
        background-color: #ed6c02;
    }
    
    .match-info {
        text-align: center;
        margin-top: 8px;
        font-size: 12px;
        color: #666;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 768px) {
        .team-name {
            font-size: 14px;
        }
        
        .match-score {
            font-size: 18px;
            padding: 4px 10px;
        }
        
        .match-header {
            font-size: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)


# АДАПТИВНЫЙ ДИЗАЙН ДЛЯ МОБИЛЬНЫХ УСТРОЙСТВ
st.markdown("""
<style>
    /* Мета-теги для мобильных устройств */
    meta[name="viewport"] {
        content: "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes";
    }
    
    /* Общие стили для мобильных устройств */
    @media (max-width: 768px) {
        /* Уменьшаем отступы */
        .block-container {
            padding: 1rem 0.5rem !important;
        }
        
        /* Улучшаем читаемость таблицы */
        .dataframe {
            font-size: 12px !important;
        }
        
        .dataframe td, .dataframe th {
            padding: 4px 2px !important;
            white-space: nowrap;
        }
        
        /* Делаем кнопки больше для удобного нажатия */
        .stButton button {
            min-height: 44px;
            font-size: 16px;
            width: 100%;
        }
        
        /* Улучшаем отображение метрик */
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        
        /* Адаптация для радио-кнопок */
        .stRadio {
            margin-bottom: 15px;
        }
        
        .stRadio div {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .stRadio label {
            flex: 1 1 auto;
            text-align: center;
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 8px;
            margin: 0 !important;
        }
        
        /* Адаптация для selectbox */
        .stSelectbox {
            margin-bottom: 15px;
        }
        
        /* Скрываем лишние колонки в таблице на мобильных */
        .dataframe th:nth-child(4),
        .dataframe td:nth-child(4),
        .dataframe th:nth-child(5),
        .dataframe td:nth-child(5),
        .dataframe th:nth-child(6),
        .dataframe td:nth-child(6) {
            display: none;
        }
    }
    
    /* Стили для карточек матчей */
    .match-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #2e7d32;
    }
    
    .match-card.scheduled {
        border-left-color: #ed6c02;
    }
    
    .match-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 14px;
        color: #666;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .match-teams {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .team-name {
        flex: 2;
        font-size: 16px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .team-name.left {
        text-align: right;
        padding-right: 10px;
    }
    
    .team-name.right {
        text-align: left;
        padding-left: 10px;
    }
    
    .match-score {
        flex: 1;
        font-size: 24px;
        font-weight: bold;
        background: white;
        padding: 5px 15px;
        border-radius: 25px;
        margin: 0 5px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .match-status {
        text-align: center;
        margin-top: 12px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 20px;
        border-radius: 25px;
        color: white;
        font-size: 14px;
        font-weight: bold;
    }
    
    .status-badge.completed {
        background-color: #2e7d32;
    }
    
    .status-badge.scheduled {
        background-color: #ed6c02;
    }
    
    .match-info {
        display: flex;
        justify-content: center;
        gap: 20px;
        font-size: 13px;
        color: #666;
        margin-top: 8px;
    }
    
    /* Адаптация для сайдбара на мобильных */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            min-width: 80% !important;
            width: 80% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("🏆 Кубок Elita по футзалу")
st.subheader("Волжский муниципальный район")
st.markdown("---")

# Функция загрузки данных из локального JSON файла
@st.cache_data(ttl=60)  # Кэшируем на 1 минуту, чтобы видеть изменения быстрее
def load_tournament_data():
    """Загружает данные турнира из локального файла data/tournament.json"""
    try:
        file_path = 'data/tournament.json'
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            st.error(f"Файл {file_path} не найден!")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Показываем информацию о загрузке
        completed = sum(1 for m in data['matches'] if m['status'] == 'completed')
        st.sidebar.success(f"✅ Данные загружены из файла")
        st.sidebar.write(f"📊 Сыграно матчей: {completed}")
        st.sidebar.write(f"🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        return data
    except FileNotFoundError:
        st.error("Файл data/tournament.json не найден!")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Ошибка в формате JSON файла: {e}")
        return None
    except Exception as e:
        st.error(f"Ошибка при загрузке: {e}")
        return None

# Функция для расчета турнирной таблицы
def calculate_standings(matches, group_teams):
    """Рассчитывает турнирную таблицу для группы"""
    
    standings = {}
    for team in group_teams:
        standings[team] = {
            'Команда': team,
            'И': 0,
            'В': 0,
            'Н': 0,
            'П': 0,
            'ЗМ': 0,
            'ПМ': 0,
            'О': 0
        }
    
    for match in matches:
        if match['status'] == 'completed' and match['score1'] is not None and match['score2'] is not None:
            team1 = match['team1']
            team2 = match['team2']
            score1 = match['score1']
            score2 = match['score2']
            
            if team1 not in standings or team2 not in standings:
                continue
            
            standings[team1]['И'] += 1
            standings[team1]['ЗМ'] += score1
            standings[team1]['ПМ'] += score2
            
            standings[team2]['И'] += 1
            standings[team2]['ЗМ'] += score2
            standings[team2]['ПМ'] += score1
            
            if score1 > score2:
                standings[team1]['В'] += 1
                standings[team1]['О'] += 3
                standings[team2]['П'] += 1
            elif score1 < score2:
                standings[team2]['В'] += 1
                standings[team2]['О'] += 3
                standings[team1]['П'] += 1
            else:
                standings[team1]['Н'] += 1
                standings[team1]['О'] += 1
                standings[team2]['Н'] += 1
                standings[team2]['О'] += 1
    
    df = pd.DataFrame(list(standings.values()))
    if not df.empty:
        df['+/-'] = df['ЗМ'] - df['ПМ']
        df = df.sort_values(['О', '+/-', 'ЗМ'], ascending=False).reset_index(drop=True)
    
    return df

# Загружаем данные
data = load_tournament_data()

if data:
    # Создаем вкладки (только просмотр, без администрирования)
    tab1, tab2 = st.tabs([
        "📊 Турнирная таблица", 
        "⚔️ Матчи"
    ])
    
    # Вкладка 1: Турнирная таблица
    with tab1:
        st.header("Турнирная таблица - Групповой этап")
        
        group_choice = st.radio(
            "Выберите группу:",
            ["Группа A", "Группа B"],
            horizontal=True
        )
        
        if group_choice == "Группа A":
            group_teams = data['groups']['A']
            group_matches = [m for m in data['matches'] if m['group'] == 'A']
            df_standings = calculate_standings(group_matches, group_teams)
        else:
            group_teams = data['groups']['B']
            group_matches = [m for m in data['matches'] if m['group'] == 'B']
            df_standings = calculate_standings(group_matches, group_teams)
        
        if not df_standings.empty:
            df_standings.insert(0, 'Место', range(1, len(df_standings) + 1))
            
            def highlight_top(row):
                if row.name == 0:
                    return ['background-color: #90EE90'] * len(row)
                elif row.name == len(df_standings) - 1:
                    return ['background-color: #FFB6C1'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = df_standings.style.apply(highlight_top, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("Нет данных для отображения")
    
    # Вкладка 2: Матчи (исправленная версия)
    with tab2:
        st.header("Расписание матчей - Групповой этап")
        
        # Фильтры
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tour_filter = st.selectbox(
                "Тур:",
                ["Все", "1 тур", "2 тур", "3 тур", "4 тур", "5 тур"]
            )
        
        with col2:
            group_filter = st.selectbox(
                "Группа:",
                ["Все", "A", "B"]
            )
        
        with col3:
            status_filter = st.selectbox(
                "Статус:",
                ["Все", "Завершенные", "Предстоящие"]
            )
        
        # Фильтруем матчи
        filtered_matches = data['matches'].copy()
        
        if tour_filter != "Все":
            tour_num = int(tour_filter.split()[0])
            filtered_matches = [m for m in filtered_matches if m['tour'] == tour_num]
        
        if group_filter != "Все":
            filtered_matches = [m for m in filtered_matches if m['group'] == group_filter]
        
        if status_filter == "Завершенные":
            filtered_matches = [m for m in filtered_matches if m['status'] == 'completed']
        elif status_filter == "Предстоящие":
            filtered_matches = [m for m in filtered_matches if m['status'] == 'scheduled']
        
        # Сортируем по дате и туру
        filtered_matches.sort(key=lambda x: (x['date'], x['time']))
        
        # Отображаем матчи в виде карточек
        if filtered_matches:
            current_tour = None
            for match in filtered_matches:
                if current_tour != match['tour']:
                    current_tour = match['tour']
                    st.subheader(f"⚔️ {current_tour} тур")
                
                # Определяем цвета в зависимости от статуса
                if match['status'] == 'completed':
                    bg_color = "#e8f5e9"
                    border_color = "#2e7d32"
                    status_text = "✅ Завершен"
                    status_bg = "#2e7d32"
                else:
                    bg_color = "#fff3e0"
                    border_color = "#ed6c02"
                    status_text = "⏳ Предстоит"
                    status_bg = "#ed6c02"
                
                # Форматируем дату
                date_obj = datetime.strptime(match['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d.%m.%Y')
                
                # Отображаем счет
                if match['score1'] is not None and match['score2'] is not None:
                    score_display = f"{match['score1']} : {match['score2']}"
                else:
                    score_display = "? : ?"
                
                # Используем columns для создания карточки (более надежно, чем HTML)
                with st.container():
                    # Внешний контейнер с фоном
                    st.markdown(f"""
                    <div style="
                        background-color: {bg_color};
                        border-left: 5px solid {border_color};
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 12px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; color: #666; font-size: 14px;">
                            <span>⏱️ {match['time']}</span>
                            <span>📅 {formatted_date}</span>
                            <span>Группа {match['group']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 15px 0;">
                            <div style="flex: 2; text-align: right; font-weight: bold; font-size: 16px; padding-right: 15px;">
                                {match['team1']}
                            </div>
                            <div style="flex: 1; text-align: center; background-color: white; padding: 8px 0; border-radius: 25px; font-weight: bold; font-size: 20px;">
                                {score_display}
                            </div>
                            <div style="flex: 2; text-align: left; font-weight: bold; font-size: 16px; padding-left: 15px;">
                                {match['team2']}
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 10px;">
                            <span style="background-color: {status_bg}; color: white; padding: 5px 20px; border-radius: 20px; font-size: 14px;">
                                {status_text}
                            </span>
                        </div>
                        <div style="text-align: center; margin-top: 8px; color: #666; font-size: 12px;">
                            ⚽ Тур {match['tour']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Нет матчей, соответствующих выбранным фильтрам")
    
    # Статистика в сайдбаре
    with st.sidebar:
        st.header("📊 Статистика турнира")
        
        completed_matches = [m for m in data['matches'] if m['status'] == 'completed']
        scheduled_matches = [m for m in data['matches'] if m['status'] == 'scheduled']
        
        total_goals = 0
        for m in completed_matches:
            if m['score1'] is not None and m['score2'] is not None:
                total_goals += m['score1'] + m['score2']
        
        st.metric("Всего матчей", len(data['matches']))
        st.metric("Сыграно матчей", len(completed_matches))
        st.metric("Осталось матчей", len(scheduled_matches))
        st.metric("Всего голов", total_goals)
        
        if completed_matches:
            st.divider()
            st.subheader("Последние результаты")
            last_matches = sorted(completed_matches, key=lambda x: x['date'], reverse=True)[:3]
            for match in last_matches:
                date_obj = datetime.strptime(match['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d.%m')
                st.write(f"📅 {formatted_date}: {match['team1']} {match['score1']}:{match['score2']} {match['team2']}")
        
        st.divider()
        st.caption("📝 Для изменения результатов редактируйте файл:")
        st.code("data/tournament.json", language="bash")
        st.caption("🔄 Изменения появятся через 1 минуту")

else:
    st.error("Не удалось загрузить данные турнира. Проверьте файл data/tournament.json")