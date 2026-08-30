from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Mobile-safe viewport, including iPhone/iPad safe areas.
s = s.replace(
    '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">',
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
    1,
)

sentinel = '/* DEVICE_COMPAT_V1 */'
css = r'''
/* DEVICE_COMPAT_V1 */
html,body{width:100%;max-width:100%;overflow-x:hidden;-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{min-height:100vh;min-height:100dvh}
.screen{min-height:100vh;min-height:100dvh;padding:max(8px,env(safe-area-inset-top)) max(8px,env(safe-area-inset-right)) max(8px,env(safe-area-inset-bottom)) max(8px,env(safe-area-inset-left))}
.card{max-width:calc(100vw - max(16px,env(safe-area-inset-left)) - max(16px,env(safe-area-inset-right)));overflow-wrap:anywhere}
button,input,select{max-width:100%}button,#controls{-webkit-user-select:none;user-select:none}

/* The play screen uses the available visual viewport instead of assuming one fixed device height. */
#game.active{display:flex;flex-direction:column;height:100vh;height:100dvh;min-height:0;overflow:hidden;padding:max(4px,env(safe-area-inset-top)) max(4px,env(safe-area-inset-right)) max(4px,env(safe-area-inset-bottom)) max(4px,env(safe-area-inset-left))}
#game #hud{flex:0 0 auto;width:min(1120px,100%);max-width:100%;margin:0 auto 5px}
#game #arena{flex:1 1 auto;width:min(1120px,100%);max-width:100%;height:auto;min-height:240px;max-height:630px;margin:0 auto}
#game #controls{flex:0 0 auto}
#game #boostBtn,#game .note{flex:0 0 auto}

/* Lobby/teacher screens remain scrollable even on short displays. */
#lobby.active,#hostLobby.active,#hostGame.active,#nameScreen.active{overflow-y:auto;-webkit-overflow-scrolling:touch}
.observerArena{height:min(480px,56vh);height:min(480px,56dvh)}

@media(max-width:700px){
  .screen{padding:max(6px,env(safe-area-inset-top)) max(6px,env(safe-area-inset-right)) max(6px,env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left))}
  .card{width:100%;margin:8px auto;padding:14px;border-width:3px;border-radius:18px}
  h1{font-size:clamp(28px,9vw,42px)}h2{font-size:20px}
  .room{font-size:28px;letter-spacing:4px}.btn{min-height:50px;font-size:18px}.modeSelect{font-size:16px}
  #hostGame .card{width:100%;max-width:100%}.observerPanel{padding:8px;margin:10px 0}.observerToolbar{display:grid;grid-template-columns:1fr;gap:6px;text-align:left}.observerToolbar select{width:100%;min-width:0}.observerArena{height:min(420px,52vh);height:min(420px,52dvh);min-height:220px}.observerLabel{font-size:10px;max-width:90%}
  #hud{grid-template-columns:minmax(0,1fr) 94px minmax(0,1fr);gap:3px}.score{padding:5px 6px;border-width:2px;border-radius:10px;font-size:clamp(13px,4vw,18px)}.middle{font-size:11px}.timer{font-size:24px}#modeLabel,#mapLabel{font-size:9px}#status{font-size:9px}
  #arena{border-width:3px;border-radius:15px;min-height:220px;box-shadow:none}
  #personal{left:5px;top:5px;padding:4px 6px;border-width:2px;font-size:10px}#hint{right:5px;top:5px;max-width:45vw;padding:4px 6px;border-width:2px;font-size:10px}#toast{max-width:80vw;text-align:center;font-size:12px}
  #controls{width:196px;margin:5px auto 0;grid-template-columns:60px 60px 60px;grid-template-rows:50px 50px;gap:5px}#controls button{border-width:2px;border-radius:11px;font-size:23px;box-shadow:0 2px 0 var(--ink)}
  #boostBtn{width:min(360px,94vw);min-height:44px;margin:5px auto 0;font-size:15px;box-shadow:0 2px 0 var(--ink)}.note{font-size:10px;line-height:1.15;margin-top:3px}
  .overlay{padding:7px}.box{width:min(500px,98%);padding:14px;border-width:3px;border-radius:16px}#qText{font-size:clamp(34px,12vw,54px);margin:4px 0 10px}.ans{min-height:58px;border-width:3px;font-size:clamp(22px,8vw,32px)}
}

@media(max-width:380px){
  #hud{grid-template-columns:minmax(0,1fr) 76px minmax(0,1fr)}.middle>div:first-child{display:none}.timer{font-size:22px}.score{font-size:12px;padding:4px}.room{font-size:24px}.note{display:none}
  #controls{width:176px;grid-template-columns:54px 54px 54px;grid-template-rows:46px 46px}
}

/* Short landscape phones: use the map for nearly the whole screen and float touch controls over a corner. */
@media(orientation:landscape) and (max-height:560px) and (pointer:coarse){
  #game.active{padding:max(2px,env(safe-area-inset-top)) max(3px,env(safe-area-inset-right)) max(2px,env(safe-area-inset-bottom)) max(3px,env(safe-area-inset-left))}
  #hud{margin-bottom:2px;grid-template-columns:1fr 90px 1fr}.middle>div:first-child,#modeLabel,#mapLabel,#status{display:none}.timer{font-size:20px}.score{font-size:14px;padding:3px 6px}
  #arena{min-height:0;max-height:none;height:auto;border-width:3px}
  #controls{position:fixed;right:max(8px,env(safe-area-inset-right));bottom:max(8px,env(safe-area-inset-bottom));z-index:95;width:174px;margin:0;grid-template-columns:52px 52px 52px;grid-template-rows:44px 44px;opacity:.92}#controls button{background:rgba(255,255,255,.94)}
  #boostBtn{position:fixed;left:max(8px,env(safe-area-inset-left));bottom:max(8px,env(safe-area-inset-bottom));z-index:96;width:170px;min-height:42px;margin:0;font-size:13px}.note{display:none}
  #personal{font-size:9px}#hint{font-size:9px;max-width:36vw}
}

/* Very short laptop/Chromebook windows still keep the arena and controls visible. */
@media(min-width:701px) and (max-height:700px){
  #game #arena{min-height:260px;max-height:none}.middle>div:first-child{font-size:12px}.timer{font-size:28px}
  #controls{grid-template-columns:58px 58px 58px;grid-template-rows:48px 48px;width:190px;margin-top:4px}#controls button{font-size:22px}.note{font-size:10px;margin-top:2px}
}

@media(prefers-reduced-motion:reduce){.star,.player.immune .ninja,#boostBtn.ready{animation:none!important}.player{transition:none}}
'''

if sentinel not in s:
    if '</style>' not in s:
        raise SystemExit('style closing tag not found')
    s = s.replace('</style>', css + '\n</style>', 1)

# Recenter whichever camera is active when a browser resizes or a phone rotates.
old = 'window.addEventListener("resize",()=>{if(teamAssigned)updateCamera()})'
new = 'window.addEventListener("resize",()=>{if(teamAssigned)updateCamera();if(isHost)updateObserver()});window.addEventListener("orientationchange",()=>setTimeout(()=>{if(teamAssigned)updateCamera();if(isHost)updateObserver()},120))'
if old in s:
    s = s.replace(old, new, 1)

# Avoid a duplicate observer-only resize handler if present.
s = s.replace('\nwindow.addEventListener("resize",()=>{if(isHost)updateObserver()});', '', 1)

p.write_text(s, encoding='utf-8')
