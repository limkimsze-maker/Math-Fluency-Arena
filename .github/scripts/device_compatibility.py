from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'OBSERVER_GUEST_V1' in s:
    raise SystemExit('Observer guest mode is already installed')

# 1) Styling for the invited observer PIN and guest observer screen.
css_marker = '.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}\n'
css_add = '''.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}
/* OBSERVER_GUEST_V1 */
.observerPin{font-size:28px;letter-spacing:5px;margin:4px 0 6px}.observerGuest #hostGameRoster,.observerGuest #hostRankingTitle,.observerGuest #hostRoundRanking,.observerGuest #playAgain{display:none!important}.observerGuest .observerPanel{margin-bottom:8px}
'''
if css_marker not in s:
    raise SystemExit('CSS marker not found')
s = s.replace(css_marker, css_add, 1)

# 2) Public lobby: invited observers use the room code plus a separate PIN.
old_lobby = '''<section id="lobby" class="screen active"><div class="card"><h1>⭐ Math Star Chase and Bank</h1><div class="tag">⛩️ Sakura Arena · Solve. Grab. Bank. Win. 🌸</div><p class="small">Try the game against a bot, or join a live room with a 4-digit code.</p><button id="tryBot" class="btn primary">🤖 Try the Game vs Bot</button><div class="small">Browser-only demo · no room code needed</div><hr><input id="roomInput" class="code" maxlength="4" inputmode="numeric" placeholder="0000"><button id="join" class="btn">Join Room</button><div id="msg" class="msg"></div><details><summary><b>Creator Access</b></summary><p class="small">Live class hosting is password protected.</p><input id="creatorPassword" class="text" type="password" placeholder="Creator password"><button id="creator" class="btn">🔒 Open Live Class Room</button></details></div></section>'''
new_lobby = '''<section id="lobby" class="screen active"><div class="card"><h1>⭐ Math Star Chase and Bank</h1><div class="tag">⛩️ Sakura Arena · Solve. Grab. Bank. Win. 🌸</div><p class="small">Try the game against a bot, or join a live room with a 4-digit code.</p><button id="tryBot" class="btn primary">🤖 Try the Game vs Bot</button><div class="small">Browser-only demo · no room code needed</div><hr><input id="roomInput" class="code" maxlength="4" inputmode="numeric" placeholder="0000"><button id="join" class="btn">Join Room</button><details><summary><b>👁️ Observer Access</b></summary><p class="small">Invited observers need the room code above and the separate Observer PIN.</p><input id="observerPinInput" class="text" maxlength="4" inputmode="numeric" placeholder="Observer PIN"><button id="joinObserver" class="btn">👁️ Join as Observer</button></details><div id="msg" class="msg"></div><details><summary><b>Creator Access</b></summary><p class="small">Live class hosting is password protected.</p><input id="creatorPassword" class="text" type="password" placeholder="Creator password"><button id="creator" class="btn">🔒 Open Live Class Room</button></details></div></section>'''
if old_lobby not in s:
    raise SystemExit('Lobby marker not found')
s = s.replace(old_lobby, new_lobby, 1)

# 3) Host lobby: show a session-only observer PIN that the creator can share.
old_host = '<section id="hostLobby" class="screen"><div class="card"><h1>Class Lobby</h1><p class="small">Share this room code with your pupils.</p><div id="hostRoomCode" class="room"></div><div class="hostGrid">'
new_host = '<section id="hostLobby" class="screen"><div class="card"><h1>Class Lobby</h1><p class="small">Share this room code with your pupils.</p><div id="hostRoomCode" class="room"></div><p class="small"><b>👁️ Observer PIN</b></p><div id="hostObserverPin" class="room observerPin"></div><p class="small">Share the Observer PIN only with invited observers. They can watch the arena and follow players, but cannot control the game.</p><div class="hostGrid">'
if old_host not in s:
    raise SystemExit('Host lobby marker not found')
s = s.replace(old_host, new_host, 1)

# 4) Host/guest observer panel wording and a hideable ranking heading.
s = s.replace('<div class="observerPanel"><div class="observerToolbar"><b>👁️ Teacher Observer</b>', '<div class="observerPanel"><div class="observerToolbar"><b>👁️ Live Observer</b>', 1)
s = s.replace('Whole Game shows the entire arena. Choose a pupil to follow that player. Observer mode has no game controls.', 'Whole Game shows the entire arena. Choose a player to follow. Observer mode has no game controls.', 1)
s = s.replace('<div id="hostGameRoster" class="roster"></div><h2>Player Ranking</h2><div id="hostRoundRanking">', '<div id="hostGameRoster" class="roster"></div><h2 id="hostRankingTitle">Player Ranking</h2><div id="hostRoundRanking">', 1)

# 5) Element references and observer session state.
old_refs = 'tryBotBtn=$("tryBot"),joinBtn=$("join"),creatorBtn=$("creator"),roomInput=$("roomInput"),msg=$("msg"),creatorPassword=$("creatorPassword"),\nhostRoomCode=$("hostRoomCode"),hostGameCode=$("hostGameCode"),playerCount=$("playerCount"),blueCount=$("blueCount"),redCount=$("redCount"),roster=$("roster"),startRoundBtn=$("startRound"),hostMsg=$("hostMsg"),'
new_refs = 'tryBotBtn=$("tryBot"),joinBtn=$("join"),joinObserverBtn=$("joinObserver"),creatorBtn=$("creator"),roomInput=$("roomInput"),observerPinInput=$("observerPinInput"),msg=$("msg"),creatorPassword=$("creatorPassword"),\nhostRoomCode=$("hostRoomCode"),hostObserverPin=$("hostObserverPin"),hostGameCode=$("hostGameCode"),playerCount=$("playerCount"),blueCount=$("blueCount"),redCount=$("redCount"),roster=$("roster"),startRoundBtn=$("startRound"),hostMsg=$("hostMsg"),'
if old_refs not in s:
    raise SystemExit('Reference marker not found')
s = s.replace(old_refs, new_refs, 1)

old_state = 'let room="",name="",team=null,socket=null,isHost=false,teamAssigned=false,x=100,y=100,starX=300,starY=220,carried=0,immuneUntil=0,blue=0,red=0,streak=0,bestStreak=0,boostStarStreak=0,boostReady=false,boostUntil=0,qOpen=false,qLock=false,questionMode="star",stealTargetId=null,stealTargetName="",mathMode="add20",mapKey="compact",roundStart=0,roundEnd=0,roundActive=false,finished=false,lastFrame=performance.now(),lastSend=0,lastHeartbeat=0,lastBank=0,moved=false,toastTimer,hostTicker=null,facing="right",observerTarget="overview",demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0;'
new_state = 'let room="",name="",team=null,socket=null,isHost=false,isObserver=false,observerAuthorized=false,observerPin="",pendingObserverPin="",teamAssigned=false,x=100,y=100,starX=300,starY=220,carried=0,immuneUntil=0,blue=0,red=0,streak=0,bestStreak=0,boostStarStreak=0,boostReady=false,boostUntil=0,qOpen=false,qLock=false,questionMode="star",stealTargetId=null,stealTargetName="",mathMode="add20",mapKey="compact",roundStart=0,roundEnd=0,roundActive=false,finished=false,lastFrame=performance.now(),lastSend=0,lastHeartbeat=0,lastBank=0,moved=false,toastTimer,hostTicker=null,facing="right",observerTarget="overview",demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0;'
if old_state not in s:
    raise SystemExit('State marker not found')
s = s.replace(old_state, new_state, 1)

# 6) Player join remains a player join; add invited observer join.
old_join = '''async function joinRoom(){const code=roomInput.value.replace(/\\D/g,"").slice(0,4);if(code.length!==4){msg.textContent="Enter a 4-digit room code.";return}try{const r=await fetch(BACKEND+"/api/join-room?code="+code);if(!r.ok){msg.textContent="Room "+code+" is not active.";return}isHost=false;room=code;nameRoom.textContent=room;nameMsg.textContent="";show($("nameScreen"));setTimeout(()=>playerName.focus(),50)}catch(e){msg.textContent="Unable to check the room."}}
'''
new_join = '''async function joinRoom(){const code=roomInput.value.replace(/\\D/g,"").slice(0,4);if(code.length!==4){msg.textContent="Enter a 4-digit room code.";return}try{const r=await fetch(BACKEND+"/api/join-room?code="+code);if(!r.ok){msg.textContent="Room "+code+" is not active.";return}isHost=false;isObserver=false;observerAuthorized=false;pendingObserverPin="";room=code;nameRoom.textContent=room;nameMsg.textContent="";show($("nameScreen"));setTimeout(()=>playerName.focus(),50)}catch(e){msg.textContent="Unable to check the room."}}
async function joinObserver(){const code=roomInput.value.replace(/\\D/g,"").slice(0,4),pin=observerPinInput.value.replace(/\\D/g,"").slice(0,4);if(code.length!==4){msg.textContent="Enter the 4-digit room code first.";return}if(pin.length!==4){msg.textContent="Enter the 4-digit Observer PIN.";return}msg.textContent="Checking observer access…";try{const r=await fetch(BACKEND+"/api/join-room?code="+code);if(!r.ok){msg.textContent="Room "+code+" is not active.";return}if(socket){try{socket.close()}catch(e){}socket=null}isHost=false;isObserver=true;observerAuthorized=false;pendingObserverPin=pin;room=code;hostGameCode.textContent=room;$("hostGame").classList.add("observerGuest");show($("hostGame"));hostPhase.textContent="Checking Observer PIN…";hostTimer.textContent="—";hostBlueScore.textContent="0";hostRedScore.textContent="0";observerLabel.textContent="Waiting for observer access…";connectSocket()}catch(e){msg.textContent="Unable to check the room."}}
'''
if old_join not in s:
    raise SystemExit('Join marker not found')
s = s.replace(old_join, new_join, 1)

# 7) Host creates a fresh observer PIN for each live hosting session.
old_openhost = 'function openHost(code){isHost=true;room=String(code);hostRoomCode.textContent=room;hostGameCode.textContent=room;show($("hostLobby"));renderLocalRecords();connectSocket();startHostTicker()}'
new_openhost = 'function openHost(code){isHost=true;isObserver=false;observerAuthorized=false;pendingObserverPin="";observerPin=String(Math.floor(1000+Math.random()*9000));room=String(code);hostRoomCode.textContent=room;hostObserverPin.textContent=observerPin;hostGameCode.textContent=room;$("hostGame").classList.remove("observerGuest");show($("hostLobby"));renderLocalRecords();connectSocket();startHostTicker()}'
if old_openhost not in s:
    raise SystemExit('openHost marker not found')
s = s.replace(old_openhost, new_openhost, 1)

# 8) Bot demo must leave observer mode.
s = s.replace('demoMode=true;isHost=false;room="BOT";name="You";team="blue";teamAssigned=true;observerTarget="overview";', 'demoMode=true;isHost=false;isObserver=false;observerAuthorized=false;room="BOT";name="You";team="blue";teamAssigned=true;observerTarget="overview";', 1)

# 9) WebSocket observer handshake. The PIN is checked by the host and observers never enter a team.
old_connect = 'function connectSocket(){if(socket&&socket.readyState<=1)return;socket=new WebSocket(WS+"/room/"+encodeURIComponent(room));socket.addEventListener("open",()=>{if(isHost){send({type:"hostHello",id:playerId});send({type:"needPlayers",id:playerId});renderHostRoster()}else{status.textContent="CONNECTED ✓";requestTeam()}});socket.addEventListener("close",()=>{if(!isHost)status.textContent="DISCONNECTED"});socket.addEventListener("error",()=>{if(!isHost)status.textContent="CONNECTION ERROR"});socket.addEventListener("message",e=>{try{handle(JSON.parse(e.data))}catch(err){console.error(err)}})}'
new_connect = 'function connectSocket(){if(socket&&socket.readyState<=1)return;socket=new WebSocket(WS+"/room/"+encodeURIComponent(room));socket.addEventListener("open",()=>{if(isHost){send({type:"hostHello",id:playerId});send({type:"needPlayers",id:playerId});renderHostRoster()}else if(isObserver){requestObserverAccess()}else{status.textContent="CONNECTED ✓";requestTeam()}});socket.addEventListener("close",()=>{if(isObserver&&!observerAuthorized){show($("lobby"));msg.textContent="Observer connection closed. Try again."}else if(!isHost&&!isObserver)status.textContent="DISCONNECTED"});socket.addEventListener("error",()=>{if(isObserver&&!observerAuthorized){show($("lobby"));msg.textContent="Observer connection error."}else if(!isHost&&!isObserver)status.textContent="CONNECTION ERROR"});socket.addEventListener("message",e=>{try{handle(JSON.parse(e.data))}catch(err){console.error(err)}})}'
if old_connect not in s:
    raise SystemExit('connectSocket marker not found')
s = s.replace(old_connect, new_connect, 1)

old_handle_start = '''function handle(d){
 if(d.type==="joinRequest"&&isHost){assignFromHost(d);return}
 if(d.type==="needPlayers"&&teamAssigned){sendState();return}
 if(d.type==="teamAssigned"&&d.targetId===playerId&&!isHost){acceptTeam(d);return}
 if((d.type==="playerState"||d.type==="move")&&d.id!==playerId){upsert(d);if(isHost)renderHostRoster();return}
 if(d.type==="playerLeft"){players.delete(d.id);if(isHost)renderHostRoster();return}
 if(d.type==="startRound"){beginRound(d.startAt,d.endAt,d.mathMode,d.mapKey);return}
 if(d.type==="hostSync"){applyHostSync(d);return}
'''
new_handle_start = '''function handle(d){
 if(d.type==="joinRequest"&&isHost){assignFromHost(d);return}
 if(d.type==="observerJoinRequest"&&isHost){authorizeObserver(d);return}
 if(d.type==="observerAccepted"&&d.targetId===playerId&&isObserver){acceptObserver(d);return}
 if(d.type==="observerDenied"&&d.targetId===playerId&&isObserver){denyObserver();return}
 if(d.type==="needPlayers"&&teamAssigned){sendState();return}
 if(d.type==="teamAssigned"&&d.targetId===playerId&&!isHost&&!isObserver){acceptTeam(d);return}
 if((d.type==="playerState"||d.type==="move")&&d.id!==playerId){upsert(d);if(isHost)renderHostRoster();return}
 if(d.type==="playerLeft"){players.delete(d.id);if(isHost)renderHostRoster();else if(isObserver)updateObserver();return}
 if(d.type==="startRound"){if(isObserver){beginObserverRound(d.startAt,d.endAt,d.mathMode,d.mapKey)}else beginRound(d.startAt,d.endAt,d.mathMode,d.mapKey);return}
 if(d.type==="hostSync"){applyHostSync(d);return}
'''
if old_handle_start not in s:
    raise SystemExit('handle marker not found')
s = s.replace(old_handle_start, new_handle_start, 1)

request_marker = 'function requestTeam(){send({type:"joinRequest",id:playerId,name,ts:Date.now()});setTimeout(()=>{if(!teamAssigned&&socket&&socket.readyState===1)requestTeam()},1200)}\n'
observer_functions = '''function requestObserverAccess(){if(!isObserver||observerAuthorized||!pendingObserverPin)return;send({type:"observerJoinRequest",id:playerId,pin:pendingObserverPin,ts:Date.now()});setTimeout(()=>{if(isObserver&&!observerAuthorized&&socket&&socket.readyState===1)requestObserverAccess()},1400)}
function authorizeObserver(d){const ok=String(d.pin||"")===observerPin&&observerPin.length===4;if(!ok){send({type:"observerDenied",targetId:d.id,ts:Date.now()});return}send({type:"observerAccepted",targetId:d.id,blue,red,roundStart,roundEnd,mathMode,mapKey,active:roundActive&&!finished,finished,ts:Date.now()})}
function acceptObserver(d){observerAuthorized=true;pendingObserverPin="";observerPinInput.value="";msg.textContent="";hostGameCode.textContent=room;$("hostGame").classList.add("observerGuest");show($("hostGame"));applyObserverSync(d);send({type:"needPlayers",id:playerId});requestAnimationFrame(updateObserver)}
function denyObserver(){observerAuthorized=false;pendingObserverPin="";isObserver=false;if(socket){try{socket.close()}catch(e){}socket=null}show($("lobby"));msg.textContent="Observer PIN incorrect. Ask the room creator for the current PIN."}
function beginObserverRound(s,e,mode=mathMode,map=mapKey){setMathMode(mode);setMap(map);roundStart=Number(s)||Date.now()+1000;roundEnd=Number(e)||roundStart+ROUND;roundActive=true;finished=false;blue=0;red=0;score();hostGameCode.textContent=room;$("hostGame").classList.add("observerGuest");show($("hostGame"));hostPhase.textContent="Get ready…";hostTimer.textContent="3:00";renderObserverMap();refreshObserverSelect();send({type:"needPlayers",id:playerId});requestAnimationFrame(updateObserver)}
function applyObserverSync(d){if(d.mathMode)setMathMode(d.mathMode);if(d.mapKey)setMap(d.mapKey);blue=Math.max(0,Number(d.blue)||0);red=Math.max(0,Number(d.red)||0);score();roundStart=Number(d.roundStart)||0;roundEnd=Number(d.roundEnd)||0;finished=!!d.finished;roundActive=!!d.active&&roundEnd>Date.now();hostModeLabel.textContent=modeNames[mathMode]||mathMode;hostMapLabel.textContent=(mapProfiles[mapKey]||mapProfiles.compact).name;if(roundActive){hostPhase.textContent=Date.now()<roundStart?"Get ready…":"Round in progress";updateRoundClock()}else if(finished){hostTimer.textContent="0:00";hostPhase.textContent=blue===red?"Draw!":blue>red?"🔵 Blue Wins!":"🔴 Red Wins!"}else{hostTimer.textContent="—";hostPhase.textContent="Waiting for the host to start a round."}renderObserverMap();refreshObserverSelect();updateObserver()}
'''
if request_marker not in s:
    raise SystemExit('requestTeam marker not found')
s = s.replace(request_marker, request_marker + observer_functions, 1)

# 10) Observer clients render the observer world rather than player sprites.
old_upsert = 'function upsert(d){if(!d.team)return;const p={...(players.get(d.id)||{}),id:d.id,name:safe(d.name)||"Player",team:d.team,x:Number(d.x)||100,y:Number(d.y)||100,starX:Number(d.starX)||0,starY:Number(d.starY)||0,carried:Number(d.carried)||0,immuneUntil:Number(d.immuneUntil)||0,boostUntil:Number(d.boostUntil)||0,facing:d.facing==="left"?"left":"right",lastSeen:Date.now()};players.set(d.id,p);if(!isHost)drawRemote(p);else updateObserver()}'
new_upsert = 'function upsert(d){if(!d.team)return;const p={...(players.get(d.id)||{}),id:d.id,name:safe(d.name)||"Player",team:d.team,x:Number(d.x)||100,y:Number(d.y)||100,starX:Number(d.starX)||0,starY:Number(d.starY)||0,carried:Number(d.carried)||0,immuneUntil:Number(d.immuneUntil)||0,boostUntil:Number(d.boostUntil)||0,facing:d.facing==="left"?"left":"right",lastSeen:Date.now()};players.set(d.id,p);if(isHost||isObserver)updateObserver();else drawRemote(p)}'
if old_upsert not in s:
    raise SystemExit('upsert marker not found')
s = s.replace(old_upsert, new_upsert, 1)

s = s.replace('function updateObserver(){if(!isHost||!observerArena||!observerWorld)return;', 'function updateObserver(){if((!isHost&&!isObserver)||!observerArena||!observerWorld)return;', 1)

# 11) Round clock/finish/sync have a non-playing observer path.
s = s.replace('if(isHost){hostPhase.textContent="Starting in "+n+"…"}else{startCount.style.display="block";startCount.textContent=n}', 'if(isHost||isObserver){hostPhase.textContent="Starting in "+n+"…"}else{startCount.style.display="block";startCount.textContent=n}', 1)
s = s.replace('if(!isHost&&waiting.classList.contains("open")){waiting.classList.remove("open");startCount.style.display="none";hint.textContent="Your next ⭐ is nearby — chase it, solve, then bank!"}\n if(isHost)hostPhase.textContent="Round in progress";', 'if(!isHost&&!isObserver&&waiting.classList.contains("open")){waiting.classList.remove("open");startCount.style.display="none";hint.textContent="Your next ⭐ is nearby — chase it, solve, then bank!"}\n if(isHost||isObserver)hostPhase.textContent="Round in progress";', 1)
s = s.replace('if(isHost)hostTimer.textContent=txt;else timer.textContent=txt}', 'if(isHost||isObserver)hostTimer.textContent=txt;else timer.textContent=txt}', 1)

old_finish = 'function finish(){if(finished)return;finished=true;roundActive=false;boostReady=false;boostUntil=0;updateBoostUI();stop();if(isHost){hostTimer.textContent="0:00";hostPhase.textContent=blue===red?"Draw!":blue>red?"🔵 Blue Wins!":"🔴 Red Wins!";playAgain.style.display="block";archiveHostRound();sendHostSync();return}'
new_finish = 'function finish(){if(finished)return;finished=true;roundActive=false;boostReady=false;boostUntil=0;updateBoostUI();stop();if(isObserver){hostTimer.textContent="0:00";hostPhase.textContent=blue===red?"Draw!":blue>red?"🔵 Blue Wins!":"🔴 Red Wins!";updateObserver();return}if(isHost){hostTimer.textContent="0:00";hostPhase.textContent=blue===red?"Draw!":blue>red?"🔵 Blue Wins!":"🔴 Red Wins!";playAgain.style.display="block";archiveHostRound();sendHostSync();return}'
if old_finish not in s:
    raise SystemExit('finish marker not found')
s = s.replace(old_finish, new_finish, 1)

old_apply_sync = 'function applyHostSync(d){if(isHost)return;if(d.mathMode)setMathMode(d.mathMode);if(d.mapKey)setMap(d.mapKey);blue=Math.max(blue,Number(d.blue)||0);red=Math.max(red,Number(d.red)||0);score();const e=Number(d.roundEnd)||0,s=Number(d.roundStart)||0;if(d.active&&e>Date.now()&&!roundActive)beginRound(s,e,d.mathMode||mathMode,d.mapKey||mapKey)}'
new_apply_sync = 'function applyHostSync(d){if(isHost)return;if(isObserver){if(observerAuthorized)applyObserverSync(d);return}if(d.mathMode)setMathMode(d.mathMode);if(d.mapKey)setMap(d.mapKey);blue=Math.max(blue,Number(d.blue)||0);red=Math.max(red,Number(d.red)||0);score();const e=Number(d.roundEnd)||0,s=Number(d.roundStart)||0;if(d.active&&e>Date.now()&&!roundActive)beginRound(s,e,d.mathMode||mathMode,d.mapKey||mapKey)}'
if old_apply_sync not in s:
    raise SystemExit('applyHostSync marker not found')
s = s.replace(old_apply_sync, new_apply_sync, 1)

# 12) Controls and responsive observer rendering.
old_binds = 'tryBotBtn.addEventListener("click",startBotDemo);joinBtn.addEventListener("click",joinRoom);creatorBtn.addEventListener("click",creatorRoom);roomInput.addEventListener("input",()=>roomInput.value=roomInput.value.replace(/\\D/g,""));roomInput.addEventListener("keydown",e=>{if(e.key==="Enter")joinRoom()});creatorPassword.addEventListener("keydown",e=>{if(e.key==="Enter")creatorRoom()});'
new_binds = 'tryBotBtn.addEventListener("click",startBotDemo);joinBtn.addEventListener("click",joinRoom);joinObserverBtn.addEventListener("click",joinObserver);creatorBtn.addEventListener("click",creatorRoom);roomInput.addEventListener("input",()=>roomInput.value=roomInput.value.replace(/\\D/g,""));observerPinInput.addEventListener("input",()=>observerPinInput.value=observerPinInput.value.replace(/\\D/g,""));roomInput.addEventListener("keydown",e=>{if(e.key==="Enter")joinRoom()});observerPinInput.addEventListener("keydown",e=>{if(e.key==="Enter")joinObserver()});creatorPassword.addEventListener("keydown",e=>{if(e.key==="Enter")creatorRoom()});'
if old_binds not in s:
    raise SystemExit('Binding marker not found')
s = s.replace(old_binds, new_binds, 1)
s = s.replace('window.addEventListener("resize",()=>{if(teamAssigned)updateCamera();if(isHost)updateObserver()});window.addEventListener("orientationchange",()=>setTimeout(()=>{if(teamAssigned)updateCamera();if(isHost)updateObserver()},120))', 'window.addEventListener("resize",()=>{if(teamAssigned)updateCamera();if(isHost||isObserver)updateObserver()});window.addEventListener("orientationchange",()=>setTimeout(()=>{if(teamAssigned)updateCamera();if(isHost||isObserver)updateObserver()},120))', 1)

p.write_text(s, encoding='utf-8')
