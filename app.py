import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="Кубок Elita по футзалу",
    page_icon="⚽",
    layout="wide"
)

# Заголовок
st.title("🏆 Кубок Elita по футзалу")
st.subheader("Волжский муниципальный район")
st.markdown("---")

# Функция загрузки данных из JSON
@st.cache_data
def load_tournament_data():
    """Загружает данные турнира из JSON файла"""
    try:
        with open('data/tournament.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        st.error("Файл data/tournament.json не найден!")
        return None
    except json.JSONDecodeError:
        st.error("Ошибка в формате JSON файла!")
        return None

# Функция сохранения данных в JSON
def save_tournament_data(data):
    """Сохраняет данные турнира в JSON файл"""
    try:
        with open('data/tournament.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        # Очищаем кэш после сохранения
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Ошибка при сохранении: {e}")
        return False

# Функция для расчета турнирной таблицы
def calculate_standings(matches, group_teams):
    """Рассчитывает турнирную таблицу для группы"""
    
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
    
    # Обрабатываем каждый матч
    for match in matches:
        if match['status'] == 'completed' and match['score1'] is not None and match['score2'] is not None:
            team1 = match['team1']
            team2 = match['team2']
            score1 = match['score1']
            score2 = match['score2']
            
            # Обновляем статистику для команды 1
            standings[team1]['И'] += 1
            standings[team1]['ЗМ'] += score1
            standings[team1]['ПМ'] += score2
            
            # Обновляем статистику для команды 2
            standings[team2]['И'] += 1
            standings[team2]['ЗМ'] += score2
            standings[team2]['ПМ'] += score1
            
            # Определяем результат
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
    
    # Преобразуем в DataFrame и сортируем по очкам
    df = pd.DataFrame(list(standings.values()))
    df['+/-'] = df['ЗМ'] - df['ПМ']
    df = df.sort_values(['О', '+/-', 'ЗМ'], ascending=False).reset_index(drop=True)
    
    return df

# Функция для проверки пароля (безопасная версия)
def check_password():
    """Возвращает True если пароль введен правильно"""
    
    def get_admin_password():
        """Получает пароль из разных источников"""
        # Пробуем из Streamlit secrets
        try:
            if "admin_password" in st.secrets:
                return st.secrets["admin_password"]
        except:
            pass
        
        # Пробуем из переменных окружения
        env_password = os.getenv("ADMIN_PASSWORD")
        if env_password:
            return env_password
        
        # Если ничего нет, показываем ошибку
        st.error("Пароль администратора не настроен! Добавьте его в .env или .streamlit/secrets.toml")
        return None
    
    def password_entered():
        correct_password = get_admin_password()
        
        if correct_password is None:
            st.session_state["password_correct"] = False
        elif st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.text_input(
            "Введите пароль администратора:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Введите пароль администратора:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Неверный пароль")
        return False
    else:
        return True

# Загружаем данные
data = load_tournament_data()

if data:
    # Создаем вкладки
    tab1, tab2, tab3 = st.tabs([
        "📊 Турнирная таблица", 
        "⚔️ Матчи",
        "🔧 Администрирование"
    ])
    
    # Вкладка 1: Турнирная таблица
    with tab1:
        st.header("Турнирная таблица - Групповой этап")
        
        # Выбор группы
        group_choice = st.radio(
            "Выберите группу:",
            ["Группа A", "Группа B"],
            horizontal=True
        )
        
        if group_choice == "Группа A":
            group_teams = data['groups']['A']
            group_matches = [m for m in data['matches'] if m['group'] == 'A']
            df_standings = calculate_standings(group_matches, group_teams)
            
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
            group_teams = data['groups']['B']
            group_matches = [m for m in data['matches'] if m['group'] == 'B']
            df_standings = calculate_standings(group_matches, group_teams)
            
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
    
    # Вкладка 2: Матчи
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
        
        # Отображаем матчи
        if filtered_matches:
            current_tour = None
            for match in filtered_matches:
                if current_tour != match['tour']:
                    current_tour = match['tour']
                    st.subheader(f"⚔️ {current_tour} тур")
                
                with st.container():
                    cols = st.columns([2, 1, 1, 2, 2, 1])
                    
                    with cols[0]:
                        st.write(f"**{match['team1']}**")
                    
                    with cols[1]:
                        if match['status'] == 'completed' and match['score1'] is not None:
                            st.write(f"**{match['score1']}**")
                        else:
                            st.write("**-**")
                    
                    with cols[2]:
                        if match['status'] == 'completed' and match['score2'] is not None:
                            st.write(f"**{match['score2']}**")
                        else:
                            st.write("**-**")
                    
                    with cols[3]:
                        st.write(f"**{match['team2']}**")
                    
                    with cols[4]:
                        date_obj = datetime.strptime(match['date'], '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%d.%m')
                        st.write(f"📅 {formatted_date} {match['time']}")
                    
                    with cols[5]:
                        st.write(f"Группа {match['group']}")
                    
                    st.markdown("---")
        else:
            st.info("Нет матчей, соответствующих выбранным фильтрам")
    
    # Вкладка 3: Администрирование
    with tab3:
        st.header("🔧 Администрирование турнира")
        
        if check_password():
            st.success("✅ Доступ разрешен")
            
            # Создаем две колонки для выбора действия
            action = st.radio(
                "Выберите действие:",
                ["📝 Ввод результатов", "🔄 Сброс результатов"],
                horizontal=True
            )
            
            if action == "📝 Ввод результатов":
                st.subheader("Ввод результатов матчей")
                
                # Показываем все матчи, сортируем по дате
                all_matches = sorted(data['matches'], key=lambda x: (x['date'], x['time']))
                
                # Создаем список для выбора
                match_options = {}
                for match in all_matches:
                    date_obj = datetime.strptime(match['date'], '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                    status = "✅" if match['status'] == 'completed' else "⏳"
                    key = f"{status} {match['tour']} тур: {match['team1']} - {match['team2']} ({formatted_date} {match['time']})"
                    match_options[key] = match
                
                selected_match_key = st.selectbox(
                    "Выберите матч:",
                    options=list(match_options.keys()),
                    key="input_match"
                )
                
                match = match_options[selected_match_key]
                
                # Форма для ввода результата
                with st.form(key="score_form"):
                    st.write(f"**{match['team1']}** vs **{match['team2']}**")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        score1 = st.number_input(
                            match['team1'], 
                            min_value=0, 
                            max_value=50, 
                            value=match['score1'] if match['score1'] is not None else 0,
                            step=1
                        )
                    
                    with col2:
                        st.markdown("<h3 style='text-align: center; padding-top: 30px;'>:</h3>", 
                                  unsafe_allow_html=True)
                    
                    with col3:
                        score2 = st.number_input(
                            match['team2'], 
                            min_value=0, 
                            max_value=50, 
                            value=match['score2'] if match['score2'] is not None else 0,
                            step=1
                        )
                    
                    submitted = st.form_submit_button("💾 Сохранить результат", use_container_width=True)
                    
                    if submitted:
                        for m in data['matches']:
                            if m['id'] == match['id']:
                                m['score1'] = score1
                                m['score2'] = score2
                                m['status'] = 'completed'
                                break
                        
                        if save_tournament_data(data):
                            st.success("✅ Результат сохранен!")
                            st.rerun()
            
            else:  # Сброс результатов
                st.subheader("🔄 Сброс результатов")
                st.warning("⚠️ Здесь вы можете отменить результат сыгранного матча")
                
                # Показываем только сыгранные матчи
                completed_matches = [m for m in data['matches'] if m['status'] == 'completed']
                
                if completed_matches:
                    st.write(f"**Найдено сыгранных матчей:** {len(completed_matches)}")
                    
                    for match in completed_matches:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{match['tour']} тур:** {match['team1']} {match['score1']}:{match['score2']} {match['team2']}")
                        with col2:
                            if st.button(f"🔄 Сбросить", key=f"reset_{match['id']}"):
                                for m in data['matches']:
                                    if m['id'] == match['id']:
                                        m['score1'] = None
                                        m['score2'] = None
                                        m['status'] = 'scheduled'
                                        break
                                if save_tournament_data(data):
                                    st.success("🔄 Результат сброшен!")
                                    st.rerun()
                        st.divider()
                else:
                    st.info("📭 Нет сыгранных матчей для сброса")
        else:
            st.info("🔒 Введите пароль для доступа к администрированию")
    
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
                st.write(f"{match['team1']} {match['score1']}:{match['score2']} {match['team2']}")

else:
    st.error("Не удалось загрузить данные турнира. Проверьте файл data/tournament.json")