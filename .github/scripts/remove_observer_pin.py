from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'OBSERVER_PIN_REMOVED_V1' in s:
    raise SystemExit('Observer PIN removal patch already applied')

# Remove the guest Observer Access controls from the home page.
s, n = re.subn(
    r'<details><summary><b>👁️ Observer Access</b></summary><p class="small">Invited observers need the room code above and the separate Observer PIN\.</p><input id="observerPinInput" class="text" maxlength="4" inputmode="numeric" placeholder="Observer PIN"><button id="joinObserver" class="btn">👁️ Join as Observer</button></details>',
    '',
    s,
    count=1,
)
if n != 1:
    raise SystemExit('Could not find home-page Observer Access block')

# Remove the PIN display from the host lobby; the host already has the live observer view.
s, n = re.subn(
    r'<p class="small"><b>👁️ Observer PIN</b></p><div id="hostObserverPin" class="room observerPin"></div><p class="small">Share the Observer PIN only with invited observers\. They can watch the arena and follow players, but cannot control the game\.</p>',
    '',
    s,
    count=1,
)
if n != 1:
    raise SystemExit('Could not find host Observer PIN block')

# Remove the now-unreachable guest observer join function.
s, n = re.subn(
    r'async function joinObserver\(\)\{.*?\}\nasync function creatorRoom',
    'async function creatorRoom',
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit('Could not remove joinObserver function')

# Do not generate or display a PIN when a teacher opens their own room.
old = 'observerPin=String(Math.floor(1000+Math.random()*9000));room=String(code);hostRoomCode.textContent=room;hostObserverPin.textContent=observerPin;hostGameCode.textContent=room;'
new = 'room=String(code);hostRoomCode.textContent=room;hostGameCode.textContent=room;'
if old not in s:
    raise SystemExit('Could not find Observer PIN generation in openHost')
s = s.replace(old, new, 1)

# Remove event handlers tied to the deleted guest-observer controls.
for old in [
    'joinObserverBtn.addEventListener("click",joinObserver);',
    'observerPinInput.addEventListener("input",()=>observerPinInput.value=observerPinInput.value.replace(/\\D/g,""));',
    'observerPinInput.addEventListener("keydown",e=>{if(e.key==="Enter")joinObserver()});',
]:
    if old not in s:
        raise SystemExit('Could not find observer event handler: ' + old)
    s = s.replace(old, '', 1)

# Add a marker explaining that the host's built-in observer remains, but guest PIN access is removed.
marker_anchor = '/* OBSERVER_GUEST_V1 */'
if marker_anchor not in s:
    raise SystemExit('Could not find observer CSS anchor')
s = s.replace(marker_anchor, '/* OBSERVER_PIN_REMOVED_V1 — room creator is host + observer; no guest observer PIN UI */\n' + marker_anchor, 1)

# Safety checks: visible PIN/join controls and the guest join function must be gone.
for forbidden in [
    'id="observerPinInput"',
    'id="joinObserver"',
    'id="hostObserverPin"',
    'Observer PIN',
    'async function joinObserver()',
    'joinObserverBtn.addEventListener',
    'observerPinInput.addEventListener',
]:
    if forbidden in s:
        raise SystemExit('Observer PIN residue remains: ' + forbidden)

p.write_text(s, encoding='utf-8')
print('Removed guest Observer PIN access; host Live Observer remains.')
