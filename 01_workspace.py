import streamlit as st
import time
import random

# --- 1. 기본 설정 및 Session State 초기화 ---

if 'match_stage' not in st.session_state:
    st.session_state.match_stage = 'SETUP'

if 'team_a' not in st.session_state:
    st.session_state.team_a = "Team A"
if 'team_b' not in st.session_state:
    st.session_state.team_b = "Team B"

if 'score_a' not in st.session_state:
    st.session_state.score_a = 0
if 'score_b' not in st.session_state:
    st.session_state.score_b = 0

if 'team_a_roster' not in st.session_state:
    st.session_state.team_a_roster = []
if 'team_b_roster' not in st.session_state:
    st.session_state.team_b_roster = []

if 'match_log' not in st.session_state:
    st.session_state.match_log = []

if 'goal_log' not in st.session_state:
    st.session_state.goal_log = []

# 통계 데이터 초기화
if 'match_stats' not in st.session_state:
    st.session_state.match_stats = {
        'A': {'shots': 0, 'on_target': 0, 'passes': 0, 'pass_success': 0, 'possession': 0},
        'B': {'shots': 0, 'on_target': 0, 'passes': 0, 'pass_success': 0, 'possession': 0}
    }

def reset_game():
    st.session_state.match_stage = 'SETUP'
    st.session_state.score_a = 0
    st.session_state.score_b = 0
    st.session_state.team_a_roster = []
    st.session_state.team_b_roster = []
    st.session_state.match_log = []
    st.session_state.goal_log = []
    st.session_state.match_stats = {
        'A': {'shots': 0, 'on_target': 0, 'passes': 0, 'pass_success': 0, 'possession': 0},
        'B': {'shots': 0, 'on_target': 0, 'passes': 0, 'pass_success': 0, 'possession': 0}
    }

def generate_full_roster(key_players):
    full_roster = []
    for p in key_players:
        if p['name']:
            full_roster.append(f"{p['name']} ({p['role']})")
    needed = 11 - len(full_roster)
    roles_pool = ['공격수', '미드필더', '수비수', '수비수', '미드필더', '수비수', '미드필더', '공격수']
    for i in range(needed):
        role_name = roles_pool[i % len(roles_pool)]
        full_roster.append(f"{role_name} {i+1}")
    return full_roster

def add_log(minute, message):
    st.session_state.match_log.append({'time': minute, 'msg': message})

def add_goal(team, minute, scorer, assist=None):
    st.session_state.goal_log.append({
        'team': team,
        'time': minute,
        'scorer': scorer,
        'assist': assist
    })

def get_player_role(player_str):
    if "(" in player_str and ")" in player_str:
        return player_str.split("(")[1].split(")")[0]
    else:
        return player_str.split(" ")[0]

def generate_event(team_name, roster, is_goal_chance=False):
    fw_roles = ['CF', 'SS', 'LWF', 'RWF', '공격수']
    mf_roles = ['AMF', 'LMF', 'RMF', 'CMF', 'DMF', '미드필더']
    df_roles = ['CB', 'LB', 'RB', 'GK', '수비수']
    
    # 1: 유효슈팅, 2: 빗나감/수비, 3: 골
    # (일반 패스는 여기서 처리하지 않고 분당 통계에서 처리)
    event_type = 0
    
    if is_goal_chance:
        roll = random.random()
        if roll < 0.35: event_type = 3 # 골
        elif roll < 0.70: event_type = 1 # 유효슈팅
        else: event_type = 2 # 빗나감
    else:
        # 기습 슈팅
        if random.random() < 0.5: event_type = 1
        else: event_type = 2
            
    msg = ""
    is_goal = False
    scorer = None
    assist = None
    target_roster = roster 
    
    if event_type == 3: # GOAL
        if random.random() < 0.6: target_roster = [p for p in roster if get_player_role(p) in fw_roles]
        elif random.random() < 0.9: target_roster = [p for p in roster if get_player_role(p) in mf_roles]
        else: target_roster = [p for p in roster if get_player_role(p) in df_roles]
        if not target_roster: target_roster = roster
        scorer = random.choice(target_roster)
        if random.random() < 0.7:
            assist_player = random.choice([p for p in roster if p != scorer])
            assist = assist_player
            msg = f"⚽ **GOAL!!!** {scorer}의 득점! (도움: {assist})"
        else:
            msg = f"⚽ **GOAL!!!** {scorer}의 환상적인 개인기 득점!"
        is_goal = True
        
    elif event_type == 2: # Miss / Defense
        if random.random() < 0.7: target_roster = [p for p in roster if get_player_role(p) in df_roles]
        elif random.random() < 0.9: target_roster = [p for p in roster if get_player_role(p) in mf_roles]
        else: target_roster = [p for p in roster if get_player_role(p) in fw_roles]
        if not target_roster: target_roster = roster
        player = random.choice(target_roster)
        def_actions = [
            f"{player}의 결정적인 태클! 위기를 넘깁니다.",
            f"골키퍼의 슈퍼 세이브! {player} 대단합니다!", 
            f"{player}의 슈팅이 골대를 살짝 빗나갑니다."
        ]
        msg = random.choice(def_actions)
        
    elif event_type == 1: # Shot on Target
        if random.random() < 0.6: target_roster = [p for p in roster if get_player_role(p) in fw_roles]
        elif random.random() < 0.9: target_roster = [p for p in roster if get_player_role(p) in mf_roles]
        else: target_roster = [p for p in roster if get_player_role(p) in df_roles]
        if not target_roster: target_roster = roster
        player = random.choice(target_roster)
        shot_actions = [
            f"{player}의 강력한 유효슈팅! 골키퍼 정면입니다.",
            f"{player}, 회심의 슈팅이 골대를 맞고 나옵니다!",
            f"{player}의 헤더! 아쉽게 빗나갑니다."
        ]
        msg = random.choice(shot_actions)
        
    return msg, is_goal, scorer, assist, event_type

# [NEW] 매 분마다 실행되는 기본 통계 업데이트 (패스, 점유율)
def update_per_minute_stats():
    stats = st.session_state.match_stats
    
    # 1분 동안 양팀 합쳐서 7~12개의 패스가 왔다갔다 한다고 가정
    # 랜덤하게 점유 팀을 정함 (약간의 확률 변동 가능)
    if random.random() < 0.5:
        poss_team = 'A'
        opp_team = 'B'
    else:
        poss_team = 'B'
        opp_team = 'A'
        
    # 점유율 증가
    stats[poss_team]['possession'] += 1
    
    # 점유한 팀 패스 증가 (4~8개)
    passes_p = random.randint(4, 8)
    stats[poss_team]['passes'] += passes_p
    stats[poss_team]['pass_success'] += int(passes_p * random.uniform(0.85, 0.98))
    
    # 상대팀도 압박하면서 패스 1~3개 정도는 함
    passes_o = random.randint(1, 3)
    stats[opp_team]['passes'] += passes_o
    stats[opp_team]['pass_success'] += int(passes_o * random.uniform(0.8, 0.95))

# [NEW] 이벤트 발생 시 슈팅 통계 업데이트
def update_event_stats(team_code, event_type):
    stats = st.session_state.match_stats
    
    if event_type == 3: # Goal
        stats[team_code]['shots'] += 1
        stats[team_code]['on_target'] += 1
        
    elif event_type == 1: # Shot on Target
        stats[team_code]['shots'] += 1
        stats[team_code]['on_target'] += 1
        
    elif event_type == 2: # Miss
        # 빗나간 슈팅도 슈팅 수에는 포함
        stats[team_code]['shots'] += 1

# --- UI 디자인 ---

st.title("⚽ 단계별 축구 경기 시뮬레이터")

scoreboard_placeholder = st.empty()
stats_placeholder = st.empty()

def render_scoreboard():
    if st.session_state.match_stage != 'SETUP':
        with scoreboard_placeholder.container():
            col_left, col_mid, col_right = st.columns([1, 0.6, 1], gap="small")
            with col_left:
                st.markdown(f"<h3 style='text-align: right; color: #FF4B4B;'>{st.session_state.team_a} 🔴</h3>", unsafe_allow_html=True)
            with col_mid:
                st.markdown(f"<h1 style='text-align: center; margin: 0; padding: 0;'>{st.session_state.score_a} : {st.session_state.score_b}</h1>", unsafe_allow_html=True)
            with col_right:
                st.markdown(f"<h3 style='text-align: left; color: #1C83E1;'>🔵 {st.session_state.team_b}</h3>", unsafe_allow_html=True)
            
            if st.session_state.goal_log:
                st.write("") 
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"<div style='text-align: right; color: grey; font-size: 0.9em;'>", unsafe_allow_html=True)
                    for goal in st.session_state.goal_log:
                        if goal['team'] == 'A':
                            assist_str = f"(AS: {goal['assist']})" if goal['assist'] else ""
                            st.write(f"⚽ {goal['time']} {goal['scorer']} {assist_str}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"<div style='text-align: left; color: grey; font-size: 0.9em;'>", unsafe_allow_html=True)
                    for goal in st.session_state.goal_log:
                        if goal['team'] == 'B':
                            assist_str = f"(AS: {goal['assist']})" if goal['assist'] else ""
                            st.write(f"⚽ {goal['time']} {goal['scorer']} {assist_str}")
                    st.markdown("</div>", unsafe_allow_html=True)
            st.divider()

def render_stats():
    if st.session_state.match_stage == 'SETUP': return

    s = st.session_state.match_stats
    total_poss = s['A']['possession'] + s['B']['possession']
    if total_poss == 0: total_poss = 1
    poss_a = int((s['A']['possession'] / total_poss) * 100)
    poss_b = 100 - poss_a
    
    with stats_placeholder.container():
        st.markdown("""
        <style>
        .stat-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #333; }
        .stat-val { font-weight: bold; width: 40px; text-align: center; }
        .stat-label { flex-grow: 1; text-align: center; color: #aaa; font-size: 0.9em; }
        .stat-a { color: #FF4B4B; }
        .stat-b { color: #1C83E1; }
        </style>
        """, unsafe_allow_html=True)
        
        with st.expander("📊 실시간 경기 통계", expanded=True):
            st.markdown(f"""
            <div class='stat-row'>
                <div class='stat-val stat-a'>{poss_a}%</div>
                <div class='stat-label'>점유율</div>
                <div class='stat-val stat-b'>{poss_b}%</div>
            </div>
            <div class='stat-row'>
                <div class='stat-val stat-a'>{s['A']['shots']}</div>
                <div class='stat-label'>슈팅</div>
                <div class='stat-val stat-b'>{s['B']['shots']}</div>
            </div>
            <div class='stat-row'>
                <div class='stat-val stat-a'>{s['A']['on_target']}</div>
                <div class='stat-label'>유효 슈팅</div>
                <div class='stat-val stat-b'>{s['B']['on_target']}</div>
            </div>
            <div class='stat-row'>
                <div class='stat-val stat-a'>{s['A']['passes']}</div>
                <div class='stat-label'>패스 시도</div>
                <div class='stat-val stat-b'>{s['B']['passes']}</div>
            </div>
            <div class='stat-row'>
                <div class='stat-val stat-a'>{s['A']['pass_success']}</div>
                <div class='stat-label'>패스 성공</div>
                <div class='stat-val stat-b'>{s['B']['pass_success']}</div>
            </div>
            """, unsafe_allow_html=True)

render_scoreboard()
render_stats()

if st.session_state.match_stage != 'SETUP':
    with st.expander("📝 경기 중계 기록", expanded=True):
        if not st.session_state.match_log:
            st.write("아직 기록이 없습니다.")
        else:
            for log in reversed(st.session_state.match_log):
                st.write(f"**{log['time']}** {log['msg']}")

# --- 2. 경기 진행 로직 ---

if st.session_state.match_stage == 'SETUP':
    col1, col2 = st.columns(2)
    roles = ['CF', 'SS', 'LWF', 'RWF', 'AMF', 'LMF', 'RMF', 'CMF', 'DMF', 'CB', 'LB', 'RB', 'GK']
    
    default_players_a = [("라민 야말", "RWF"), ("페드리", "CMF"), ("하피냐", "LWF")]
    default_players_b = [("음바페", "CF"), ("비니시우스 주니어", "LWF"), ("주드 벨링엄", "CMF")]
    
    with col1:
        st.subheader("홈 팀 설정")
        st.session_state.team_a = st.text_input("홈 팀 이름", value="바르셀로나")
        st.markdown("**핵심 선수 3명 입력**")
        team_a_keys = []
        for i in range(3):
            c_name, c_role = st.columns([2, 1])
            def_name, def_role = default_players_a[i]
            p_name = c_name.text_input(f"선수 {i+1} 이름", value=def_name, key=f"a_name_{i}")
            p_role = c_role.selectbox(f"포지션", roles, index=roles.index(def_role), key=f"a_role_{i}")
            if p_name: team_a_keys.append({'name': p_name, 'role': p_role})

    with col2:
        st.subheader("원정 팀 설정")
        st.session_state.team_b = st.text_input("원정 팀 이름", value="레알 마드리드")
        st.markdown("**핵심 선수 3명 입력**")
        team_b_keys = []
        for i in range(3):
            c_name, c_role = st.columns([2, 1])
            def_name, def_role = default_players_b[i]
            p_name = c_name.text_input(f"선수 {i+1} 이름", value=def_name, key=f"b_name_{i}")
            p_role = c_role.selectbox(f"포지션", roles, index=roles.index(def_role), key=f"b_role_{i}")
            if p_name: team_b_keys.append({'name': p_name, 'role': p_role})
    
    if st.button("경기 시작", use_container_width=True):
        st.session_state.team_a_roster = generate_full_roster(team_a_keys)
        st.session_state.team_b_roster = generate_full_roster(team_b_keys)
        st.session_state.match_stage = 'FIRST_HALF'
        st.rerun()

elif st.session_state.match_stage == 'FIRST_HALF':
    st.subheader("전반전")
    if st.button("전반전 시작 (Kick Off)", use_container_width=True):
        with st.spinner("경기 진행 중..."):
            add_log("0'", "경기 시작!")
            
            # [핵심] 1분부터 45분까지 루프를 돕니다.
            for minute in range(1, 46):
                
                # 1. 매 분마다 기본 통계(패스/점유율) 업데이트 (화면에 바로 반영됨)
                update_per_minute_stats()
                render_stats() # 통계판 갱신
                
                # 2. 이벤트 발생 여부 결정 (약 15% 확률로 텍스트 중계)
                if random.random() < 0.15: 
                    # 이벤트 발생!
                    team_idx = random.randint(0, 1)
                    if team_idx == 0:
                        team_code, team_name, roster = 'A', st.session_state.team_a, st.session_state.team_a_roster
                    else:
                        team_code, team_name, roster = 'B', st.session_state.team_b, st.session_state.team_b_roster
                    
                    # 득점 기회인지 판정
                    is_chance = random.random() < 0.35
                    msg, is_goal, scorer, assist, evt_type = generate_event(team_name, roster, is_chance)
                    
                    # 슈팅/골 통계 업데이트
                    update_event_stats(team_code, evt_type)
                    render_stats() # 통계판 다시 갱신 (슈팅 숫자 올라감)

                    icon = "🔴" if team_code == 'A' else "🔵"
                    full_msg = f"{icon} {team_name}: {msg}"
                    
                    st.write(f"**{minute}'** {full_msg}")
                    add_log(f"{minute}'", full_msg)
                    
                    if is_goal:
                        if team_code == 'A': st.session_state.score_a += 1
                        else: st.session_state.score_b += 1
                        add_goal(team_code, f"{minute}'", scorer, assist)
                        render_scoreboard() # 점수판 갱신
                    
                    # 이벤트가 터졌을 때는 읽을 시간을 줌
                    time.sleep(1.2)
                
                else:
                    # 이벤트가 없는 시간은 빠르게 지나감 (패스 숫자만 올라가는 시간)
                    time.sleep(0.1)
            
            add_log("HT", f"전반 종료. 스코어 {st.session_state.score_a} : {st.session_state.score_b}")
            st.session_state.match_stage = 'SECOND_HALF'
            st.rerun()

elif st.session_state.match_stage == 'SECOND_HALF':
    st.subheader("후반전")
    if st.button("후반전 시작", use_container_width=True):
        with st.spinner("후반전 진행 중..."):
            add_log("46'", "후반전 시작!")
            
            for minute in range(46, 91):
                update_per_minute_stats()
                render_stats()
                
                if random.random() < 0.15:
                    team_idx = random.randint(0, 1)
                    if team_idx == 0:
                        team_code, team_name, roster = 'A', st.session_state.team_a, st.session_state.team_a_roster
                    else:
                        team_code, team_name, roster = 'B', st.session_state.team_b, st.session_state.team_b_roster
                    
                    is_chance = random.random() < 0.35
                    msg, is_goal, scorer, assist, evt_type = generate_event(team_name, roster, is_chance)
                    
                    update_event_stats(team_code, evt_type)
                    render_stats()

                    icon = "🔴" if team_code == 'A' else "🔵"
                    full_msg = f"{icon} {team_name}: {msg}"
                    
                    st.write(f"**{minute}'** {full_msg}")
                    add_log(f"{minute}'", full_msg)
                    
                    if is_goal:
                        if team_code == 'A': st.session_state.score_a += 1
                        else: st.session_state.score_b += 1
                        add_goal(team_code, f"{minute}'", scorer, assist)
                        render_scoreboard()
                    
                    time.sleep(1.2)
                else:
                    time.sleep(0.1)
            
            add_log("FT", f"정규 시간 종료. 스코어 {st.session_state.score_a} : {st.session_state.score_b}")
            
            if st.session_state.score_a != st.session_state.score_b:
                st.session_state.match_stage = 'FINISHED'
            else:
                st.session_state.match_stage = 'EXTRA_TIME'
            st.rerun()

elif st.session_state.match_stage == 'EXTRA_TIME':
    st.info("정규 시간 종료. 무승부로 연장전에 돌입합니다.")
    if st.button("연장전 시작", use_container_width=True):
        with st.spinner("연장전 혈투 중..."):
            add_log("91'", "연장 전반 시작!")
            
            # 연장 전반 15분
            for minute in range(91, 106):
                update_per_minute_stats()
                render_stats()
                
                if random.random() < 0.2: # 연장은 좀 더 박진감 있게 (확률 높임)
                    team_idx = random.randint(0, 1)
                    if team_idx == 0:
                        team_code, team_name, roster = 'A', st.session_state.team_a, st.session_state.team_a_roster
                    else:
                        team_code, team_name, roster = 'B', st.session_state.team_b, st.session_state.team_b_roster
                    
                    msg, is_goal, scorer, assist, evt_type = generate_event(team_name, roster, is_goal_chance=True) # 기회 더 많이
                    update_event_stats(team_code, evt_type)
                    render_stats()
                    
                    icon = "🔴" if team_code == 'A' else "🔵"
                    full_msg = f"{icon} {team_name}: {msg}"
                    st.write(f"**{minute}'** {full_msg}")
                    add_log(f"{minute}'", full_msg)
                    
                    if is_goal:
                        if team_code == 'A': st.session_state.score_a += 1
                        else: st.session_state.score_b += 1
                        add_goal(team_code, f"{minute}'", scorer, assist)
                        render_scoreboard()
                    time.sleep(1.2)
                else:
                    time.sleep(0.1)
            
            add_log("105'", "연장 전반 종료. 진영 교체.")
            time.sleep(1)
            add_log("106'", "연장 후반 시작!")
            
            # 연장 후반 15분
            for minute in range(106, 121):
                update_per_minute_stats()
                render_stats()
                
                if random.random() < 0.2:
                    team_idx = random.randint(0, 1)
                    if team_idx == 0:
                        team_code, team_name, roster = 'A', st.session_state.team_a, st.session_state.team_a_roster
                    else:
                        team_code, team_name, roster = 'B', st.session_state.team_b, st.session_state.team_b_roster
                    
                    msg, is_goal, scorer, assist, evt_type = generate_event(team_name, roster, is_goal_chance=True)
                    update_event_stats(team_code, evt_type)
                    render_stats()
                    
                    icon = "🔴" if team_code == 'A' else "🔵"
                    full_msg = f"{icon} {team_name}: {msg}"
                    st.write(f"**{minute}'** {full_msg}")
                    add_log(f"{minute}'", full_msg)
                    
                    if is_goal:
                        if team_code == 'A': st.session_state.score_a += 1
                        else: st.session_state.score_b += 1
                        add_goal(team_code, f"{minute}'", scorer, assist)
                        render_scoreboard()
                    time.sleep(1.2)
                else:
                    time.sleep(0.1)
            
            add_log("ET", f"연장 종료. 스코어 {st.session_state.score_a} : {st.session_state.score_b}")
            
            if st.session_state.score_a != st.session_state.score_b:
                st.session_state.match_stage = 'FINISHED'
            else:
                st.session_state.match_stage = 'PENALTY'
            st.rerun()

elif st.session_state.match_stage == 'PENALTY':
    st.warning("연장전 종료. 승부차기를 시작합니다.")
    if st.button("승부차기 시작", use_container_width=True):
        with st.spinner("승부차기 진행 중..."):
            st.write("긴장되는 순간...")
            time.sleep(2)
            
            for i in range(1, 6): 
                st.write(f"[{i}번 키커] 🔴 {st.session_state.team_a} 준비합니다...")
                time.sleep(1.5)
                if random.random() < 0.75:
                    st.success("⚽ 골! 성공합니다!")
                    st.session_state.score_a += 1
                    add_log("PK", f"🔴 {st.session_state.team_a} {i}번 키커 득점 성공")
                else:
                    st.error("❌ 실축! 막힙니다!")
                    add_log("PK", f"🔴 {st.session_state.team_a} {i}번 키커 실축")
                render_scoreboard()
                time.sleep(1)
                
                st.write(f"[{i}번 키커] 🔵 {st.session_state.team_b} 준비합니다...")
                time.sleep(1.5)
                if random.random() < 0.75:
                    st.success("⚽ 골! 성공합니다!")
                    st.session_state.score_b += 1
                    add_log("PK", f"🔵 {st.session_state.team_b} {i}번 키커 득점 성공")
                else:
                    st.error("❌ 실축! 막힙니다!")
                    add_log("PK", f"🔵 {st.session_state.team_b} {i}번 키커 실축")
                render_scoreboard()
                time.sleep(1)
            
            while st.session_state.score_a == st.session_state.score_b:
                st.warning("서든데스 진행...")
                time.sleep(1)
                if random.random() < 0.5: st.session_state.score_a += 1
                if random.random() < 0.5: st.session_state.score_b += 1
                render_scoreboard()
                time.sleep(1)
            
            msg = f"승부차기 종료. 최종 스코어 {st.session_state.score_a} : {st.session_state.score_b}"
            st.write(msg)
            add_log("PK", msg)
            
            st.session_state.match_stage = 'FINISHED'
            st.rerun()

elif st.session_state.match_stage == 'FINISHED':
    st.balloons()
    if st.session_state.score_a > st.session_state.score_b:
        st.success(f"🎉 {st.session_state.team_a} 승리! 🎉")
    else:
        st.success(f"🎉 {st.session_state.team_b} 승리! 🎉")
    
    render_stats()

st.divider()
if st.button("🔄 다시 하기"):
    reset_game()
    st.rerun()