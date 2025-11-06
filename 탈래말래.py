import streamlit as st
import random
import time
import datetime # 1. 시간 입력을 위해 datetime 모듈을 가져옵니다.

# --------------------------------------------------------------------------------
# 1. 앱 상태 초기화 (Session State)
# Streamlit은 코드가 위에서 아래로 매번 다시 실행됩니다.
# 사용자의 걸음 수, 예약 상태 등을 "기억"하게 하려면 st.session_state를 사용해야 합니다.
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
        
        # 3. (수정) 층별 예약 상태 (기능 3 - 다중 예약)
        # 기존: {floor: False} -> 층마다 '예약 리스트'를 갖도록 변경
        st.session_state.reservations = {floor: [] for floor in st.session_state.floors}
        # 예시: '1F': [{'name': '홍길동', 'time': time_obj1}, {'name': '김철수', 'time': time_obj2}]
        
        # 4. (삭제) 층별 예약 시간
        # 'reservations' 리스트 안으로 통합되어 더 이상 필요 없음.
        # st.session_state.reservation_times = {floor: None for floor in st.session_state.floors}
        
        # 5. 캐시워크 상태 (기능 5)
        st.session_state.cashwalk = {'steps': 0, 'cash': 0}

        # 6. 정기 알림 설정 상태
        st.session_state.alert_floor = None # 알림 받을 층
        st.session_state.alert_time = None  # 알림 받을 시간 (time 객체)
        st.session_state.alert_window_minutes = 5 # 알림 시간 5분 전후로 활성화

# --------------------------------------------------------------------------------
# 2. 헬퍼 함수 (기능별 로직)
# --------------------------------------------------------------------------------

# (시뮬레이션) 혼잡도 데이터를 랜덤으로 새로고침하는 함수
def update_congestion_data():
    """모든 층과 엘리베이터의 혼잡도를 랜덤으로 다시 설정합니다."""
    # ... (기존 코드와 동일) ...
    st.session_state.elevator_congestion = random.choice(st.session_state.congestion_levels)
    st.session_state.floor_congestion = {
        floor: random.choice(st.session_state.congestion_levels) 
        for floor in st.session_state.floors
    }

# (기능 3, 4) 엘리베이터 예약 로직 (수정 - 다중 예약)
def reserve_elevator(floor, time_obj, user_name):
    """특정 층에, 지정된 시간으로 '현재 사용자'의 예약을 추가합니다."""
    # (수정) 예약 정보를 {이름, 시간} 딕셔너리로 생성
    new_reservation = {'name': user_name, 'time': time_obj}
    
    # (수정) 해당 층의 예약 리스트에 추가
    st.session_state.reservations[floor].append(new_reservation)
    
    time_str = time_obj.strftime('%H:%M')
    st.sidebar.success(f"{user_name}님, {floor} {time_str} 예약 완료!")

# (기능 3) 예약 취소 로직 (수정 - 다중 예약)
def cancel_reservation(floor, user_name):
    """특정 층의 예약 리스트에서 '현재 사용자'의 예약을 모두 제거합니다."""
    
    current_reservations = st.session_state.reservations[floor]
    
    # (수정) 현재 사용자의 이름(user_name)과 일치하지 *않는* 예약만 남김
    reservations_to_keep = [res for res in current_reservations if res['name'] != user_name]
    
    if len(reservations_to_keep) == len(current_reservations):
        # 아무것도 삭제되지 않음 = 예약이 원래 없었음
        st.sidebar.warning(f"{floor}에 {user_name}님의 예약이 없습니다.")
    else:
        # (수정) 필터링된 리스트로 교체
        st.session_state.reservations[floor] = reservations_to_keep
        st.sidebar.info(f"{floor} {user_name}님 예약이 취소되었습니다.")

# (기능 5) 캐시워크 로직
def simulate_steps_logic(steps_to_add):
    # ... (기존 코드와 동일) ...
    current_cash = st.session_state.cashwalk['cash']
    if current_cash >= 100:
        return
    st.session_state.cashwalk['steps'] += steps_to_add
    cash_to_add = (steps_to_add // 10) * 1
    new_cash = min(current_cash + cash_to_add, 100)
    st.session_state.cashwalk['cash'] = new_cash

# (기능 6) 정기 알림 설정 저장 함수
def set_alert(floor, time_obj):
    # ... (기존 코드와 동일) ...
    st.session_state.alert_floor = floor
    st.session_state.alert_time = time_obj
    st.sidebar.success(f"{floor} {time_obj.strftime('%H:%M')} 알림 저장!")

# (기능 6) 정기 알림 설정 해제 함수
def clear_alert():
    # ... (기존 코드와 동일) ...
    st.session_state.alert_floor = None
    st.session_state.alert_time = None
    st.sidebar.info("정기 알림이 해제되었습니다.")

# --------------------------------------------------------------------------------
# 3. Streamlit UI 렌더링
# --------------------------------------------------------------------------------

# 0. 상태 초기화 함수를 맨 위에 호출
initialize_state()

# --- (신규) 로그인 게이트 ---
if not st.session_state.logged_in:
    st.title("🏫 우리 학교 엘리베이터 앱 로그인")
    
    # (신규) 학번과 이름 입력 필드
    user_id_input = st.text_input("학번")
    user_name_input = st.text_input("이름")
    
    if st.button("로그인"):
        if user_id_input and user_name_input:
            # (신규) 로그인 성공 시, 세션에 학번과 이름 저장
            st.session_state.logged_in = True
            st.session_state.user_id = user_id_input
            st.session_state.user_name = user_name_input
            st.rerun() # 앱을 새로고침하여 메인 화면으로 이동
        else:
            st.error("학번과 이름을 모두 입력해주세요.")

else:
    # --- (기존) 메인 앱 로직 ---
    # 로그인이 성공해야 아래의 모든 UI가 보임

    # --- 사이드바 UI (기능 조작부) ---
    st.sidebar.title("🛠️ 기능 조작 패널")
    
    # (신규) 로그인한 사용자 정보 표시
    st.sidebar.markdown(f"**{st.session_state.user_name}**님 ( {st.session_state.user_id} )")
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_id = ""
        st.rerun() # 앱을 새로고침하여 로그인 화면으로 이동

    # --- (기능 6) 정기 알림 설정 ---
    st.sidebar.header("⏰ 정기 알림 설정")
    # ... (기존 코드와 동일) ...
    default_floor_index = 0
    if st.session_state.alert_floor:
        try:
            default_floor_index = st.session_state.floors.index(st.session_state.alert_floor)
        except ValueError:
            pass 
    default_time = st.session_state.alert_time if st.session_state.alert_time else datetime.time(8, 50)
    alert_floor_input = st.sidebar.selectbox(
        "알림 받을 층", st.session_state.floors, index=default_floor_index
    )
    # (수정 3) step=60 (1분) 단위로 변경
    alert_time_input = st.sidebar.time_input("알림 시간:", default_time, step=60)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("알림 저장"):
            set_alert(alert_floor_input, alert_time_input)
    with col2:
        if st.button("알림 해제"):
            clear_alert()

    # --- (기능 3, 4) 엘리베이터 예약 ---
    st.sidebar.header("🚑 엘리베이터 예약 (긴급)")
    st.sidebar.caption("다친 사람을 위한 우선 예약 기능입니다.")

    selected_floor = st.sidebar.selectbox("예약할 층", st.session_state.floors, key="reserve_floor")
    # (수정 3) step=60 (1분) 단위로 변경
    selected_time = st.sidebar.time_input("예약 시간:", datetime.datetime.now().time(), key="reserve_time", step=60)

    col1_reserve, col2_reserve = st.sidebar.columns(2)
    with col1_reserve:
        if st.button("예약하기"):
            # (수정) 예약 시 '현재 사용자'의 이름을 함께 넘김
            reserve_elevator(selected_floor, selected_time, st.session_state.user_name)
    with col2_reserve:
        if st.button("예약 취소"):
            # (수정) 취소 시 '현재 사용자'의 이름을 함께 넘김
            cancel_reservation(selected_floor, st.session_state.user_name)

    # --- (기능 5) 캐시워크 ---
    st.sidebar.header("👟 캐시워크 (시연)")
    # ... (기존 코드와 동일) ...
    st.sidebar.caption("핸드폰 건강 앱의 걸음 수를 직접 입력하세요.")
    
    # (수정 1) number_input이 즉시 실행되지 않도록 key를 사용해 분리
    st.sidebar.number_input("추가할 걸음 수 입력:", min_value=0, max_value=10000, value=0, step=100, key="steps_to_add_input")

    # (수정 1) '걸음 수 추가' 버튼을 눌러야만 로직이 실행되도록 변경
    if st.sidebar.button("걸음 수 추가하기"):
        steps_to_add = st.session_state.steps_to_add_input
        if steps_to_add > 0:
            simulate_steps_logic(steps_to_add)
            st.session_state.steps_to_add_input = 0 # 입력창 초기화
            st.rerun() # 페이지 새로고침으로 즉시 반영
        else:
            st.sidebar.warning("0보단 큰 값을 입력하세요.")

    st.sidebar.metric("오늘 총 걸음", f"{st.session_state.cashwalk['steps']} 보")
    st.sidebar.metric("오늘 적립 캐시", f"{st.session_state.cashwalk['cash']} 원")
    if st.sidebar.button("캐시워크 리셋"):
        st.session_state.cashwalk = {'steps': 0, 'cash': 0}


    # --- 메인 화면 UI (대시보드) ---
    st.title("🏫 우리 학교 엘리베이터 앱")

    # --- (기능 6) 정기 알림판 ---
    st.header("🔔 나의 맞춤 알림")
    # ... (기존 코드와 동일) ...
    if not st.session_state.alert_floor or not st.session_state.alert_time:
        st.info("사이드바에서 '정기 알림'을 설정해 보세요. ⏰")
    else:
        alert_time = st.session_state.alert_time
        target_floor = st.session_state.alert_floor
        window_min = st.session_state.alert_window_minutes
        now = datetime.datetime.now()
        now_time = now.time()
        alert_datetime = datetime.datetime.combine(now.date(), alert_time)
        start_alert_time = (alert_datetime - datetime.timedelta(minutes=window_min)).time()
        end_alert_time = (alert_datetime + datetime.timedelta(minutes=window_min)).time()
        
        if start_alert_time <= now_time <= end_alert_time:
            status = st.session_state.floor_congestion[target_floor]
            color_icon = st.session_state.congestion_colors[status]
            st.error(f"💥 지금 {target_floor}로 갈 시간입니다! ( {alert_time.strftime('%H:%M')} 알림 )\n\n## 현재 혼잡도: {color_icon} {status}")
        else:
            st.success(f"{target_floor} {alert_time.strftime('%H:%M')} 알림이 설정되었습니다. ( {window_min}분 전후로 활성화됩니다 )")


    # --- (기능 1, 2) 실시간 현황 ---
    st.header("실시간 현황")
    # ... (기존 코드와 동일) ...
    st.caption("실제로는 카메라가 이 데이터를 업데이트합니다.")
    if st.button("현황 새로고침 (데이터 시뮬레이션)"):
        update_congestion_data()
    elevator_status = st.session_state.elevator_congestion
    elevator_color_icon = st.session_state.congestion_colors[elevator_status]
    st.markdown(f"## {elevator_color_icon} 엘리베이터 내부: **{elevator_status}**")
    st.markdown("---") # 구분선

    # --- (기능 2, 3, 4) 층별 대기 현황 (수정) ---
    st.header("층별 대기 현황")

    # B1, 1F, 2F
    cols_top = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i]
        with cols_top[i]:
            st.markdown(f"### {floor}")
            
            # (수정 2) 예약 리스트와 혼잡도 상태를 항상 먼저 가져옴
            reservation_list = st.session_state.reservations[floor]
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            # (수정 2) 혼잡도를 항상 표시하는 컨테이너
            with st.container(border=True):
                # 1. 혼잡도는 항상 표시
                st.markdown(f"## {color_icon} {status}")

                # 2. 예약이 있는 경우, 그 위에 popover 버튼 추가
                if reservation_list:
                    count = len(reservation_list)
                    
                    # popover: 클릭하면 예약 상세 정보가 뜨는 팝업
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} 예약 현황**")
                        # 가장 빠른 예약 시간 찾기
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        # 모든 예약자 목록 표시
                        for res in sorted_reservations:
                            st.markdown(f"- **{res['name']}** ({res['time'].strftime('%H:%M')})")

    # 3F, 4F, 5F
    cols_bottom = st.columns(3)
    for i in range(3): 
        floor = st.session_state.floors[i + 3] # 3, 4, 5
        with cols_bottom[i]:
            st.markdown(f"### {floor}")
            
            # (수정 2) 예약 리스트와 혼잡도 상태를 항상 먼저 가져옴
            reservation_list = st.session_state.reservations[floor]
            status = st.session_state.floor_congestion[floor]
            color_icon = st.session_state.congestion_colors[status]

            # (수정 2) 혼잡도를 항상 표시하는 컨테이너
            with st.container(border=True):
                # 1. 혼잡도는 항상 표시
                st.markdown(f"## {color_icon} {status}")
                
                # 2. 예약이 있는 경우, 그 위에 popover 버튼 추가
                if reservation_list:
                    count = len(reservation_list)
                    
                    # popover: 클릭하면 예약 상세 정보가 뜨는 팝업
                    with st.popover(f"🚑 예약 ({count}명)"):
                        st.markdown(f"**{floor} 예약 현황**")
                        # 가장 빠른 예약 시간 찾기
                        sorted_reservations = sorted(reservation_list, key=lambda x: x['time'])
                        # 모든 예약자 목록 표시
                        for res in sorted_reservations:
                            st.markdown(f"- **{res['name']}** ({res['time'].strftime('%H:%M')})")
