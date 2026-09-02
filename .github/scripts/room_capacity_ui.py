from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

MARKER = 'ROOM_CAPACITY_UI_V1'
if MARKER in s:
    raise SystemExit('ROOM_CAPACITY_UI_V1 already installed')

# 1) Lightweight capacity status styling.
anchor = '.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}\n/* HOST_SAFETY_V1 */'
insert = '''.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}
/* ROOM_CAPACITY_UI_V1 — live 10-public-room availability */
.roomCapacity{margin:12px 0 8px;padding:11px 12px;border:3px solid #9aa8ba;border-radius:14px;background:#f7fbff;font-weight:900;line-height:1.35}.roomCapacity.available{border-color:#237a3b;background:#e8f8ec;color:#155b2b}.roomCapacity.full{border-color:#a33b43;background:#fff0f1;color:#84252d}.roomCapacity.checking{color:#59677f}.roomCapacity .capacitySub{display:block;margin-top:3px;font-size:12px;font-weight:700;color:#66758d}
/* HOST_SAFETY_V1 */'''
if anchor not in s:
    raise SystemExit('CSS anchor not found')
s = s.replace(anchor, insert, 1)

# 2) Put availability and public hosting prominently on the home screen.
old_lobby = '<p class="small">Try the game against a bot, or join a live room with a 4-digit code.</p><button id="tryBot" class="btn primary">🤖 Try 3v3 vs Bots</button><div class="small">Browser-only demo · no room code needed</div><hr><input id="roomInput" class="code" maxlength="4" inputmode="numeric" placeholder="0000">'
new_lobby = '<p class="small">Try the game against bots, host a public live room, or join with a 4-digit code.</p><div id="roomCapacity" class="roomCapacity checking" aria-live="polite">Checking public room availability…</div><button id="createRoomBtn" class="btn primary" type="button">🏫 Create Public Live Room</button><div class="small">10 shared public rooms · a room slot returns about 2 minutes after the room becomes empty</div><button id="tryBot" class="btn">🤖 Try 3v3 vs Bots</button><div class="small">Browser-only demo · no room code needed</div><hr><input id="roomInput" class="code" maxlength="4" inputmode="numeric" placeholder="0000">'
if old_lobby not in s:
    raise SystemExit('Lobby anchor not found')
s = s.replace(old_lobby, new_lobby, 1)

# 3) Add DOM references.
old_refs = 'tryBotBtn=$("tryBot"),botSetup=$("botSetup"),'
new_refs = 'createRoomBtn=$("createRoomBtn"),roomCapacity=$("roomCapacity"),tryBotBtn=$("tryBot"),botSetup=$("botSetup"),'
if old_refs not in s:
    raise SystemExit('DOM refs anchor not found')
s = s.replace(old_refs, new_refs, 1)

# 4) Live capacity refresh and improved public-room creation handling.
old_create = 'async function createRoom(){msg.textContent="Creating room...";try{const r=await fetch(BACKEND+"/api/create-room",{method:"POST"}),d=await r.json();if(!r.ok){msg.textContent=d.full?"Public room creation is temporarily paused. Try again later.":(d.message||"Unable to create room.");return}openHost(d.code)}catch(e){msg.textContent="Unable to connect to Live Class."}}'
new_create = '''async function refreshRoomCapacity(){
  if(!roomCapacity)return;
  try{
    const r=await fetch(BACKEND+"/api/room-capacity",{cache:"no-store"}),d=await r.json();
    if(!r.ok)throw new Error("capacity");
    const cap=Math.max(0,Number(d.publicCapacity)||10),used=Math.max(0,Number(d.publicRoomsInUse)||0),left=Math.max(0,Number(d.publicRoomsAvailable)||0);
    roomCapacity.classList.remove("checking","available","full");
    roomCapacity.classList.add(left>0?"available":"full");
    roomCapacity.innerHTML=(left>0?"🟢 ":"🔴 ")+left+" of "+cap+" public rooms available"+'<span class="capacitySub">'+used+" in use · Creator Room is separately reserved</span>";
    if(createRoomBtn){createRoomBtn.disabled=left<=0;createRoomBtn.textContent=left>0?"🏫 Create Public Live Room":"⏳ Public Rooms Full"}
  }catch(e){
    roomCapacity.classList.remove("available","full");roomCapacity.classList.add("checking");roomCapacity.textContent="Live room availability temporarily unavailable.";
    if(createRoomBtn){createRoomBtn.disabled=false;createRoomBtn.textContent="🏫 Create Public Live Room"}
  }
}
async function createRoom(){
  if(createRoomBtn)createRoomBtn.disabled=true;msg.textContent="Creating public room...";
  try{
    const r=await fetch(BACKEND+"/api/create-room",{method:"POST"}),d=await r.json();
    if(!r.ok){msg.textContent=d.message||(d.full?"All public rooms are currently in use. Please try again later.":"Unable to create room.");await refreshRoomCapacity();return}
    openHost(d.code);refreshRoomCapacity()
  }catch(e){msg.textContent="Unable to connect to Live Class.";refreshRoomCapacity()}
}'''
if old_create not in s:
    raise SystemExit('createRoom anchor not found')
s = s.replace(old_create, new_create, 1)

# 5) Bind public host button.
old_bind = 'tryBotBtn.addEventListener("click",openBotSetup);'
new_bind = 'if(createRoomBtn)createRoomBtn.addEventListener("click",createRoom);tryBotBtn.addEventListener("click",openBotSetup);'
if old_bind not in s:
    raise SystemExit('Button binding anchor not found')
s = s.replace(old_bind, new_bind, 1)

# 6) Refresh immediately, and lightly while the lobby is visible.
old_init = 'setMap("compact");updateBoostUI();window.addEventListener("beforeunload",e=>{'
new_init = 'setMap("compact");updateBoostUI();refreshRoomCapacity();setInterval(()=>{if($("lobby").classList.contains("active"))refreshRoomCapacity()},30000);window.addEventListener("beforeunload",e=>{'
if old_init not in s:
    raise SystemExit('Init anchor not found')
s = s.replace(old_init, new_init, 1)

p.write_text(s, encoding='utf-8')
print('Installed ROOM_CAPACITY_UI_V1')
