from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'OBSERVER_LIVE_QUESTION_V1' in s:
    raise SystemExit('Live observer question patch already applied')

# Lightweight teacher question panel styling.
css_anchor = '/* HOST_SAFETY_V1 */'
css = '''/* OBSERVER_LIVE_QUESTION_V1 — teacher can follow a selected pupil's live question */
.observerQuestion{margin:0 0 9px;padding:9px 11px;border:2px dashed #b9c5d5;border-radius:12px;background:#f8fbff;text-align:left;min-height:52px;font-weight:800}.observerQuestion.active{border-style:solid;border-color:#7a8799;background:#fff}.oqTitle{font-size:12px;color:#66758d;font-weight:900;margin-bottom:3px}.oqQuestion{font-size:clamp(24px,4vw,34px);font-weight:900;line-height:1.15}.oqChoices{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}.oqChoice{display:inline-block;min-width:42px;padding:4px 8px;border:2px solid #c9d4e3;border-radius:9px;background:#fff;text-align:center;font-weight:900}.oqChoice.chosen.correct{background:#dff5d8;border-color:#3f8b3a}.oqChoice.chosen.wrong{background:#ffe0e2;border-color:#b83e47}.oqResult{margin-top:5px;font-size:13px;font-weight:900}.oqResult.correct{color:#237a3b}.oqResult.wrong{color:#9b2630}
'''
if css_anchor not in s:
    raise SystemExit('CSS anchor not found')
s = s.replace(css_anchor, css + css_anchor, 1)

# Add live question panel above observer arena.
html_old = '<div class="observerToolbar"><b>👁️ Live Observer</b><select id="observerSelect" aria-label="Observer view"><option value="overview">Whole Game</option></select></div><div id="observerArena" class="observerArena">'
html_new = '<div class="observerToolbar"><b>👁️ Live Observer</b><select id="observerSelect" aria-label="Observer view"><option value="overview">Whole Game</option></select></div><div id="observerQuestion" class="observerQuestion" aria-live="polite">Select a player to see their current question.</div><div id="observerArena" class="observerArena">'
if html_old not in s:
    raise SystemExit('Observer toolbar HTML anchor not found')
s = s.replace(html_old, html_new, 1)

# Wire DOM reference.
old = 'observerSelect=$("observerSelect"),observerArena=$("observerArena"),observerWorld=$("observerWorld"),observerLabel=$("observerLabel"),hostRoundRanking=$("hostRoundRanking"),'
new = 'observerSelect=$("observerSelect"),observerArena=$("observerArena"),observerWorld=$("observerWorld"),observerLabel=$("observerLabel"),observerQuestion=$("observerQuestion"),hostRoundRanking=$("hostRoundRanking"),'
if old not in s:
    raise SystemExit('Observer DOM declaration anchor not found')
s = s.replace(old, new, 1)

# Local current-question state (never contains the correct answer).
old = 'qOpen=false,qLock=false,questionMode="star",stealTargetId=null,stealTargetName="",mathMode="add20"'
new = 'qOpen=false,qLock=false,questionMode="star",liveQuestion=null,stealTargetId=null,stealTargetName="",mathMode="add20"'
if old not in s:
    raise SystemExit('Question state declaration anchor not found')
s = s.replace(old, new, 1)

# Host receives only question text/options/selected result, never the correct answer.
old = ' if((d.type==="playerState"||d.type==="move")&&d.id!==playerId){upsert(d);if(isHost)renderHostRoster();return}\n if(d.type==="playerLeft")'
new = ' if((d.type==="playerState"||d.type==="move")&&d.id!==playerId){upsert(d);if(isHost)renderHostRoster();return}\n if(d.type==="questionState"&&isHost&&d.id!==playerId){applyQuestionState(d);return}\n if(d.type==="playerLeft")'
if old not in s:
    raise SystemExit('Message handler anchor not found')
s = s.replace(old, new, 1)

# Store the live/last question only in the host's in-memory player record.
upsert_anchor = 'function upsert(d){if(!d.team)return;'
question_handler = '''function applyQuestionState(d){
  const p=players.get(d.id);if(!p)return;
  if(d.open){
    p.question={open:true,mode:d.mode==="steal"?"steal":"star",text:String(d.text||"").slice(0,40),options:Array.isArray(d.options)?d.options.slice(0,4).map(v=>String(v).slice(0,8)):[],selected:d.selected==null?null:String(d.selected).slice(0,8),result:d.result==="correct"?"correct":d.result==="wrong"?"wrong":"",targetName:safe(d.targetName||""),updatedAt:Date.now()}
  }else if(p.question){
    p.question={...p.question,open:false,closedAt:Date.now()}
  }
  updateObserver()
}
'''
if upsert_anchor not in s:
    raise SystemExit('upsert anchor not found')
s = s.replace(upsert_anchor, question_handler + upsert_anchor, 1)

# Add a teacher-only renderer for selected player question details.
observer_anchor = 'function updateObserver(){if((!isHost&&!isObserver)||!observerArena||!observerWorld)return;'
renderer = '''function renderObserverQuestion(target){
  if(!observerQuestion)return;
  observerQuestion.innerHTML="";observerQuestion.classList.remove("active");
  if(!target){observerQuestion.textContent="Select a player to see their current question.";return}
  const q=target.question,showLast=q&&!q.open&&Date.now()-(q.closedAt||0)<3000;
  if(!q||(!q.open&&!showLast)){observerQuestion.textContent=target.name+" · No question open — currently moving/chasing/banking.";return}
  observerQuestion.classList.add("active");
  const title=document.createElement("div");title.className="oqTitle";title.textContent=(q.open?"LIVE · ":"LAST · ")+(q.mode==="steal"?"⚡ GRAB QUESTION":"⭐ STAR QUESTION")+" · "+target.name;observerQuestion.appendChild(title);
  const qt=document.createElement("div");qt.className="oqQuestion";qt.textContent=q.text||"Question";observerQuestion.appendChild(qt);
  const choices=document.createElement("div");choices.className="oqChoices";(q.options||[]).forEach(v=>{const c=document.createElement("span");c.className="oqChoice";c.textContent=v;if(q.selected!=null&&String(q.selected)===String(v)){c.classList.add("chosen",q.result||"")}choices.appendChild(c)});observerQuestion.appendChild(choices);
  if(q.selected!=null){const r=document.createElement("div");r.className="oqResult "+(q.result||"");r.textContent=(q.result==="correct"?"✅ Correct: ":q.result==="wrong"?"❌ Incorrect: ":"Answered: ")+q.selected;observerQuestion.appendChild(r)}
}
'''
if observer_anchor not in s:
    raise SystemExit('updateObserver anchor not found')
s = s.replace(observer_anchor, renderer + observer_anchor, 1)

# Render the question panel whenever observer view updates.
old = 'const target=observerTarget==="overview"?null:players.get(observerTarget);if(target&&now-(target.lastSeen||0)<20000){'
new = 'const target=observerTarget==="overview"?null:players.get(observerTarget);renderObserverQuestion(target&&now-(target.lastSeen||0)<20000?target:null);if(target&&now-(target.lastSeen||0)<20000){'
if old not in s:
    raise SystemExit('Observer target anchor not found')
s = s.replace(old, new, 1)

# Put a calculator marker beside pupils who are currently answering.
old = 'sig=list.map(p=>p.id+":"+p.name+":"+p.team).join("|");if(observerSelect.dataset.sig!==sig){observerSelect.dataset.sig=sig;observerSelect.innerHTML=\'<option value="overview">Whole Game</option>\'+list.map(p=>\'<option value="\'+p.id+\'">\'+(p.team==="red"?\'🔴 \':\'🔵 \')+safe(p.name)+\'</option>\').join("")}'
new = 'sig=list.map(p=>p.id+":"+p.name+":"+p.team+":"+(p.question&&p.question.open?1:0)).join("|");if(observerSelect.dataset.sig!==sig){observerSelect.dataset.sig=sig;observerSelect.innerHTML=\'<option value="overview">Whole Game</option>\'+list.map(p=>\'<option value="\'+p.id+\'">\'+(p.question&&p.question.open?\'🧮 \':\'\')+(p.team==="red"?\'🔴 \':\'🔵 \')+safe(p.name)+\'</option>\').join("")}'
if old not in s:
    raise SystemExit('Observer select signature anchor not found')
s = s.replace(old, new, 1)

# Broadcast question state without the answer key.
open_anchor = 'function openQuestion(mode="star",targetId=null,targetName=""){'
helper = '''function sendQuestionState(open){
  if(demoMode||!teamAssigned)return;
  if(open&&liveQuestion)send({type:"questionState",id:playerId,open:true,mode:liveQuestion.mode,text:liveQuestion.text,options:liveQuestion.options,selected:liveQuestion.selected,result:liveQuestion.result,targetName:liveQuestion.targetName,ts:Date.now()});
  else send({type:"questionState",id:playerId,open:false,ts:Date.now()})
}
'''
if open_anchor not in s:
    raise SystemExit('openQuestion anchor not found')
s = s.replace(open_anchor, helper + open_anchor, 1)

# Set and send question when it opens.
old = 'const q=makeQ();qText.textContent=q.text;answers.innerHTML="";'
new = 'const q=makeQ();liveQuestion={mode,text:q.text,options:q.options.map(String),selected:null,result:"",targetName:stealTargetName};sendQuestionState(true);qText.textContent=q.text;answers.innerHTML="";'
if old not in s:
    raise SystemExit('Question creation anchor not found')
s = s.replace(old, new, 1)

# Send the chosen option and correctness immediately after a pupil answers.
old = 'stats.attempts++;[...answers.children].forEach(b=>b.disabled=true);if(v===c){'
new = 'stats.attempts++;[...answers.children].forEach(b=>b.disabled=true);if(liveQuestion){liveQuestion={...liveQuestion,selected:String(v),result:v===c?"correct":"wrong"};sendQuestionState(true)}if(v===c){'
if old not in s:
    raise SystemExit('Answer result anchor not found')
s = s.replace(old, new, 1)

# Close state after feedback disappears; host keeps the last question for ~3 seconds.
old = 'question.classList.remove("open");qOpen=false;qLock=false;if(mode==="star")placeStar();questionMode="star";'
new = 'question.classList.remove("open");qOpen=false;qLock=false;liveQuestion=null;sendQuestionState(false);if(mode==="star")placeStar();questionMode="star";'
if old not in s:
    raise SystemExit('Question close anchor not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('Added live selected-player question display for host observer.')
