from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_lobby = '''<section id="lobby" class="screen active"><div class="card"><h1>⭐ Math Star Chase and Bank</h1><div class="tag">⛩️ Sakura Arena · Solve. Grab. Bank. Win. 🌸</div><p class="small">Teachers create a room. Pupils join with the 4-digit code.</p><button id="tryBot" class="btn primary">🤖 Try the Game vs Bot</button><div class="small">Browser-only demo · no room code needed</div><button id="create" class="btn">Create Live Class Room</button><hr><input id="roomInput" class="code" maxlength="4" inputmode="numeric" placeholder="0000"><button id="join" class="btn">Join Room</button><div id="msg" class="msg"></div><details><summary><b>Creator Access</b></summary><input id="creatorPassword" class="text" type="password" placeholder="Creator password"><button id="creator" class="btn">Open Reserved Room</button></details></div></section>'''
new_lobby = '''<section id="lobby" class="screen active"><div class="card"><h1>⭐ Math Star Chase and Bank</h1><div class="tag">⛩️ Sakura Arena · Solve. Grab. Bank. Win. 🌸</div><p class="small">Try the game against a bot, or join a live room with a 4-digit code.</p><button id="tryBot" class="btn primary">🤖 Try the Game vs Bot</button><div class="small">Browser-only demo · no room code needed</div><hr><input id="roomInput" class="code" maxlength="4" inputmode="numeric" placeholder="0000"><button id="join" class="btn">Join Room</button><div id="msg" class="msg"></div><details><summary><b>Creator Access</b></summary><p class="small">Live class hosting is password protected.</p><input id="creatorPassword" class="text" type="password" placeholder="Creator password"><button id="creator" class="btn">🔒 Open Live Class Room</button></details></div></section>'''
if old_lobby not in s:
    raise SystemExit('Lobby marker not found')
s = s.replace(old_lobby, new_lobby, 1)

old_decl = 'tryBotBtn=$("tryBot"),createBtn=$("create"),joinBtn=$("join"),creatorBtn=$("creator"),roomInput=$("roomInput"),msg=$("msg"),creatorPassword=$("creatorPassword"),'
new_decl = 'tryBotBtn=$("tryBot"),joinBtn=$("join"),creatorBtn=$("creator"),roomInput=$("roomInput"),msg=$("msg"),creatorPassword=$("creatorPassword"),'
if old_decl not in s:
    raise SystemExit('Button declaration marker not found')
s = s.replace(old_decl, new_decl, 1)

old_bind = 'createBtn.addEventListener("click",createRoom);joinBtn.addEventListener("click",joinRoom);creatorBtn.addEventListener("click",creatorRoom);'
new_bind = 'joinBtn.addEventListener("click",joinRoom);creatorBtn.addEventListener("click",creatorRoom);'
if old_bind not in s:
    raise SystemExit('Button binding marker not found')
s = s.replace(old_bind, new_bind, 1)

p.write_text(s, encoding='utf-8')
