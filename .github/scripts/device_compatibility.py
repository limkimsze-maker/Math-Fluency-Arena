from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'HOST_SAFETY_V1' in s:
    raise SystemExit('Host safety notice is already installed')

# 1) Host safety styling.
css_marker = '/* OBSERVER_GUEST_V1 */\n'
css_add = '''/* HOST_SAFETY_V1 */
.hostSafetyWarn{margin:12px 0;padding:12px;border:3px solid #a85b00;border-radius:14px;background:#fff3d9;color:#6f3a00;font-size:14px;font-weight:800;line-height:1.45;text-align:left}.safeCloseNotice{display:none;margin:12px 0;padding:14px;border:3px solid #237a3b;border-radius:14px;background:#e8f8ec;color:#155b2b;font-size:18px;font-weight:900;text-align:center;box-shadow:0 3px 0 rgba(23,32,51,.12)}.observerGuest .hostSafetyWarn,.observerGuest .safeCloseNotice{display:none!important}
/* OBSERVER_GUEST_V1 */
'''
if css_marker not in s:
    raise SystemExit('CSS marker not found')
s = s.replace(css_marker, css_add, 1)

# 2) Put the repercussions and safe-to-close message on both host screens.
old_lobby_msg = '<div id="hostMsg" class="msg">The button activates when at least one pupil is ready.</div>'
new_lobby_msg = old_lobby_msg + '<div id="hostSafetyLobby" class="hostSafetyWarn">⚠️ <b>Keep this host page open while the live session is in use.</b> Closing or refreshing it disconnects the host, may stop new players from being assigned, removes the host controls and Teacher Observer view, may prevent local player results from being recorded, and can eventually cause the room code to be released.</div><div id="safeCloseLobby" class="safeCloseNotice">✅ All players have finished and left the live room. It is now safe to close this host page.</div>'
if old_lobby_msg not in s:
    raise SystemExit('Host lobby message marker not found')
s = s.replace(old_lobby_msg, new_lobby_msg, 1)

old_game_roster = '<div id="hostGameRoster" class="roster"></div><h2 id="hostRankingTitle">Player Ranking</h2>'
new_game_roster = '<div id="hostGameRoster" class="roster"></div><div id="hostSafetyGame" class="hostSafetyWarn">⚠️ <b>Keep this host page open while players are connected.</b> Closing or refreshing it disconnects the host, may stop new players from joining correctly, removes host/observer controls, and may prevent local results from being recorded.</div><div id="safeCloseGame" class="safeCloseNotice">✅ All players have finished and left the live room. It is now safe to close this host page.</div><h2 id="hostRankingTitle">Player Ranking</h2>'
if old_game_roster not in s:
    raise SystemExit('Host game roster marker not found')
s = s.replace(old_game_roster, new_game_roster, 1)

# 3) Element references.
old_refs = 'hostRoomCode=$("hostRoomCode"),hostObserverPin=$("hostObserverPin"),hostGameCode=$("hostGameCode"),playerCount=$("playerCount"),blueCount=$("blueCount"),redCount=$("redCount"),roster=$("roster"),startRoundBtn=$("startRound"),hostMsg=$("hostMsg"),\nhostTimer=$("hostTimer"),hostBlueScore=$("hostBlueScore"),hostRedScore=$("hostRedScore"),hostPhase=$("hostPhase"),hostGameRoster=$("hostGameRoster"),observerSelect=$("observerSelect"),'
new_refs = 'hostRoomCode=$("hostRoomCode"),hostObserverPin=$("hostObserverPin"),hostGameCode=$("hostGameCode"),playerCount=$("playerCount"),blueCount=$("blueCount"),redCount=$("redCount"),roster=$("roster"),startRoundBtn=$("startRound"),hostMsg=$("hostMsg"),hostSafetyLobby=$("hostSafetyLobby"),safeCloseLobby=$("safeCloseLobby"),\nhostTimer=$("hostTimer"),hostBlueScore=$("hostBlueScore"),hostRedScore=$("hostRedScore"),hostPhase=$("hostPhase"),hostGameRoster=$("hostGameRoster"),hostSafetyGame=$("hostSafetyGame"),safeCloseGame=$("safeCloseGame"),observerSelect=$("observerSelect"),'
if old_refs not in s:
    raise SystemExit('Element reference marker not found')
s = s.replace(old_refs, new_refs, 1)

# 4) Track whether players actually participated and whether closing is safe.
old_state_tail = 'demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0;'
new_state_tail = 'demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0,hostHadPlayers=false,safeToClose=false;'
if old_state_tail not in s:
    raise SystemExit('State marker not found')
s = s.replace(old_state_tail, new_state_tail, 1)

# 5) Reset safety state whenever a creator opens a fresh live room.
old_open = 'function openHost(code){isHost=true;isObserver=false;observerAuthorized=false;pendingObserverPin="";observerPin=String(Math.floor(1000+Math.random()*9000));room=String(code);hostRoomCode.textContent=room;hostObserverPin.textContent=observerPin;hostGameCode.textContent=room;$("hostGame").classList.remove("observerGuest");show($("hostLobby"));renderLocalRecords();connectSocket();startHostTicker()}'
new_open = 'function openHost(code){isHost=true;isObserver=false;observerAuthorized=false;pendingObserverPin="";hostHadPlayers=false;safeToClose=false;document.title="Math Star Chase and Bank";if(hostSafetyLobby)hostSafetyLobby.style.display="block";if(hostSafetyGame)hostSafetyGame.style.display="block";if(safeCloseLobby)safeCloseLobby.style.display="none";if(safeCloseGame)safeCloseGame.style.display="none";observerPin=String(Math.floor(1000+Math.random()*9000));room=String(code);hostRoomCode.textContent=room;hostObserverPin.textContent=observerPin;hostGameCode.textContent=room;$("hostGame").classList.remove("observerGuest");show($("hostLobby"));renderLocalRecords();connectSocket();startHostTicker()}'
if old_open not in s:
    raise SystemExit('openHost marker not found')
s = s.replace(old_open, new_open, 1)

# 6) Update the safety state from the live roster. Green message appears only after a round has finished and all players have left.
old_roster_start = 'function renderHostRoster(){if(!isHost)return;const now=Date.now();for(const[id,p]of players){if(now-(p.lastSeen||0)>20000)players.delete(id)}refreshObserverSelect();updateObserver();const list=[...players.values()].sort((a,b)=>a.team.localeCompare(b.team)||a.name.localeCompare(b.name));const bc=list.filter(p=>p.team==="blue").length,rc=list.filter(p=>p.team==="red").length;'
new_roster_start = 'function renderHostRoster(){if(!isHost)return;const now=Date.now();for(const[id,p]of players){if(now-(p.lastSeen||0)>20000)players.delete(id)}refreshObserverSelect();updateObserver();const list=[...players.values()].sort((a,b)=>a.team.localeCompare(b.team)||a.name.localeCompare(b.name));if(list.length>0)hostHadPlayers=true;safeToClose=!!(finished&&hostHadPlayers&&list.length===0);if(hostSafetyLobby)hostSafetyLobby.style.display=safeToClose?"none":"block";if(hostSafetyGame)hostSafetyGame.style.display=safeToClose?"none":"block";if(safeCloseLobby)safeCloseLobby.style.display=safeToClose?"block":"none";if(safeCloseGame)safeCloseGame.style.display=safeToClose?"block":"none";if(safeToClose)document.title="✅ Safe to close · Math Star Chase";else document.title="🔴 LIVE HOST · Keep Open";const bc=list.filter(p=>p.team==="blue").length,rc=list.filter(p=>p.team==="red").length;'
if old_roster_start not in s:
    raise SystemExit('renderHostRoster marker not found')
s = s.replace(old_roster_start, new_roster_start, 1)

# 7) Native browser leave confirmation while the host session is not yet safe to close.
old_unload = 'window.addEventListener("beforeunload",()=>{if(!isHost&&teamAssigned)send({type:"playerLeft",id:playerId})})'
new_unload = 'window.addEventListener("beforeunload",e=>{if(isHost&&!safeToClose){e.preventDefault();e.returnValue="";return}if(!isHost&&teamAssigned)send({type:"playerLeft",id:playerId})})'
if old_unload not in s:
    raise SystemExit('beforeunload marker not found')
s = s.replace(old_unload, new_unload, 1)

p.write_text(s, encoding='utf-8')
