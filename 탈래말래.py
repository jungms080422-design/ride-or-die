import streamlit as st
import random
import time
import datetime
import re
import requests # Imgur 링크를 위해 추가
from io import BytesIO # Imgur 링크를 위해 추가

# --------------------------------------------------------------------------------
# 0. 전역 설정 및 디자인 (하얀 배경, 짙은 파란색 포인트)
# --------------------------------------------------------------------------------

# 1. 색상 팔레트 정의 (수정)
PRIMARY_COLOR = "#0D47A1"  # 짙은 파란색 (포인트)
BACKGROUND_COLOR = "#F4F6F8" # 하얀색 계열 배경
SECONDARY_COLOR = "#FFFFFF" # 뉴모피즘 컴포넌트 배경
ACCENT_COLOR = "#42A5F5"   # 밝은 파란색 (보조)

# 2. 전역 CSS 스타일 (하얀 배경 뉴모피즘)
st.markdown(f"""
    <style>
    /* Google Noto Sans KR 폰트 불러오기 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

    /* CSS 변수 정의 */
    :root {{
        --primary-color: {PRIMARY_COLOR};
        --background-color: {BACKGROUND_COLOR};
        --secondary-color: {SECONDARY_COLOR};
        --accent-color: {ACCENT_COLOR};
        --light-shadow: rgba(255, 255, 255, 0.8); /* 밝은 그림자 */
        --dark-shadow: rgba(174, 174, 192, 0.4);  /* 어두운 그림자 */
        --font-family: 'Noto Sans KR', sans-serif; /* 폰트 적용 */
    }}

    /* 전체 배경색 및 폰트 */
    .stApp {{
        background-color: var(--background-color);
        color: #333333;
        font-family: var(--font-family);
    }}

    /* 사이드바 배경색 */
    .stSidebar {{
        background-color: var(--background-color);
        border-right: 1px solid #E0E0E0;
    }}
    .stSidebar .st-emotion-cache-1jicfl2 {{
         background-color: var(--background-color);
    }}

    /* 버튼 기본 스타일 (뉴모피즘) */
    .stButton > button {{
        background-color: var(--secondary-color);
        color: #333333;
        border: none;
        border-radius: 12px;
        box-shadow: 6px 6px 12px var(--dark-shadow), -6px -6px 12px var(--light-shadow);
        transition: all 0.2s ease-in-out;
        padding: 10px 20px;
        font-weight: 600;
        font-family: var(--font-family);
    }}
    .stButton > button:hover {{
        box-shadow: 2px 2px 4px var(--dark-shadow), -2px -2px 4px var(--light-shadow);
        transform: scale(0.98);
    }}
    .stButton > button:active {{
        box-shadow: inset 2px 2px 4px var(--dark-shadow), inset -2px -2px 4px var(--light-shadow);
    }}

    /* 짙은 파란색 버튼 (포인트) - type="primary" */
    .stButton > button[kind="primary"] {{
        background-color: var(--primary-color);
        color: white;
        box-shadow: 6px 6px 12px var(--dark-shadow), -6px -6px 12px var(--light-shadow);
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #0B3A80; /* 호버 시 조금 더 어둡게 */
        box-shadow: 2px 2px 4px var(--dark-shadow), -2px -2px 4px var(--light-shadow);
    }}
    .stButton > button[kind="primary"]:active {{
        box-shadow: inset 2px 2px 4px var(--dark-shadow), inset -2px -2px 4px var(--light-shadow);
    }}

    /* 텍스트 입력 필드 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        background-color: var(--secondary-color);
        border: none;
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px var(--dark-shadow), inset -5px -5px 10px var(--light-shadow);
        padding: 10px;
        color: #333333;
        font-family: var(--font-family);
    }}

    /* selectbox */
    .stSelectbox > div > div {{
        background-color: var(--secondary-color);
        border: none;
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px var(--dark-shadow), inset -5px -5px 10px var(--light-shadow);
        padding: 5px;
        color: #333333;
        font-family: var(--font-family);
    }}
    .stSelectbox > div > div > div {{
        background-color: var(--background-color);
    }}

    /* metric (수치 표시) */
    .stMetric {{
        background-color: var(--secondary-color);
        border-radius: 12px;
        box-shadow: 6px 6px 12px var(--dark-shadow), -6px -6px 12px var(--light-shadow);
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
    }}
    .stMetric > div[data-testid="stMetricValue"] {{
        color: var(--primary-color); /* 포인트 색상 */
        font-weight: 700;
    }}
    
    /* popover (예약 현황) */
    .stPopover > button {{
        background-color: var(--secondary-color);
        border-radius: 12px;
        box-shadow: 3px 3px 6px var(--dark-shadow), -3px -3px 6px var(--light-shadow);
        color: var(--primary-color);
        font-weight: 600;
    }}
    .stPopover > button:hover {{
        box-shadow: 1px 1px 2px var(--dark-shadow), -1px -1px 2px var(--light-shadow);
    }}

    /* 컨테이너 (border=True) - UI 글자 잘림 현상 해결 (padding 수정) */
    .stContainer {{
        background-color: var(--secondary-color);
        border-radius: 15px;
        box-shadow: 8px 8px 16px var(--dark-shadow), -8px -8px 16px var(--light-shadow);
        padding: 15px; /* 20px -> 15px로 줄여 공간 확보 */
        margin-bottom: 20px;
    }}
    
    /* 알림 메시지 (info, success, error 등) */
    .stAlert {{
        background-color: var(--secondary-color);
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px var(--dark-shadow), inset -5px -5px 10px var(--light-shadow);
        color: #333333;
        font-family: var(--font-family);
        border: none;
    }}
    .stAlert.info {{ border-left: 8px solid var(--accent-color); }} /* 파란색 */
    .stAlert.success {{ border-left: 8px solid #4CAF50; }} /* 초록색 */
    .stAlert.error {{ border-left: 8px solid #F44336; }} /* 빨간색 */
    .stAlert.warning {{ border-left: 8px solid #FFC107; }} /* 노란색 */


    /* 헤더 스타일 */
    h1, h2, h3, h4, h5, h6 {{
        color: #333333;
        font-family: var(--font-family);
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.7);
    }}
    
    /* 구분선 */
    hr {{
        background-color: var(--dark-shadow);
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
        # 입력창 초기화는 여기서도 필요
        st.session_state.steps_to_add_input = 0
        return
        
    st.session_state.cashwalk['steps'] += steps_to_add
    cash_to_add = (steps_to_add // 10) * 1
    new_cash = min(current_cash + cash_to_add, 100)
    
    added_cash = new_cash - current_cash
    if added_cash > 0:
        st.sidebar.success(f"{added_cash} 캐시 적립!")
    elif cash_to_add > 0:
         st.sidebar.warning("일일 최대 100캐시를 초과했습니다.")
    else:
        st.sidebar.info("캐시를 적립하기엔 걸음 수가 부족합니다. (10보당 1원)")

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
# Imgur 같은 곳에 이미지를 업로드하고, 그 '직접' 링크를 사용하세요.
# 예: https://i.imgur.com/vL4GfNT.png (이것은 Streamlit 로고 예시입니다)
LOGO_URL = "https://imgur.com/a/CvBZIEp" 

# URL에서 이미지를 불러오는 로직
try:
    response = requests.get(LOGO_URL)
    logo_image = BytesIO(response.content)
    st.image(logo_image, width=80) # 로고 파일 경로와 너비 설정
except Exception as e:
    st.warning("로고 이미지를 불러오는 데 실패했습니다. URL을 확인하세요.")
    # st.error(e) # 디버깅 시 사용

st.title("탈래말래") # 앱 이름
st.markdown("---") # 구분선

# --- 로그인 게이트 ---
if not st.session_state.logged_in:
    with st.container(border=True):
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
            # 로그아웃 시 공유 상태 초기화 (선택 사항)
            # shared_state = get_shared_state()
            # shared_state['reservations'] = {floor: [] for floor in st.session_state.floors}
            
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
        
        default_reserve_time_str = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime('%H:%M')
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
            key="steps_to_add_input" # 이 key를 콜백이 사용
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
        
        # 알림창을 컨테이너로 감싸기
        with st.container(border=True):
            if start_alert_time <= now_time <= end_alert_time:
                status = st.session_state.floor_congestion[target_floor]
                color_icon = st.session_state.congestion_colors[status]
                # st.error 대신 st.markdown으로 스타일링
                st.markdown(f"### <span style='color: #F44336;'>💥 지금 {target_floor}로 갈 시간입니다!</span>", unsafe_allow_html=True)
                st.markdown(f"#### ( {alert_time_str} 알림 )")
                st.markdown(f"## 현재 혼잡도: {color_icon} {status}")
            else:
                # st.success 대신 st.markdown으로 스타일링
                st.markdown(f"### <span style='color: #4CAF50;'>✅ {target_floor} {alert_time_str} 알림 설정됨</span>", unsafe_allow_html=True)
                st.caption(f"( {window_min}분 전후로 활성화됩니다 )")


    # --- (기능 1, 2) 실시간 현황 ---
    st.subheader("실시간 현황")
    st.caption("실제로는 카메라가 이 데이터를 업데이트합니다.")
    
    # 현황 새로고침 버튼
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
            st.markdown(f"#### {floor}") # UI 글자 잘림 현상 해결 (h3 -> h4)
            
            reservation_list = get_shared_state()['reservations'][floor] # 공유 상태에서 읽기
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            with st.container(border=True):
                st.markdown(f"### {color_icon} {status}") # UI 글자 잘림 현상 해결 (h2 -> h3)

                if reservation_list:
                    count = len(reservation_list)
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} - 총 {count}건의 예약**")
                        # 예약 시간을 기준으로 정렬
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        # 이름(res['name']) 대신 시간만 표시
                        for res in sorted_reservations:
                            st.markdown(f"- {res['time'].strftime('%H:%M')}")

    # 3F, 4F, 5F
    cols_bottom = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i + 3] # 3, 4, 5
        with cols_bottom[i]:
            st.markdown(f"#### {floor}") # UI 글자 잘림 현상 해결 (h3 -> h4)
            
            reservation_list = get_shared_state()['reservations'][floor] # 공유 상태에서 읽기
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            with st.container(border=True):
                st.markdown(f"### {color_icon} {status}") # UI 글자 잘림 현상 해결 (h2 -> h3)
                
                if reservation_list:
                    count = len(reservation_list)
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} - 총 {count}건의 예약**")
                        # 예약 시간을 기준으로 정렬
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        # 이름(res['name']) 대신 시간만 표시
                        for res in sorted_reservations:
                            st.markdown(f"- {res['time'].strftime('%H:%M')}")
