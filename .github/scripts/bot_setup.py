from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

MARKER = 'BOT_SETUP_OPTIONS_V1'
if MARKER in s:
    raise SystemExit('Bot setup options are already installed')
if 'MAP_CHOOSER_12_V1' not in s:
    raise SystemExit('12-map chooser must be installed first')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'{label} marker not found')
    s = s.replace(old, new, 1)

def regex_once(pattern, replacement, label):
    global s
    s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label} marker not found or ambiguous: {n}')
    s = s2

css = r'''
/* BOT_SETUP_OPTIONS_V1 */
#botSetup .card{width:min(820px,96vw)}.botSetupGrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;text-align:left}.botSetupGrid label{display:block;font-weight:900;margin-bottom:5px}.botSetupGrid .modeSelect{margin:0}.botMapNote{margin:8px 0 2px;padding:8px 10px;border:2px dashed #b9c5d5;border-radius:10px;background:#f8fbff}.botActions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}.botActions .btn{margin:0}.botMapChoices{margin-top:10px}
@media(max-width:700px){.botSetupGrid,.botActions{grid-template-columns:1fr}}
'''
replace_once('</style>', css + '\n</style>', 'style end')

math_options = '''<option value="add20">Addition within 20</option><option value="sub20">Subtraction within 20</option><option value="mul5">Multiplication: ×2 to ×5 tables</option><option value="div5">Division: ÷2 to ÷5 tables</option><option value="mul610">Multiplication: ×6 to ×10 tables</option><option value="div610">Division: ÷6 to ÷10 tables</option><option value="mul10">Multiplication: ×2 to ×10 tables</option><option value="div10">Division: ÷2 to ÷10 tables</option><option value="mul12">Multiplication: ×2 to ×12 tables</option><option value="div12">Division: ÷2 to ÷12 tables</option><option value="mixed">Mixed: + − × ÷</option>'''

bot_setup_html = f'''
<section id="botSetup" class="screen"><div class="card"><h1>🤖 3v3 Bot Challenge</h1><p class="small">You + 2 Blue Bots vs 3 Red Bots. Choose what to practise and which arena to play before the round starts.</p>
<div class="botSetupGrid"><div><label for="botMathModeSelect">What do you want to learn?</label><select id="botMathModeSelect" class="modeSelect">{math_options}</select></div><div><label for="botMapSizeSelect">Map size</label><select id="botMapSizeSelect" class="modeSelect"><option value="compact">Compact · recommended for 3v3</option><option value="standard">Standard</option><option value="large">Large</option><option value="mega">Mega</option></select></div></div>
<div class="mapChooserWrap botMapChoices"><div class="mapChooserHead"><b>Choose map design</b><span class="mapSizeHint" id="botMapSizeHint">Compact · recommended for 3v3</span></div><div class="mapChoices" id="botMapChoices">
<button type="button" class="mapChoice selected" data-bot-map-theme="sakura"><div class="mapThumb"><div class="mapThumbWorld"></div></div><span>Sakura Arena</span></button>
<button type="button" class="mapChoice" data-bot-map-theme="singapore"><div class="mapThumb"><div class="mapThumbWorld"></div></div><span>Singapore City Garden</span></button>
<button type="button" class="mapChoice" data-bot-map-theme="china"><div class="mapThumb"><div class="mapThumbWorld"></div></div><span>China Garden City</span></button>
</div><div class="botMapNote small">The preview changes with map size. Every design has different paths and obstacles. No flags, official emblems, logos or copied characters are used.</div></div>
<div class="botActions"><button id="botStart" class="btn primary" type="button">Start 3v3 Bot Challenge</button><button id="botBack" class="btn" type="button">Back to Home</button></div></div></section>
'''
regex_once(r'(<section id="hostLobby" class="screen">)', bot_setup_html + r'\1', 'host lobby section')

replace_once('screens=[$("lobby"),$("hostLobby"),$("hostGame"),$("nameScreen"),$("game")],', 'screens=[$("lobby"),$("botSetup"),$("hostLobby"),$("hostGame"),$("nameScreen"),$("game")],', 'screens array')
replace_once('tryBotBtn=$("tryBot"),joinBtn=$("join"),', 'tryBotBtn=$("tryBot"),botSetup=$("botSetup"),botMathModeSelect=$("botMathModeSelect"),botMapSizeSelect=$("botMapSizeSelect"),botMapChoices=$("botMapChoices"),botMapSizeHint=$("botMapSizeHint"),botStart=$("botStart"),botBack=$("botBack"),joinBtn=$("join"),', 'bot element bindings')
replace_once('demoMode=false,demoBot=null,demoBots=[],botSolveAt=', 'demoMode=false,demoBot=null,demoBots=[],botSetupTheme="sakura",botSetupSize="compact",botSolveAt=', 'bot setup state')

bot_functions = r'''
function renderBotMapChooser(){
  if(!botMapChoices)return;const size=mapSizeLabels[botSetupSize]?botSetupSize:"compact";if(botMapSizeHint)botMapSizeHint.textContent=(mapSizeLabels[size]||size)+(size==="compact"?" · recommended for 3v3":" · larger arena for extra roaming");botMapChoices.querySelectorAll(".mapChoice").forEach(btn=>{const theme=btn.dataset.botMapTheme||"sakura",profile=mapProfiles[mapKeyForSize(size,theme)];btn.classList.toggle("selected",theme===botSetupTheme);renderMiniMap(btn.querySelector(".mapThumbWorld"),profile)})
}
function openBotSetup(){
  stop();if(socket){try{socket.close()}catch(e){}socket=null}demoMode=false;teamAssigned=false;team=null;botSetupSize="compact";botSetupTheme="sakura";if(botMathModeSelect)botMathModeSelect.value="add20";if(botMapSizeSelect)botMapSizeSelect.value=botSetupSize;renderBotMapChooser();show(botSetup)
}
'''
replace_once('function spawnPlayer(){', bot_functions + '\nfunction spawnPlayer(){', 'spawn player function')

old_demo = '''  setMap("compact");setMathMode("add20");show($("game"));
  const s=Date.now()+2200,e=s+ROUND;beginRound(s,e,"add20","compact");initDemoBots();
  waitTitle.textContent="3v3 Bot Challenge";waitText.textContent="You + 2 Blue Bots vs 3 Red Bots. Solve, grab stars from Red Bots, and bank more stars to win."'''
new_demo = '''  const demoMath=botMathModeSelect&&modeNames[botMathModeSelect.value]?botMathModeSelect.value:"add20",demoMap=mapKeyForSize(botSetupSize,botSetupTheme);setMap(demoMap);setMathMode(demoMath);show($("game"));
  const s=Date.now()+2200,e=s+ROUND;beginRound(s,e,demoMath,demoMap);initDemoBots();
  waitTitle.textContent="3v3 Bot Challenge";waitText.textContent="You + 2 Blue Bots vs 3 Red Bots. "+modeNames[demoMath]+" · "+(mapProfiles[demoMap]||mapProfiles.compact).name+". Solve, grab stars from Red Bots, and bank more stars to win."'''
replace_once(old_demo, new_demo, 'bot demo hardcoded map and math')

replace_once('function leaveBotDemo(){\n  stop();roundActive=false;finished=true;demoMode=false;demoBot=null;demoBots=[];teamAssigned=false;team=null;players.clear();clearDemoActors();star.style.display="none";results.classList.remove("open");waiting.classList.remove("open");show($("lobby"));msg.textContent=""\n}', 'function leaveBotDemo(){\n  stop();roundActive=false;finished=true;demoMode=false;demoBot=null;demoBots=[];teamAssigned=false;team=null;players.clear();clearDemoActors();star.style.display="none";results.classList.remove("open");waiting.classList.remove("open");mapTheme="sakura";setMap("compact");show($("lobby"));msg.textContent=""\n}', 'leave bot demo reset')

old_bind = 'tryBotBtn.addEventListener("click",startBotDemo);joinBtn.addEventListener("click",joinRoom);'
new_bind = '''tryBotBtn.addEventListener("click",openBotSetup);if(botMapSizeSelect)botMapSizeSelect.addEventListener("change",()=>{botSetupSize=mapSizeLabels[botMapSizeSelect.value]?botMapSizeSelect.value:"compact";renderBotMapChooser()});if(botMapChoices)botMapChoices.addEventListener("click",e=>{const btn=e.target.closest(".mapChoice");if(!btn)return;const theme=btn.dataset.botMapTheme;if(!mapThemeLabels[theme])return;botSetupTheme=theme;renderBotMapChooser()});if(botStart)botStart.addEventListener("click",startBotDemo);if(botBack)botBack.addEventListener("click",()=>show($("lobby")));joinBtn.addEventListener("click",joinRoom);'''
replace_once(old_bind, new_bind, 'try bot binding')

p.write_text(s, encoding='utf-8')
print('Installed bot learning + map setup options')
