import streamlit as st
import random
import time
import datetime # 1. 시간 입력을 위해 datetime 모듈을 가져옵니다.
import re # 2. 시간 형식 검증을 위해 re(정규식) 모듈을 가져옵니다.

# --------------------------------------------------------------------------------
# 1. 앱 상태 초기화 (Session State)
# --------------------------------------------------------------------------------
# ... (이전 코드와 동일, 생략) ...
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
        
        # 3. 층별 예약 상태 (기능 3 - 다중 예약)
        st.session_state.reservations = {floor: [] for floor in st.session_state.floors}
        
        # 5. 캐시워크 상태 (기능 5)
        st.session_state.cashwalk = {'steps': 0, 'cash': 0}
        # (수정 1) 캐시워크 number_input의 key를 session_state에 초기화
        if 'steps_to_add_input' not in st.session_state:
            st.session_state.steps_to_add_input = 0

        # 6. 정기 알림 설정 상태
        st.session_state.alert_floor = None # 알림 받을 층
        st.session_state.alert_time_str = "08:50"  # (수정 2) 알림 받을 시간을 문자열로 저장
        st.session_state.alert_window_minutes = 5 # 알림 시간 5분 전후로 활성화

# --------------------------------------------------------------------------------
# 2. 헬퍼 함수 (기능별 로직)
# --------------------------------------------------------------------------------

# ... (이전 코드와 동일, 생략) ...
# (시뮬레이션) 혼잡도 데이터를 랜덤으로 새로고침하는 함수
def update_congestion_data():
    """모든 층과 엘리베이터의 혼잡도를 랜덤으로 다시 설정합니다."""
    st.session_state.elevator_congestion = random.choice(st.session_state.congestion_levels)
    st.session_state.floor_congestion = {
        floor: random.choice(st.session_state.congestion_levels) 
        for floor in st.session_state.floors
    }

# (기능 3, 4) 엘리베이터 예약 로직 (수정 - 다중 예약)
def reserve_elevator(floor, time_obj, user_name):
    """특정 층에, 지정된 시간으로 '현재 사용자'의 예약을 추가합니다."""
    new_reservation = {'name': user_name, 'time': time_obj}
    st.session_state.reservations[floor].append(new_reservation)
    
    time_str = time_obj.strftime('%H:%M')
    st.sidebar.success(f"{user_name}님, {floor} {time_str} 예약 완료!")

# (기능 3) 예약 취소 로직 (수정 - 다중 예약)
def cancel_reservation(floor, user_name):
    """특정 층의 예약 리스트에서 '현재 사용자'의 예약을 모두 제거합니다."""
    current_reservations = st.session_state.reservations[floor]
    reservations_to_keep = [res for res in current_reservations if res['name'] != user_name]
    
    if len(reservations_to_keep) == len(current_reservations):
        st.sidebar.warning(f"{floor}에 {user_name}님의 예약이 없습니다.")
    else:
        st.session_state.reservations[floor] = reservations_to_keep
        st.sidebar.info(f"{floor} {user_name}님 예약이 취소되었습니다.")

# (수정 1 - 기능 5) 캐시워크 버튼 클릭 시 실행될 '콜백 함수'
def on_click_add_steps():
    """'걸음 수 추가하기' 버튼이 눌렸을 때 호출될 함수 (오류 수정)"""
    
    # 1. 입력된 걸음 수 가져오기
    steps_to_add = st.session_state.steps_to_add_input
    
    if steps_to_add <= 0:
        st.sidebar.warning("0보단 큰 값을 입력하세요.")
        return

    # 2. 캐시워크 로직 실행
    current_cash = st.session_state.cashwalk['cash']
    if current_cash >= 100:
        st.sidebar.warning("오늘은 100캐시를 모두 적립했습니다.")
        return
        
    st.session_state.cashwalk['steps'] += steps_to_add
    cash_to_add = (steps_to_add // 10) * 1
    new_cash = min(current_cash + cash_to_add, 100)
    st.session_state.cashwalk['cash'] = new_cash

    # 3. 로직 실행 후, 입력창을 0으로 리셋
    st.session_state.steps_to_add_input = 0

# (기능 6) 정기 알림 설정 저장 함수
def set_alert(floor, time_str):
    st.session_state.alert_floor = floor
    st.session_state.alert_time_str = time_str # (수정 2) 문자열로 저장
    st.sidebar.success(f"{floor} {time_str} 알림 저장!")

# (기능 6) 정기 알림 설정 해제 함수
def clear_alert():
    st.session_state.alert_floor = None
    st.session_state.alert_time_str = "08:50" # 기본값으로 리셋
    st.sidebar.info("정기 알림이 해제되었습니다.")

# (수정 2 - 공통) 시간 형식 검증 함수 (HH:MM)
def validate_time_format(time_str):
    """ "HH:MM" (예: 08:30, 14:05) 형식인지 검증하고 time 객체로 변환합니다. """
    
    # 정규식: HH (00-23), MM (00-59)
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    
    if not time_pattern.match(time_str):
        # 형식에 맞지 않으면 None 반환
        return None
        
    try:
        # datetime.time 객체로 변환 시도
        return datetime.datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        # 형식은 맞으나 유효하지 않은 시간 (예: 25:00) - 정규식에서 이미 걸러짐
        return None

# --------------------------------------------------------------------------------
# 3. Streamlit UI 렌더링
# --------------------------------------------------------------------------------

# 0. 상태 초기화 함수를 맨 위에 호출
initialize_state()

# --- (신규) 로그인 게이트 ---
# ... (이전 코드와 동일, 생략) ...
if not st.session_state.logged_in:
    st.title("🏫 우리 학교 엘리베이터 앱 로그인")
    
    user_id_input = st.text_input("학번")
    user_name_input = st.text_input("이름")
    
    if st.button("로그인"):
        if user_id_input and user_name_input:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id_input
            st.session_state.user_name = user_name_input
            st.rerun() 
        else:
            st.error("학번과 이름을 모두 입력해주세요.")

else:
    # --- (기존) 메인 앱 로직 ---
    # 로그인이 성공해야 아래의 모든 UI가 보임

    # --- 사이드바 UI (기능 조작부) ---
    # ... (이전 코드와 동일, 생략) ...
    st.sidebar.title("🛠️ 기능 조작 패널")
    
    st.sidebar.markdown(f"**{st.session_state.user_name}**님 ( {st.session_state.user_id} )")
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_id = ""
        st.rerun() 

    # --- (기능 6) 정기 알림 설정 ---
    st.sidebar.header("⏰ 정기 알림 설정")
    
    default_floor_index = 0
    if st.session_state.alert_floor:
        try:
            default_floor_index = st.session_state.floors.index(st.session_state.alert_floor)
        except ValueError:
            pass 
            
    alert_floor_input = st.sidebar.selectbox(
        "알림 받을 층", st.session_state.floors, index=default_floor_index
    )
    # (수정 2) st.time_input -> st.text_input 으로 변경
    alert_time_input_str = st.sidebar.text_input(
        "알림 시간 (HH:MM):", 
        value=st.session_state.alert_time_str
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("알림 저장"):
            # (수정 2) 시간 형식 검증
            time_obj = validate_time_format(alert_time_input_str)
            if time_obj:
                set_alert(alert_floor_input, alert_time_input_str)
            else:
                st.sidebar.error("시간 형식이 올바르지 않습니다. (예: 08:30)")
    with col2:
        if st.button("알림 해제"):
            clear_alert()

    # --- (기능 3, 4) 엘리베이터 예약 ---
    st.sidebar.header("🚑 엘리베이터 예약 (긴급)")
    st.sidebar.caption("다친 사람을 위한 우선 예약 기능입니다.")

    selected_floor = st.sidebar.selectbox("예약할 층", st.session_state.floors, key="reserve_floor")
    
    # (수정 2) st.time_input -> st.text_input 으로 변경
    # 현재 시간을 HH:MM 형식의 문자열 기본값으로 설정
    default_reserve_time_str = datetime.datetime.now().strftime('%H:%M')
    selected_time_str = st.sidebar.text_input(
        "예약 시간 (HH:MM):", 
        value=default_reserve_time_str, 
        key="reserve_time_str"
    )

    col1_reserve, col2_reserve = st.sidebar.columns(2)
    with col1_reserve:
        if st.button("예약하기"):
            # (수정 2) 시간 형식 검증
            time_obj = validate_time_format(selected_time_str)
            if time_obj:
                reserve_elevator(selected_floor, time_obj, st.session_state.user_name)
            else:
                st.sidebar.error("시간 형식이 올바르지 않습니다. (예: 09:05)")
    with col2_reserve:
        if st.button("예약 취소"):
            cancel_reservation(selected_floor, st.session_state.user_name)

    # --- (기능 5) 캐시워크 ---
    st.sidebar.header("👟 캐시워크 (시연)")
    st.sidebar.caption("핸드폰 건강 앱의 걸음 수를 직접 입력하세요.")
    
    # (수정 1) number_input이 즉시 실행되지 않도록 key를 사용
    st.sidebar.number_input(
        "추가할 걸음 수 입력:", 
        min_value=0, 
        max_value=10000, 
        value=0, 
        step=100, 
        key="steps_to_add_input" # session_state 키 지정
    )

    # (수정 1) 'on_click' 콜백을 사용하여 오류 수정
    st.sidebar.button(
        "걸음 수 추가하기", 
        on_click=on_click_add_steps # 버튼 클릭 시 'on_click_add_steps' 함수 실행
    )

    st.sidebar.metric("오늘 총 걸음", f"{st.session_state.cashwalk['steps']} 보")
    st.sidebar.metric("오늘 적립 캐시", f"{st.session_state.cashwalk['cash']} 원")
    if st.sidebar.button("캐시워크 리셋"):
        st.session_state.cashwalk = {'steps': 0, 'cash': 0}
        st.session_state.steps_to_add_input = 0 # 리셋 시 입력창도 0으로


    # --- 메인 화면 UI (대시보드) ---
    st.title("🏫 우리 학교 엘리베이터 앱")

    # --- (기능 6) 정기 알림판 ---
    # ... (이전 코드와 동일, 생략) ...
    st.header("🔔 나의 맞춤 알림")
    
    # (수정 2) 문자열로 저장된 시간(alert_time_str)을 time 객체로 변환
    alert_time_str = st.session_state.alert_time_str
    alert_time_obj = validate_time_format(alert_time_str) # 검증 겸 변환
    target_floor = st.session_state.alert_floor

    if not target_floor or not alert_time_obj:
        st.info("사이드바에서 '정기 알림'을 설정해 보세요. ⏰")
    else:
        window_min = st.session_state.alert_window_minutes
        now = datetime.datetime.now()
        now_time = now.time()
        
        # (수정 2) time 객체를 기준으로 시간 계산
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
    # ... (이전 코드와 동일, 생략) ...
    st.header("실시간 현황")
    st.caption("실제로는 카메라가 이 데이터를 업데이트합니다.")
    if st.button("현황 새로고침 (데이터 시뮬레이션)"):
        update_congestion_data()
        
    elevator_status = st.session_state.elevator_congestion
    elevator_color_icon = st.session_state.congestion_colors[elevator_status]
    st.markdown(f"## {elevator_color_icon} 엘리베이터 내부: **{elevator_status}**")
    st.markdown("---") # 구분선

    # --- (기능 2, 3, 4) 층별 대기 현황 ---
    st.header("층별 대기 현황")

    # B1, 1F, 2F
    cols_top = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i]
        with cols_top[i]:
            st.markdown(f"### {floor}")
            
            reservation_list = st.session_state.reservations[floor]
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            with st.container(border=True):
                st.markdown(f"## {color_icon} {status}")

                if reservation_list:
                    count = len(reservation_list)
                    # (수정 1) popover 클릭 시 예약자 이름 없이 시간만 표시
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} - 총 {count}건의 예약**")
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        # (수정 1) 이름(res['name'])을 제외하고 시간(res['time'])만 표시
                        for res in sorted_reservations:
                            st.markdown(f"- {res['time'].strftime('%H:%M')}")

    # 3F, 4F, 5F
    cols_bottom = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i + 3] # 3, 4, 5
        with cols_bottom[i]:
            st.markdown(f"### {floor}")
            
            reservation_list = st.session_state.reservations[floor]
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            with st.container(border=True):
                st.markdown(f"## {color_icon} {status}")
                
                if reservation_list:
                    count = len(reservation_list)
                    # (수정 1) popover 클릭 시 예약자 이름 없이 시간만 표시
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} - 총 {count}건의 예약**")
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        # (수정 1) 이름(res['name'])을 제외하고 시간(res['time'])만 표시
                        for res in sorted_reservations:
                            st.markdown(f"- {res['time'].strftime('%H:%M')}")
