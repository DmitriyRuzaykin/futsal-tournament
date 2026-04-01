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
    
    /* Стили для рамки заголовка как на QA Compass */
    .hero-frame {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 3px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .hero-content {
        background: white;
        border-radius: 18px;
        padding: 30px 20px;
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        display: inline-block;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Адаптация для мобильных */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 1.5rem;
        }
        
        .hero-subtitle {
            font-size: 0.85rem;
        }
        
        .hero-content {
            padding: 20px 15px;
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

# Красивая рамка с заголовком как на QA Compass
st.markdown("""
<div class="hero-frame">
    <div class="hero-content">
        <div class="hero-title">
            🏆 Кубок Elita по футзалу 2026
        </div>
        <div class="hero-subtitle">
            Волжский муниципальный округ
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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

# Функция для расчета турнирной таблицы с учетом личных встреч
def calculate_standings(matches, group_teams):
    """Рассчитывает турнирную таблицу для группы с учетом личных встреч"""
    
    # Создаем словарь для статистики команд
    standings = {}
    for team in group_teams:
        standings[team] = {
            'Команда': team,
            'И': 0,  # Игры
            'В': 0,  # Победы
            'Н': 0,  # Ничьи
            'П': 0,  # Поражения
            'ЗМ': 0,  # Забито
            'ПМ': 0,  # Пропущено
            'О': 0   # Очки
        }
    
    # Словарь для хранения результатов личных встреч
    # Формат: head_to_head[(team1, team2)] = {'points': points_team1, 'gd': goal_diff_team1}
    head_to_head = {}
    
    # Обрабатываем каждый матч
    for match in matches:
        if match['status'] == 'completed' and match['score1'] is not None and match['score2'] is not None:
            team1 = match['team1']
            team2 = match['team2']
            score1 = match['score1']
            score2 = match['score2']
            
            if team1 not in standings or team2 not in standings:
                continue
            
            # Обновляем общую статистику
            standings[team1]['И'] += 1
            standings[team1]['ЗМ'] += score1
            standings[team1]['ПМ'] += score2
            
            standings[team2]['И'] += 1
            standings[team2]['ЗМ'] += score2
            standings[team2]['ПМ'] += score1
            
            # Определяем результат
            if score1 > score2:
                standings[team1]['В'] += 1
                standings[team1]['О'] += 3
                standings[team2]['П'] += 1
                # Для личной встречи
                head_to_head[(team1, team2)] = {'points': 3, 'gd': score1 - score2}
                head_to_head[(team2, team1)] = {'points': 0, 'gd': score2 - score1}
            elif score1 < score2:
                standings[team2]['В'] += 1
                standings[team2]['О'] += 3
                standings[team1]['П'] += 1
                # Для личной встречи
                head_to_head[(team1, team2)] = {'points': 0, 'gd': score1 - score2}
                head_to_head[(team2, team1)] = {'points': 3, 'gd': score2 - score1}
            else:
                standings[team1]['Н'] += 1
                standings[team1]['О'] += 1
                standings[team2]['Н'] += 1
                standings[team2]['О'] += 1
                # Для личной встречи
                head_to_head[(team1, team2)] = {'points': 1, 'gd': 0}
                head_to_head[(team2, team1)] = {'points': 1, 'gd': 0}
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(list(standings.values()))
    
    if not df.empty:
        df['+/-'] = df['ЗМ'] - df['ПМ']
        
        # Функция для сравнения команд при равенстве очков
        def compare_teams(team1, team2):
            """Сравнивает две команды по очкам, личным встречам, разнице мячей"""
            # Получаем очки
            points1 = df.loc[df['Команда'] == team1, 'О'].values[0]
            points2 = df.loc[df['Команда'] == team2, 'О'].values[0]
            
            if points1 != points2:
                return points1 > points2
            
            # Если очки равны, проверяем личную встречу
            if (team1, team2) in head_to_head:
                h2h_points1 = head_to_head[(team1, team2)]['points']
                h2h_points2 = head_to_head[(team2, team1)]['points']
                
                if h2h_points1 != h2h_points2:
                    return h2h_points1 > h2h_points2
                
                # Если очки в личных встречах равны, проверяем разницу мячей
                h2h_gd1 = head_to_head[(team1, team2)]['gd']
                h2h_gd2 = head_to_head[(team2, team1)]['gd']
                
                if h2h_gd1 != h2h_gd2:
                    return h2h_gd1 > h2h_gd2
            
            # Если личная встреча не игралась или ничья, сравниваем общую разницу мячей
            gd1 = df.loc[df['Команда'] == team1, '+/-'].values[0]
            gd2 = df.loc[df['Команда'] == team2, '+/-'].values[0]
            
            if gd1 != gd2:
                return gd1 > gd2
            
            # Если все равны, сравниваем забитые мячи
            goals1 = df.loc[df['Команда'] == team1, 'ЗМ'].values[0]
            goals2 = df.loc[df['Команда'] == team2, 'ЗМ'].values[0]
            
            return goals1 > goals2
        
        # Сортируем команды
        teams = df['Команда'].tolist()
        
        # Пузырьковая сортировка с использованием нашего компаратора
        n = len(teams)
        for i in range(n):
            for j in range(0, n - i - 1):
                if not compare_teams(teams[j], teams[j + 1]):
                    teams[j], teams[j + 1] = teams[j + 1], teams[j]
        
        # Создаем отсортированный DataFrame
        sorted_teams = []
        for team in teams:
            sorted_teams.append(standings[team])
        
        df = pd.DataFrame(sorted_teams)
        df['+/-'] = df['ЗМ'] - df['ПМ']
        df = df.reset_index(drop=True)
    
    return df

# Функция для загрузки названий команд по их позициям
def get_team_by_position(groups, group_letter, position):
    """Возвращает название команды по группе и позиции (1-5)"""
    # Сначала нужно получить актуальную турнирную таблицу для группы
    if group_letter == "A":
        group_teams = groups['A']
        group_matches = [m for m in data['matches'] if m['group'] == 'A']
        df = calculate_standings(group_matches, group_teams)
    else:
        group_teams = groups['B']
        group_matches = [m for m in data['matches'] if m['group'] == 'B']
        df = calculate_standings(group_matches, group_teams)
    
    if not df.empty and len(df) >= position:
        return df.iloc[position - 1]['Команда']
    return f"{group_letter}{position}"

# Загружаем данные
data = load_tournament_data()
  
if data:
    # Создаем вкладки
    tab1, tab2, tab3 = st.tabs([
    "📊 Турнирная таблица", 
    "⚔️ Матчи группового этапа",
    "🏆 Плей-офф"
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
    
    # Вкладка 2: Матчи
    with tab2:
        st.header("Расписание матчей")
        
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
    
    # Вкладка 3: Стыковые матчи
    with tab3:
        st.header("🏆 Плей-офф")
        # st.markdown("Игры на вылет")
        
        # Проверяем наличие стыковых матчей в данных
        if 'playoff_matches' in data and data['playoff_matches']:
            for match in data['playoff_matches']:
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
                
                # Создаем карточку матча
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
                        <span>{match.get('description', 'Стыковой матч')}</span>
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
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Информация о стыковых матчах появится позже")
    
    # Статистика в сайдбаре
    with st.sidebar:
        st.header("📊 Статистика турнира")
        
        # Собираем все матчи (групповой этап + плей-офф)
        all_matches = data['matches'].copy()
        if 'playoff_matches' in data:
            all_matches.extend(data['playoff_matches'])
        
        completed_matches = [m for m in all_matches if m['status'] == 'completed']
        scheduled_matches = [m for m in all_matches if m['status'] == 'scheduled']
        
        total_goals = 0
        for m in completed_matches:
            if m['score1'] is not None and m['score2'] is not None:
                total_goals += m['score1'] + m['score2']
        
        # Основные метрики
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего матчей", len(all_matches))
            st.metric("Сыграно", len(completed_matches))
        with col2:
            st.metric("Осталось", len(scheduled_matches))
            st.metric("Всего голов", total_goals)
        
        # Статистика по этапам
        st.divider()
        st.subheader("📈 По этапам")
        
        # Групповой этап
        group_matches = [m for m in data['matches'] if m['status'] == 'completed']
        group_goals = sum(m['score1'] + m['score2'] for m in group_matches if m['score1'] is not None)
        
        # Плей-офф (включая стыковые матчи)
        playoff_matches = []
        if 'playoff_matches' in data:
            playoff_matches = [m for m in data['playoff_matches'] if m['status'] == 'completed']
        playoff_goals = sum(m['score1'] + m['score2'] for m in playoff_matches if m['score1'] is not None)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Групповой этап", f"{len(group_matches)} матчей")
            st.metric("Голов", group_goals)
        with col2:
            st.metric("Плей-офф", f"{len(playoff_matches)} матчей")
            st.metric("Голов", playoff_goals)
        
        # Последние результаты
        if completed_matches:
            st.divider()
            st.subheader("📋 Последние результаты")
            last_matches = sorted(completed_matches, key=lambda x: x['date'], reverse=True)[:5]
            for match in last_matches:
                date_obj = datetime.strptime(match['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d.%m')
                
                # Определяем тип матча
                if match.get('stage') == 'playoff' or match.get('description', '').startswith(('Стыковой', 'Игра', 'Матч')):
                    match_icon = "🏆"
                else:
                    match_icon = "⚽"
                
                # Форматируем описание для плей-офф
                if match.get('description'):
                    match_desc = match['description']
                else:
                    match_desc = f"{match_icon} {formatted_date}"
                
                st.write(f"{match_icon} {formatted_date}: {match['team1']} {match['score1']}:{match['score2']} {match['team2']}")
        
        # Добавляем информацию о статусе турнира
        st.divider()
        if len(completed_matches) == len(all_matches):
            st.success("🏆 Турнир завершен!")
        elif len(completed_matches) > 0:
            remaining = len(scheduled_matches)
            st.info(f"⏳ Осталось сыграть {remaining} матчей")
        else:
            st.info("🎯 Турнир еще не начался")

else:
    st.error("Не удалось загрузить данные турнира. Проверьте файл data/tournament.json")