import streamlit as st
import random
import time
import datetime
import re

# --------------------------------------------------------------------------------
# 0. 전역 설정 및 디자인 (뉴모피즘)
# --------------------------------------------------------------------------------

# 1. 색상 팔레트 정의
PRIMARY_COLOR = "#007BFF"  # 쨍한 파란색 (포인트)
BACKGROUND_COLOR = "#E0E5EC" # 부드러운 회색/파란색 (뉴모피즘 배경)
LIGHT_SHADOW = "#FFFFFF" # 밝은 그림자
DARK_SHADOW = "#A3B1C6"  # 어두운 그림자

# 2. 전역 CSS 스타일 (뉴모피즘 디자인 적용 시도)
# Streamlit의 기본 UI를 오버라이드하여 뉴모피즘 느낌을 구현합니다.
# 완벽하진 않지만, 유사한 시각적 효과를 줍니다.
st.markdown(f"""
    <style>
    /* 전체 배경색 */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: #333333; /* 기본 텍스트 색상 */
    }}

    /* 사이드바 배경색 */
    .stSidebar {{
        background-color: {BACKGROUND_COLOR};
    }}

    /* 버튼 기본 스타일 (뉴모피즘) */
    .stButton > button {{
        background-color: {BACKGROUND_COLOR};
        color: #333333;
        border: none;
        border-radius: 12px;
        box-shadow: 6px 6px 12px {DARK_SHADOW}, -6px -6px 12px {LIGHT_SHADOW};
        transition: all 0.2s ease-in-out;
        padding: 10px 20px;
        font-weight: 600;
    }}
    .stButton > button:hover {{
        box-shadow: 2px 2px 4px {DARK_SHADOW}, -2px -2px 4px {LIGHT_SHADOW};
        transform: scale(0.98);
    }}
    .stButton > button:active {{
        box-shadow: inset 2px 2px 4px {DARK_SHADOW}, inset -2px -2px 4px {LIGHT_SHADOW};
    }}

    /* 쨍한 파란색 버튼 (포인트) */
    .stButton.primary-button > button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        box-shadow: 6px 6px 12px {DARK_SHADOW}, -6px -6px 12px {LIGHT_SHADOW};
    }}
    .stButton.primary-button > button:hover {{
        background-color: #0069d9;
        box-shadow: 2px 2px 4px {DARK_SHADOW}, -2px -2px 4px {LIGHT_SHADOW};
    }}
    .stButton.primary-button > button:active {{
        box-shadow: inset 2px 2px 4px {DARK_SHADOW}, inset -2px -2px 4px {LIGHT_SHADOW};
    }}

    /* 텍스트 입력 필드 */
    .stTextInput > div > div > input {{
        background-color: {BACKGROUND_COLOR};
        border: none;
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px {DARK_SHADOW}, inset -5px -5px 10px {LIGHT_SHADOW};
        padding: 10px;
        color: #333333;
    }}

    /* selectbox */
    .stSelectbox > div > div {{
        background-color: {BACKGROUND_COLOR};
        border: none;
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px {DARK_SHADOW}, inset -5px -5px 10px {LIGHT_SHADOW};
        padding: 5px;
        color: #333333;
    }}
    .stSelectbox > div > div > div {{
        background-color: {BACKGROUND_COLOR}; /* 드롭다운 메뉴 배경 */
    }}

    /* metric (수치 표시) */
    .stMetric {{
        background-color: {BACKGROUND_COLOR};
        border-radius: 12px;
        box-shadow: 6px 6px 12px {DARK_SHADOW}, -6px -6px 12px {LIGHT_SHADOW};
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
    }}
    .stMetric > div[data-testid="stMetricValue"] {{
        color: {PRIMARY_COLOR}; /* 포인트 색상 */
    }}
    
    /* popover (예약 현황) */
    .stPopover > button {{
        background-color: {BACKGROUND_COLOR};
        border-radius: 12px;
        box-shadow: 3px 3px 6px {DARK_SHADOW}, -3px -3px 6px {LIGHT_SHADOW};
    }}
    .stPopover > button:hover {{
        box-shadow: 1px 1px 2px {DARK_SHADOW}, -1px -1px 2px {LIGHT_SHADOW};
    }}

    /* 컨테이너 (border=True) */
    .stContainer {{
        background-color: {BACKGROUND_COLOR};
        border-radius: 15px; /* 더 둥글게 */
        box-shadow: 8px 8px 16px {DARK_SHADOW}, -8px -8px 16px {LIGHT_SHADOW};
        padding: 20px;
        margin-bottom: 20px;
    }}
    
    /* 알림 메시지 (info, success, error 등) */
    .stAlert {{
        background-color: {BACKGROUND_COLOR};
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px {DARK_SHADOW}, inset -5px -5px 10px {LIGHT_SHADOW};
        color: #333333;
    }}
    .stAlert.info {{ border-left: 8px solid #2196F3; }} /* 파란색 */
    .stAlert.success {{ border-left: 8px solid #4CAF50; }} /* 초록색 */
    .stAlert.error {{ border-left: 8px solid #F44336; }} /* 빨간색 */
    .stAlert.warning {{ border-left: 8px solid #FFC107; }} /* 노란색 */


    /* 헤더 스타일 */
    h1, h2, h3, h4, h5, h6 {{
        color: #333333;
        text-shadow: 1px 1px 2px {LIGHT_SHADOW};
    }}
    </style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------------
# 싱글톤 캐시 초기화 (모든 사용자 공유 데이터)
# --------------------------------------------------------------------------------
@st.cache_resource
def get_shared_state():
    """모든 앱 인스턴스에서 공유될 상태를 반환합니다. (Firebase 임시 대체)"""
    return {
        'reservations': {floor: [] for floor in ['B1', '1F', '2F', '3F', '4F', '5F']}
    }

# --------------------------------------------------------------------------------
# 1. 앱 상태 초기화 (Session State)
# --------------------------------------------------------------------------------
def initialize_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True # 초기화 완료 플래그
        
        # (신규) 로그인 상태 추가
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_id = "" # 학번
        
        # 층 목록
        st.session_state.floors = ['B1', '1F', '2F', '3F', '4F', '5F']
        
        # 혼잡도 레벨 및 색상 정의 (기능 1, 2)
        st.session_state.congestion_levels = ['여유', '보통', '혼잡']
        st.session_state.congestion_colors = {'여유': '🟢', '보통': '🟠', '혼잡': '🔴'}
        
        # --- 데이터 시뮬레이션 ---
        # 1. 엘리베이터 내부 혼잡도 (기능 1)
        st.session_state.elevator_congestion = random.choice(st.session_state.congestion_levels)
        
        # 2. 층별 대기 혼잡도 (기능 2)
        st.session_state.floor_congestion = {
            floor: random.choice(st.session_state.congestion_levels) 
            for floor in st.session_state.floors
        }
        
        # 3. 층별 예약 상태 (get_shared_state()로 대체)
        # st.session_state.reservations = {floor: [] for floor in st.session_state.floors} # 주석 처리
        
        # 5. 캐시워크 상태 (기능 5)
        st.session_state.cashwalk = {'steps': 0, 'cash': 0}
        if 'steps_to_add_input' not in st.session_state:
            st.session_state.steps_to_add_input = 0

        # 6. 정기 알림 설정 상태
        st.session_state.alert_floor = None 
        st.session_state.alert_time_str = "08:50"
        st.session_state.alert_window_minutes = 5 

# --------------------------------------------------------------------------------
# 2. 헬퍼 함수 (기능별 로직)
# --------------------------------------------------------------------------------

# (시뮬레이션) 혼잡도 데이터를 랜덤으로 새로고침하는 함수
def update_congestion_data():
    """모든 층과 엘리베이터의 혼잡도를 랜덤으로 다시 설정합니다."""
    st.session_state.elevator_congestion = random.choice(st.session_state.congestion_levels)
    st.session_state.floor_congestion = {
        floor: random.choice(st.session_state.congestion_levels) 
        for floor in st.session_state.floors
    }

# (기능 3, 4) 엘리베이터 예약 로직 (수정 - 다중 예약 및 공유 상태 사용)
def reserve_elevator(floor, time_obj, user_name):
    """특정 층에, 지정된 시간으로 '현재 사용자'의 예약을 추가합니다. 공유 상태 사용."""
    shared_state = get_shared_state() # 공유 상태 가져오기
    new_reservation = {'name': user_name, 'time': time_obj}
    shared_state['reservations'][floor].append(new_reservation) # 공유 상태에 저장
    
    time_str = time_obj.strftime('%H:%M')
    st.sidebar.success(f"{user_name}님, {floor} {time_str} 예약 완료!")

# (기능 3) 예약 취소 로직 (수정 - 다중 예약 및 공유 상태 사용)
def cancel_reservation(floor, user_name):
    """특정 층의 예약 리스트에서 '현재 사용자'의 예약을 모두 제거합니다. 공유 상태 사용."""
    shared_state = get_shared_state() # 공유 상태 가져오기
    current_reservations = shared_state['reservations'][floor] # 공유 상태에서 읽기
    reservations_to_keep = [res for res in current_reservations if res['name'] != user_name]
    
    if len(reservations_to_keep) == len(current_reservations):
        st.sidebar.warning(f"{floor}에 {user_name}님의 예약이 없습니다.")
    else:
        shared_state['reservations'][floor] = reservations_to_keep # 공유 상태 업데이트
        st.sidebar.info(f"{floor} {user_name}님 예약이 취소되었습니다.")

# (수정 1 - 기능 5) 캐시워크 버튼 클릭 시 실행될 '콜백 함수'
def on_click_add_steps():
    """'걸음 수 추가하기' 버튼이 눌렸을 때 호출될 함수 (오류 수정)"""
    
    steps_to_add = st.session_state.steps_to_add_input
    
    if steps_to_add <= 0:
        st.sidebar.warning("0보단 큰 값을 입력하세요.")
        return

    current_cash = st.session_state.cashwalk['cash']
    if current_cash >= 100:
        st.sidebar.warning("오늘은 100캐시를 모두 적립했습니다.")
        return
        
    st.session_state.cashwalk['steps'] += steps_to_add
    cash_to_add = (steps_to_add // 10) * 1
    new_cash = min(current_cash + cash_to_add, 100)
    st.session_state.cashwalk['cash'] = new_cash

    st.session_state.steps_to_add_input = 0 # 로직 실행 후, 입력창을 0으로 리셋

# (기능 6) 정기 알림 설정 저장 함수
def set_alert(floor, time_str):
    st.session_state.alert_floor = floor
    st.session_state.alert_time_str = time_str
    st.sidebar.success(f"{floor} {time_str} 알림 저장!")

# (기능 6) 정기 알림 설정 해제 함수
def clear_alert():
    st.session_state.alert_floor = None
    st.session_state.alert_time_str = "08:50"
    st.sidebar.info("정기 알림이 해제되었습니다.")

# (공통) 시간 형식 검증 함수 (HH:MM)
def validate_time_format(time_str):
    """ "HH:MM" (예: 08:30, 14:05) 형식인지 검증하고 time 객체로 변환합니다. """
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    if not time_pattern.match(time_str):
        return None
    try:
        return datetime.datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return None

# --------------------------------------------------------------------------------
# 3. Streamlit UI 렌더링
# --------------------------------------------------------------------------------

initialize_state()
shared_state = get_shared_state() # 공유 상태를 사용

# --- 최상단 로고 및 앱 이름 (UI 추가 1) ---
# 로고 파일을 프로젝트 폴더 안에 'logo.png'로 저장하고 사용하세요.
# 예: /your_project_folder/logo.png
# 로고가 없으면 이 부분을 주석 처리하거나 다른 이미지로 대체하세요.
st.image("test_logo.png", width=80) # 로고 파일 경로와 너비 설정
st.title("탈래말래") # 앱 이름
st.markdown("---") # 구분선

# --- 로그인 게이트 ---
if not st.session_state.logged_in:
    st.header("🏫 우리 학교 엘리베이터 앱 로그인")
    
    user_id_input = st.text_input("학번", key="login_id")
    user_name_input = st.text_input("이름", key="login_name")
    
    # 로그인 버튼에 primary-button 클래스 적용
    if st.button("로그인", key="login_btn", help="로그인하려면 학번과 이름을 입력하세요.", type="primary"):
        if user_id_input and user_name_input:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id_input
            st.session_state.user_name = user_name_input
            st.rerun() 
        else:
            st.error("학번과 이름을 모두 입력해주세요.")

else:
    # --- 사이드바 UI (기능 조작 패널) ---
    with st.sidebar: # 사이드바 전체를 with 문으로 묶어 가독성 향상
        st.title("🛠️ 기능 조작 패널")
        st.markdown(f"**{st.session_state.user_name}**님 ( {st.session_state.user_id} )")
        if st.button("로그아웃", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_id = ""
            st.rerun() 

        st.markdown("---") # 구분선

        # --- (기능 6) 정기 알림 설정 ---
        st.header("⏰ 정기 알림 설정")
        
        default_floor_index = 0
        if st.session_state.alert_floor:
            try:
                default_floor_index = st.session_state.floors.index(st.session_state.alert_floor)
            except ValueError:
                pass 
                
        alert_floor_input = st.selectbox(
            "알림 받을 층", st.session_state.floors, index=default_floor_index, key="alert_floor_sel"
        )
        alert_time_input_str = st.text_input(
            "알림 시간 (HH:MM):", 
            value=st.session_state.alert_time_str, key="alert_time_in"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("알림 저장", key="save_alert_btn", type="primary"):
                time_obj = validate_time_format(alert_time_input_str)
                if time_obj:
                    set_alert(alert_floor_input, alert_time_input_str)
                else:
                    st.error("시간 형식이 올바르지 않습니다. (예: 08:30)")
        with col2:
            if st.button("알림 해제", key="clear_alert_btn"):
                clear_alert()

        st.markdown("---") # 구분선

        # --- (기능 3, 4) 엘리베이터 예약 ---
        st.header("🚑 엘리베이터 예약 (긴급)")
        st.caption("다친 사람을 위한 우선 예약 기능입니다.")

        selected_floor = st.selectbox("예약할 층", st.session_state.floors, key="reserve_floor_sel")
        
        default_reserve_time_str = datetime.datetime.now().strftime('%H:%M')
        selected_time_str = st.text_input(
            "예약 시간 (HH:MM):", 
            value=default_reserve_time_str, 
            key="reserve_time_in"
        )

        col1_reserve, col2_reserve = st.columns(2)
        with col1_reserve:
            if st.button("예약하기", key="make_reserve_btn", type="primary"):
                time_obj = validate_time_format(selected_time_str)
                if time_obj:
                    reserve_elevator(selected_floor, time_obj, st.session_state.user_name)
                else:
                    st.error("시간 형식이 올바르지 않습니다. (예: 09:05)")
        with col2_reserve:
            if st.button("예약 취소", key="cancel_reserve_btn"):
                cancel_reservation(selected_floor, st.session_state.user_name)

        st.markdown("---") # 구분선

        # --- (기능 5) 캐시워크 ---
        st.header("👟 캐시워크 (시연)")
        st.caption("핸드폰 건강 앱의 걸음 수를 직접 입력하세요.")
        
        st.number_input(
            "추가할 걸음 수 입력:", 
            min_value=0, 
            max_value=10000, 
            value=0, 
            step=100, 
            key="steps_to_add_input"
        )

        st.button(
            "걸음 수 추가하기", 
            on_click=on_click_add_steps, # 콜백 함수
            key="add_steps_btn", 
            type="primary"
        )

        st.metric("오늘 총 걸음", f"{st.session_state.cashwalk['steps']} 보")
        st.metric("오늘 적립 캐시", f"{st.session_state.cashwalk['cash']} 원")
        if st.button("캐시워크 리셋", key="reset_cash_btn"):
            st.session_state.cashwalk = {'steps': 0, 'cash': 0}
            st.session_state.steps_to_add_input = 0 


    # --- 메인 화면 UI (대시보드) ---
    # st.title("🏫 우리 학교 엘리베이터 앱") # 최상단에 로고와 함께 이미 정의됨

    # --- (기능 6) 정기 알림판 ---
    st.subheader("🔔 나의 맞춤 알림")
    
    alert_time_str = st.session_state.alert_time_str
    alert_time_obj = validate_time_format(alert_time_str)
    target_floor = st.session_state.alert_floor

    if not target_floor or not alert_time_obj:
        st.info("사이드바에서 '정기 알림'을 설정해 보세요. ⏰")
    else:
        window_min = st.session_state.alert_window_minutes
        now = datetime.datetime.now()
        now_time = now.time()
        
        alert_datetime = datetime.datetime.combine(now.date(), alert_time_obj)
        start_alert_time = (alert_datetime - datetime.timedelta(minutes=window_min)).time()
        end_alert_time = (alert_datetime + datetime.timedelta(minutes=window_min)).time()
        
        if start_alert_time <= now_time <= end_alert_time:
            status = st.session_state.floor_congestion[target_floor]
            color_icon = st.session_state.congestion_colors[status]
            st.error(f"💥 지금 {target_floor}로 갈 시간입니다! ( {alert_time_str} 알림 )\n\n## 현재 혼잡도: {color_icon} {status}")
        else:
            st.success(f"{target_floor} {alert_time_str} 알림이 설정되었습니다. ( {window_min}분 전후로 활성화됩니다 )")


    # --- (기능 1, 2) 실시간 현황 ---
    st.subheader("실시간 현황")
    st.caption("실제로는 카메라가 이 데이터를 업데이트합니다.")
    
    # 현황 새로고침 버튼에도 primary-button 클래스 적용
    if st.button("현황 새로고침 (데이터 시뮬레이션)", key="refresh_btn", type="primary"):
        update_congestion_data()
        
    elevator_status = st.session_state.elevator_congestion
    elevator_color_icon = st.session_state.congestion_colors[elevator_status]
    
    with st.container(border=True): # 엘리베이터 내부 혼잡도도 뉴모피즘 컨테이너로 감쌈
        st.markdown(f"## {elevator_color_icon} 엘리베이터 내부: **{elevator_status}**")
    
    st.markdown("---") # 구분선

    # --- (기능 2, 3, 4) 층별 대기 현황 ---
    st.subheader("층별 대기 현황")

    # B1, 1F, 2F
    cols_top = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i]
        with cols_top[i]:
            st.markdown(f"### {floor}")
            
            reservation_list = get_shared_state()['reservations'][floor] # 공유 상태에서 읽기
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            with st.container(border=True):
                st.markdown(f"## {color_icon} {status}")

                if reservation_list:
                    count = len(reservation_list)
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} - 총 {count}건의 예약**")
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        for res in sorted_reservations:
                            st.markdown(f"- {res['time'].strftime('%H:%M')}")

    # 3F, 4F, 5F
    cols_bottom = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i + 3] # 3, 4, 5
        with cols_bottom[i]:
            st.markdown(f"### {floor}")
            
            reservation_list = get_shared_state()['reservations'][floor] # 공유 상태에서 읽기
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            with st.container(border=True):
                st.markdown(f"## {color_icon} {status}")
                
                if reservation_list:
                    count = len(reservation_list)
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} - 총 {count}건의 예약**")
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        for res in sorted_reservations:
                            st.markdown(f"- {res['time'].strftime('%H:%M')}")
