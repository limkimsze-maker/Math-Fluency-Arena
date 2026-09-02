from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

MARKER = 'MAP_CHOOSER_12_V1'
if MARKER in s:
    raise SystemExit('12-map chooser is already installed')

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

# Keep the selected visual theme separate from the automatic size category.
replace_once('mathMode="add20",mapKey="compact",roundStart=', 'mathMode="add20",mapKey="compact",mapTheme="sakura",roundStart=', 'map theme state')

# Add responsive map-choice cards and miniature previews in the host lobby.
css = r'''
/* MAP_CHOOSER_12_V1 */
.mapChooserWrap{margin:14px 0;padding:12px;border:3px solid var(--ink);border-radius:16px;background:#f8fbff;text-align:left}.mapChooserHead{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:9px}.mapChooserHead b{font-size:18px}.mapSizeHint{font-size:13px;font-weight:900;color:#59677f}.mapChoices{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.mapChoice{margin:0;border:3px solid #c9d4e3;border-radius:14px;background:#fff;padding:7px;box-shadow:none;text-align:center;font-weight:900}.mapChoice.selected{border-color:var(--ink);box-shadow:0 3px 0 var(--ink);background:#fff8cf}.mapChoice:disabled{opacity:.65}.mapThumb{position:relative;width:100%;aspect-ratio:16/10;overflow:hidden;border:2px solid var(--ink);border-radius:10px;background:#294054;margin-bottom:6px}.mapThumbWorld{position:absolute;inset:0;transform-origin:0 0;overflow:hidden}.mapThumbWorld .miniPath,.mapThumbWorld .miniWall,.mapThumbWorld .miniBush,.mapThumbWorld .miniBase,.mapThumbWorld .miniDecor{position:absolute}.mapThumbWorld .miniPath{background:#dbc995;opacity:.9;border-radius:99px}.mapThumbWorld .miniWall{background:#734a37;border:1px solid #39291f;border-radius:2px}.mapThumbWorld .miniBush{width:4.5%;height:6%;border-radius:50%;background:#5ca34a}.mapThumbWorld .miniBase{top:12%;bottom:12%;width:7%;border:1px dashed #fff;border-radius:4px}.mapThumbWorld .miniBase.blue{left:1%;background:rgba(47,125,246,.55)}.mapThumbWorld .miniBase.red{right:1%;background:rgba(255,91,99,.55)}.mapThumbWorld.theme-sakura{background:linear-gradient(135deg,#a7df76,#8fd45e)}.mapThumbWorld.theme-singapore{background:linear-gradient(135deg,#8bd274,#5fc4b4)}.mapThumbWorld.theme-china{background:linear-gradient(135deg,#9bcf72,#d9c58c)}.mapThumbWorld.theme-singapore .miniPath{background:#d8d8cf}.mapThumbWorld.theme-singapore .miniWall{background:#73808b;border-color:#47515a}.mapThumbWorld.theme-china .miniPath{background:#c8b48b}.mapThumbWorld.theme-china .miniWall{background:#9b4d3b;border-color:#5b2c24}.mapThumbWorld .miniDecor{font-size:clamp(10px,1.4vw,18px);transform:translate(-50%,-50%)}
#world.theme-sakura,.observerWorld.theme-sakura{background:linear-gradient(135deg,#a7df76,var(--grass))}#world.theme-singapore,.observerWorld.theme-singapore{background:linear-gradient(135deg,#8bd274,#5fc4b4)}#world.theme-china,.observerWorld.theme-china{background:linear-gradient(135deg,#9bcf72,#d9c58c)}#world.theme-singapore .path,.observerWorld.theme-singapore .path{background:#d8d8cf}#world.theme-singapore .wall,.observerWorld.theme-singapore .wall{background:linear-gradient(180deg,#4e5b66 0 28%,#8f9ca5 28% 100%);border-color:#46515a}#world.theme-singapore .wall::before{background:#35434d;border-color:#26333c}#world.theme-china .path,.observerWorld.theme-china .path{background:#c8b48b}#world.theme-china .wall,.observerWorld.theme-china .wall{background:linear-gradient(180deg,#71352d 0 28%,#a95543 28% 100%);border-color:#5b2c24}#world.theme-china .wall::before{background:#4b2925;border-color:#321c19}.themeDecor{position:absolute;transform:translate(-50%,-50%);pointer-events:none;user-select:none;z-index:2;filter:drop-shadow(0 2px 1px rgba(23,32,51,.2));font-size:48px}.themeDecor.big{font-size:72px;opacity:.75}.themeDecor.faint{font-size:110px;opacity:.18;z-index:1}
@media(max-width:700px){.mapChoices{grid-template-columns:1fr}.mapThumb{aspect-ratio:18/7}}
'''
replace_once('@media(max-width:700px){#hud', css + '\n@media(max-width:700px){#hud', 'map chooser css')

# Insert three previewable theme choices just before the host Start button.
chooser_html = r'''
<div class="mapChooserWrap" id="mapChooserWrap">
  <div class="mapChooserHead"><b>Choose map design</b><span class="mapSizeHint" id="mapSizeHint">Compact · recommended for this class size</span></div>
  <div class="mapChoices" id="mapChoices">
    <button type="button" class="mapChoice selected" data-map-theme="sakura"><div class="mapThumb"><div class="mapThumbWorld" data-preview-theme="sakura"></div></div><span>Sakura Arena</span></button>
    <button type="button" class="mapChoice" data-map-theme="singapore"><div class="mapThumb"><div class="mapThumbWorld" data-preview-theme="singapore"></div></div><span>Singapore City Garden</span></button>
    <button type="button" class="mapChoice" data-map-theme="china"><div class="mapThumb"><div class="mapThumbWorld" data-preview-theme="china"></div></div><span>China Garden City</span></button>
  </div>
  <div class="small" style="margin-top:8px">Each design has its own paths and obstacles. No flags, official emblems, logos or copied characters are used.</div>
</div>
'''
regex_once(r'(<button[^>]+id="startRoundBtn"[^>]*>)', chooser_html + r'\1', 'host start button')

# Replace the four original layouts with 12 distinct layouts: 3 per automatic size category.
profiles = r'''const mapProfiles={
 compact:{name:"Sakura Compact",size:"compact",theme:"sakura",w:1300,h:820,paths:[[12,24,76,8],[12,68,76,8]],walls:[[23,11,4,27],[23,56,4,31],[73,11,4,31],[73,60,4,27],[37,29,22,4],[42,66,21,4],[48,40,4,16]],bushes:[[33,46],[65,48],[50,20]]},
 compact_sg:{name:"Singapore Compact",size:"compact",theme:"singapore",w:1300,h:820,paths:[[10,18,35,8],[55,18,35,8],[12,72,76,8],[45,24,10,48],[24,44,52,8]],walls:[[20,29,4,26],[20,62,17,4],[36,13,4,22],[36,49,4,25],[60,13,4,26],[60,55,4,22],[76,30,4,26],[63,63,17,4],[45,35,10,4]],bushes:[[29,22],[70,24],[31,69],[69,68],[50,55]]},
 compact_cn:{name:"China Compact",size:"compact",theme:"china",w:1300,h:820,paths:[[14,17,72,8],[14,75,72,8],[18,25,8,50],[74,25,8,50],[34,45,32,9]],walls:[[30,25,4,18],[30,57,4,18],[66,25,4,18],[66,57,4,18],[39,29,22,4],[39,67,22,4],[45,39,4,22],[56,39,4,22]],bushes:[[23,50],[77,50],[50,22],[50,78],[38,51],[62,51]]},
 standard:{name:"Sakura Standard",size:"standard",theme:"sakura",w:1700,h:1050,paths:[[11,20,78,8],[11,72,78,8]],walls:[[18,10,4,26],[18,54,4,34],[31,24,4,31],[31,70,4,18],[45,10,4,25],[45,50,4,38],[59,24,4,31],[59,70,4,18],[73,10,4,26],[73,54,4,34],[22,42,21,4],[57,42,21,4]],bushes:[[25,64],[38,18],[50,62],[64,18],[77,64]]},
 standard_sg:{name:"Singapore Standard",size:"standard",theme:"singapore",w:1700,h:1050,paths:[[10,16,80,7],[10,78,80,7],[18,35,64,7],[18,58,64,7],[46,22,8,50]],walls:[[16,26,4,24],[16,62,4,25],[27,10,4,19],[27,43,4,25],[27,76,4,14],[40,27,4,22],[40,59,4,28],[56,12,4,24],[56,48,4,22],[56,76,4,13],[70,27,4,22],[70,61,4,27],[82,11,4,27],[82,55,4,31],[34,39,12,4],[58,55,12,4]],bushes:[[22,18],[35,72],[48,45],[64,22],[77,73],[48,82]]},
 standard_cn:{name:"China Standard",size:"standard",theme:"china",w:1700,h:1050,paths:[[14,14,72,7],[14,79,72,7],[14,45,72,8],[24,22,7,57],[69,22,7,57]],walls:[[20,28,4,13],[20,57,4,13],[33,20,4,19],[33,50,4,23],[33,80,4,9],[47,10,4,22],[47,38,4,16],[47,63,4,25],[61,22,4,18],[61,48,4,22],[61,78,4,11],[76,28,4,13],[76,57,4,13],[38,34,20,4],[42,70,16,4]],bushes:[[20,20],[80,20],[20,80],[80,80],[50,28],[50,78]]},
 large:{name:"Sakura Large",size:"large",theme:"sakura",w:2100,h:1300,paths:[[10,18,80,8],[10,74,80,8],[17,46,66,8]],walls:[[16,9,4,26],[16,52,4,37],[27,22,4,30],[27,69,4,20],[38,9,4,26],[38,50,4,39],[49,22,4,26],[49,65,4,24],[60,9,4,26],[60,50,4,39],[71,22,4,30],[71,69,4,20],[82,9,4,26],[82,52,4,37],[20,41,16,4],[64,41,16,4],[42,58,16,4]],bushes:[[23,61],[34,17],[45,76],[55,17],[66,76],[77,61],[50,36]]},
 large_sg:{name:"Singapore Large",size:"large",theme:"singapore",w:2100,h:1300,paths:[[8,14,84,7],[8,82,84,7],[15,32,70,7],[15,64,70,7],[30,20,8,58],[63,20,8,58]],walls:[[14,22,4,25],[14,59,4,30],[24,9,4,19],[24,40,4,23],[24,74,4,15],[39,14,4,24],[39,50,4,17],[39,76,4,14],[51,24,4,22],[51,58,4,30],[66,10,4,23],[66,44,4,24],[66,78,4,12],[78,23,4,24],[78,59,4,29],[86,12,4,30],[86,56,4,33],[29,47,14,4],[57,38,13,4],[45,69,14,4]],bushes:[[19,16],[32,71],[46,24],[54,79],[69,28],[82,76],[50,49]]},
 large_cn:{name:"China Large",size:"large",theme:"china",w:2100,h:1300,paths:[[12,12,76,7],[12,84,76,7],[12,47,76,7],[21,22,7,58],[72,22,7,58],[37,24,7,56],[56,24,7,56]],walls:[[17,28,4,14],[17,58,4,15],[29,14,4,22],[29,45,4,18],[29,72,4,18],[41,10,4,20],[41,38,4,19],[41,66,4,24],[53,15,4,21],[53,46,4,18],[53,73,4,16],[65,10,4,25],[65,44,4,20],[65,73,4,17],[80,28,4,14],[80,58,4,15],[34,32,16,4],[50,61,16,4],[38,79,24,4]],bushes:[[18,18],[82,18],[18,82],[82,82],[49,19],[49,82],[25,49],[75,49]]},
 mega:{name:"Sakura Mega",size:"mega",theme:"sakura",w:2500,h:1550,paths:[[9,17,82,8],[9,76,82,8],[15,46,70,8]],walls:[[14,8,4,28],[14,53,4,38],[24,21,4,31],[24,70,4,21],[34,8,4,28],[34,51,4,40],[44,21,4,27],[44,65,4,26],[54,8,4,28],[54,51,4,40],[64,21,4,27],[64,65,4,26],[74,8,4,28],[74,51,4,40],[84,21,4,31],[84,70,4,21],[18,41,14,4],[38,58,17,4],[68,41,14,4],[58,74,14,4]],bushes:[[20,61],[30,15],[40,78],[50,34],[60,15],[70,78],[80,61],[50,72],[30,50],[70,50]]},
 mega_sg:{name:"Singapore Mega",size:"mega",theme:"singapore",w:2500,h:1550,paths:[[7,12,86,7],[7,86,86,7],[12,28,76,7],[12,52,76,7],[12,70,76,7],[25,18,7,63],[48,18,7,63],[71,18,7,63]],walls:[[12,19,4,19],[12,45,4,19],[12,75,4,18],[21,8,4,17],[21,34,4,20],[21,62,4,22],[34,17,4,22],[34,48,4,19],[34,75,4,17],[44,8,4,23],[44,39,4,22],[44,69,4,24],[57,17,4,22],[57,48,4,19],[57,75,4,17],[67,8,4,23],[67,39,4,22],[67,69,4,24],[80,17,4,22],[80,48,4,19],[80,75,4,17],[88,10,4,26],[88,47,4,20],[88,76,4,16],[26,41,13,4],[61,58,13,4],[39,78,18,4]],bushes:[[17,14],[28,66],[39,24],[50,62],[61,22],[72,68],[83,17],[50,86],[26,84],[76,85]]},
 mega_cn:{name:"China Mega",size:"mega",theme:"china",w:2500,h:1550,paths:[[10,10,80,7],[10,88,80,7],[10,48,80,8],[18,20,7,62],[34,20,7,62],[50,20,7,62],[66,20,7,62],[82,20,7,62]],walls:[[14,26,4,15],[14,59,4,16],[26,11,4,20],[26,40,4,18],[26,67,4,24],[38,19,4,20],[38,48,4,19],[38,77,4,14],[47,9,4,22],[47,39,4,18],[47,66,4,25],[56,18,4,22],[56,49,4,18],[56,77,4,14],[68,10,4,24],[68,43,4,18],[68,70,4,21],[80,25,4,16],[80,59,4,16],[31,31,16,4],[53,31,16,4],[31,72,16,4],[53,72,16,4],[42,57,16,4]],bushes:[[15,16],[85,16],[15,84],[85,84],[25,51],[75,51],[50,17],[50,85],[41,43],[59,61]]}
};
const mapThemeLabels={sakura:"Sakura Arena",singapore:"Singapore City Garden",china:"China Garden City"};
const mapSizeLabels={compact:"Compact",standard:"Standard",large:"Large",mega:"Mega"};
function sizeForCount(n){return n<=8?"compact":n<=16?"standard":n<=24?"large":"mega"}
function mapKeyForSize(size,theme=mapTheme){if(theme==="singapore")return size+"_sg";if(theme==="china")return size+"_cn";return size}
function chooseMapForCount(n){return mapKeyForSize(sizeForCount(n),mapTheme)}'''
regex_once(r'const mapProfiles=\{.*?\n\};\nfunction chooseMapForCount\(n\)\{.*?\}', profiles, 'map profiles')

# Generalised decor and rendering. These are game arenas inspired by place aesthetics, not literal maps.
rendering = r'''function themeDecorHTML(theme){
  if(theme==="singapore")return '<div class="themeDecor faint" style="left:50%;top:14%">🏙️</div><div class="themeDecor big" style="left:16%;top:20%">🌴</div><div class="themeDecor" style="left:84%;top:24%">🌴</div><div class="themeDecor big" style="left:50%;top:84%">🌉</div><div class="themeDecor" style="left:28%;top:84%">🌺</div><div class="themeDecor" style="left:72%;top:78%">🌺</div>';
  if(theme==="china")return '<div class="themeDecor faint" style="left:50%;top:14%">🏯</div><div class="themeDecor big" style="left:15%;top:22%">🎋</div><div class="themeDecor big" style="left:85%;top:78%">🎋</div><div class="themeDecor" style="left:50%;top:82%">🏮</div><div class="themeDecor" style="left:28%;top:18%">🪨</div><div class="themeDecor" style="left:72%;top:20%">🏮</div>';
  return '<div class="jpDecor fuji" style="left:50%;top:9%">🗻</div><div class="jpDecor shrine" style="left:50%;top:20%">🏯</div><div class="jpDecor torii" style="left:10%;top:48%">⛩️</div><div class="jpDecor torii" style="left:90%;top:48%">⛩️</div><div class="jpDecor lantern" style="left:19%;top:39%">🏮</div><div class="jpDecor lantern" style="left:81%;top:61%">🏮</div><div class="jpDecor sakura" style="left:28%;top:16%">🌸</div><div class="jpDecor sakura" style="left:72%;top:84%">🌸</div>';
}
function renderMap(key){
  const p=mapProfiles[key]||mapProfiles.compact;if(world.dataset.mapKey===key)return;world.dataset.mapKey=key;world.dataset.theme=p.theme||"sakura";world.classList.remove("theme-sakura","theme-singapore","theme-china");world.classList.add("theme-"+(p.theme||"sakura"));world.style.width=p.w+"px";world.style.height=p.h+"px";world.querySelectorAll(".path,.base,.wall,.bush,.jpDecor,.themeDecor").forEach(el=>el.remove());let html=themeDecorHTML(p.theme||"sakura")+'<div class="base blue">BLUE BASE</div><div class="base red">RED BASE</div>';p.paths.forEach(a=>html+='<div class="path" style="'+mapStyle(a)+'"></div>');p.walls.forEach(a=>html+='<div class="wall" style="'+mapStyle(a)+'"></div>');p.bushes.forEach(a=>html+='<div class="bush" style="left:'+a[0]+'%;top:'+a[1]+'%"></div>');world.insertAdjacentHTML("afterbegin",html)
}
function setMap(key){
  mapKey=mapProfiles[key]?key:"compact";const p=mapProfiles[mapKey];mapTheme=p.theme||"sakura";renderMap(mapKey);if(hostMapLabel)hostMapLabel.textContent=p.name;if(mapLabel)mapLabel.textContent=p.name+" map";renderMapChooser()
}
function miniDecor(theme){if(theme==="singapore")return [[50,16,"🏙️"],[18,22,"🌴"],[82,75,"🌴"],[50,82,"🌉"]];if(theme==="china")return [[50,16,"🏯"],[18,23,"🎋"],[82,76,"🎋"],[50,82,"🏮"]];return [[50,14,"🗻"],[15,48,"⛩️"],[85,48,"⛩️"],[50,82,"🌸"]]}
function renderMiniMap(el,p){
  if(!el||!p)return;el.className="mapThumbWorld theme-"+(p.theme||"sakura");let html='<div class="miniBase blue"></div><div class="miniBase red"></div>';p.paths.forEach(a=>html+='<div class="miniPath" style="left:'+a[0]+'%;top:'+a[1]+'%;width:'+a[2]+'%;height:'+a[3]+'%"></div>');p.walls.forEach(a=>html+='<div class="miniWall" style="left:'+a[0]+'%;top:'+a[1]+'%;width:'+a[2]+'%;height:'+a[3]+'%"></div>');p.bushes.slice(0,7).forEach(a=>html+='<div class="miniBush" style="left:'+a[0]+'%;top:'+a[1]+'%"></div>');miniDecor(p.theme||"sakura").forEach(d=>html+='<div class="miniDecor" style="left:'+d[0]+'%;top:'+d[1]+'%">'+d[2]+'</div>');el.innerHTML=html
}
function renderMapChooser(){
  const wrap=document.getElementById("mapChooserWrap"),choices=document.getElementById("mapChoices"),hint=document.getElementById("mapSizeHint");if(!wrap||!choices)return;const p=mapProfiles[mapKey]||mapProfiles.compact,size=p.size||"compact";if(hint)hint.textContent=(mapSizeLabels[size]||size)+" · recommended for this class size";choices.querySelectorAll(".mapChoice").forEach(btn=>{const theme=btn.dataset.mapTheme||"sakura",key=mapKeyForSize(size,theme),profile=mapProfiles[key];btn.classList.toggle("selected",theme===mapTheme);btn.disabled=!!roundActive;renderMiniMap(btn.querySelector(".mapThumbWorld"),profile)})
}'''
regex_once(r'function renderMap\(key\)\{.*?\nfunction setMap\(key\)\{.*?\}', rendering, 'map renderer')

# Make the observer view use the same chosen theme/decor and geometry.
observer_renderer = r'''function renderObserverMap(){if(!observerWorld)return;const p=mapProfiles[mapKey]||mapProfiles.compact;if(observerWorld.dataset.mapKey===mapKey)return;observerWorld.dataset.mapKey=mapKey;observerWorld.classList.remove("theme-sakura","theme-singapore","theme-china");observerWorld.classList.add("theme-"+(p.theme||"sakura"));observerWorld.style.width=p.w+"px";observerWorld.style.height=p.h+"px";const paths=p.paths.map(a=>'<div class="path" style="'+mapStyle(a)+'"></div>').join("");const walls=p.walls.map(a=>'<div class="wall" style="'+mapStyle(a)+'"></div>').join("");const bushes=p.bushes.map(a=>'<div class="bush" style="left:'+a[0]+'%;top:'+a[1]+'%"></div>').join("");observerWorld.innerHTML=themeDecorHTML(p.theme||"sakura")+paths+'<div class="base blue">BLUE BASE</div><div class="base red">RED BASE</div>'+walls+bushes}'''
regex_once(r'function renderObserverMap\(\)\{.*?\nfunction refreshObserverSelect', observer_renderer + '\nfunction refreshObserverSelect', 'observer map renderer')

# Theme buttons switch only the visual/layout choice inside the current automatic size category.
listener = r'''
const mapChoicesEl=document.getElementById("mapChoices");if(mapChoicesEl)mapChoicesEl.addEventListener("click",e=>{const btn=e.target.closest(".mapChoice");if(!btn||roundActive)return;const theme=btn.dataset.mapTheme;if(!mapThemeLabels[theme])return;const current=mapProfiles[mapKey]||mapProfiles.compact;mapTheme=theme;setMap(mapKeyForSize(current.size||"compact",mapTheme));renderHostRoster()});
'''
replace_once('tryBotBtn.addEventListener("click",startBotDemo);', listener + 'tryBotBtn.addEventListener("click",startBotDemo);', 'map chooser listener')

# Ensure the host preview is always refreshed as pupil count changes.
replace_once('hostMapPreview.textContent=mapProfiles[mapKey].name+" · "+list.length+" player"+(list.length===1?"":"s");', 'hostMapPreview.textContent=mapProfiles[mapKey].name+" · "+list.length+" player"+(list.length===1?"":"s");renderMapChooser();', 'host preview refresh')

p.write_text(s, encoding='utf-8')
print('Installed 12 distinct maps with Singapore/China themes and previews')
