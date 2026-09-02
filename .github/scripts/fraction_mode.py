from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

MARKER = 'FRACTION_IDENTIFY_V1'
if MARKER in s:
    raise SystemExit('Fraction identify mode already installed')

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    s = s.replace(old, new, 1)

def replace_count(old, new, expected, label):
    global s
    count = s.count(old)
    if count != expected:
        raise SystemExit(f'{label}: expected {expected} matches, found {count}')
    s = s.replace(old, new)

# 1) Lightweight fraction-question canvas styling, including teacher observer preview.
old_css = '#qText{font-size:clamp(38px,8vw,64px);font-weight:900;margin:8px 0 16px}#answers{display:grid;grid-template-columns:1fr 1fr;gap:10px}'
new_css = '/* FRACTION_IDENTIFY_V1 — shaded-shape fraction questions adapted from the existing fractions practice */\n#fractionCanvas{display:none;width:min(320px,82vw);height:auto;margin:8px auto 10px;background:#fff;border:2px solid #d8dfe8;border-radius:12px}.fractionQ #qText{font-size:clamp(22px,5vw,34px);margin:4px 0 10px}.oqFractionCanvas{display:block;width:min(240px,100%);height:auto;margin:6px 0;border:2px solid #d8dfe8;border-radius:10px;background:#fff}\n#qText{font-size:clamp(38px,8vw,64px);font-weight:900;margin:8px 0 16px}#answers{display:grid;grid-template-columns:1fr 1fr;gap:10px}'
replace_once(old_css, new_css, 'fraction CSS anchor')

# 2) Add the new mode to both the live-room and bot setup selectors.
old_option = '<option value="mixed">Mixed: + − × ÷</option>'
new_option = '<option value="fraction">Identify Fractions</option><option value="mixed">Mixed: + − × ÷</option>'
replace_count(old_option, new_option, 2, 'math selector options')

# 3) Add a reusable canvas to the existing question overlay.
old_question_markup = '<div id="qPrompt" class="small">Solve to pick up this star</div><div id="qText">7 × 8</div><div id="answers"></div>'
new_question_markup = '<div id="qPrompt" class="small">Solve to pick up this star</div><canvas id="fractionCanvas" width="360" height="220" aria-label="Shaded fraction diagram"></canvas><div id="qText">7 × 8</div><div id="answers"></div>'
replace_once(old_question_markup, new_question_markup, 'question canvas markup')

# 4) Bind the new canvas with the existing question DOM references.
old_dom = 'boostBtn=$("boostBtn"),qPrompt=$("qPrompt"),qText=$("qText"),answers=$("answers"),feedback=$("feedback")'
new_dom = 'boostBtn=$("boostBtn"),qPrompt=$("qPrompt"),fractionCanvas=$("fractionCanvas"),qText=$("qText"),answers=$("answers"),feedback=$("feedback")'
replace_once(old_dom, new_dom, 'question DOM binding')

# 5) Register the mode name.
old_modes = 'const modeNames={add20:"Addition within 20",sub20:"Subtraction within 20",mul5:"Multiplication: ×2 to ×5 tables",div5:"Division: ÷2 to ÷5 tables",mul610:"Multiplication: ×6 to ×10 tables",div610:"Division: ÷6 to ÷10 tables",mul10:"Multiplication: ×2 to ×10 tables",div10:"Division: ÷2 to ÷10 tables",mul12:"Multiplication: ×2 to ×12 tables",div12:"Division: ÷2 to ÷12 tables",mixed:"Mixed: + − × ÷"};'
new_modes = 'const modeNames={add20:"Addition within 20",sub20:"Subtraction within 20",mul5:"Multiplication: ×2 to ×5 tables",div5:"Division: ÷2 to ÷5 tables",mul610:"Multiplication: ×6 to ×10 tables",div610:"Division: ÷6 to ÷10 tables",mul10:"Multiplication: ×2 to ×10 tables",div10:"Division: ÷2 to ÷10 tables",mul12:"Multiplication: ×2 to ×12 tables",div12:"Division: ÷2 to ÷12 tables",fraction:"Identify Fractions",mixed:"Mixed: + − × ÷"};'
replace_once(old_modes, new_modes, 'modeNames')

# 6) Add lightweight fraction generation + canvas drawing before the existing makeQ().
fraction_helpers = r'''function normaliseFractionVisual(v){
  if(!v||typeof v!=="object")return null;
  const shape=["circle","rectangle","square"].includes(v.shape)?v.shape:"rectangle",den=Math.max(2,Math.min(12,Number(v.den)||2)),num=Math.max(1,Math.min(den-1,Number(v.num)||1));
  return{shape,num,den}
}
function makeFractionOptions(num,den){
  const correct=num+"/"+den,out=[correct],seen=new Set([correct]);
  const add=(n,d)=>{if(d<2||d>12||n<1||n>=d||n*den===num*d)return;const k=n+"/"+d;if(!seen.has(k)){seen.add(k);out.push(k)}};
  add(num-1,den);add(num+1,den);add(num,den-1);add(num,den+1);add(Math.max(1,num-2),den);add(Math.min(den-1,num+2),den);
  let guard=0;while(out.length<4&&guard++<100){const d=rand(2,12),n=rand(1,d-1);add(n,d)}
  return out.slice(0,4).sort(()=>Math.random()-.5)
}
function makeFractionQ(){
  const den=rand(2,12),num=rand(1,den-1),shapes=["circle","rectangle","square"],shape=shapes[rand(0,shapes.length-1)],correct=num+"/"+den;
  return{text:"What fraction is shaded?",correct,options:makeFractionOptions(num,den),visual:{shape,num,den}}
}
function drawFractionVisual(canvas,visual){
  const v=normaliseFractionVisual(visual);if(!canvas||!v)return;
  const ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);ctx.save();ctx.lineWidth=3;ctx.strokeStyle="#172033";ctx.fillStyle="#ffd84a";
  if(v.shape==="circle"){
    const cx=w/2,cy=h/2,r=Math.min(82,h*.38),step=Math.PI*2/v.den,start=-Math.PI/2;
    for(let i=0;i<v.den;i++){ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,start+i*step,start+(i+1)*step);ctx.closePath();if(i<v.num)ctx.fill();ctx.stroke()}
  }else{
    const boxW=v.shape==="square"?Math.min(150,w*.56):Math.min(250,w*.76),boxH=v.shape==="square"?Math.min(150,h*.66):Math.min(86,h*.42),x0=(w-boxW)/2,y0=(h-boxH)/2,part=boxW/v.den;
    for(let i=0;i<v.den;i++){ctx.beginPath();ctx.rect(x0+i*part,y0,part,boxH);if(i<v.num)ctx.fill();ctx.stroke()}
  }
  ctx.restore();canvas.style.display="block"
}
'''
replace_once('function makeQ(){', fraction_helpers + 'function makeQ(){', 'fraction helper insertion')

# 7) Route fraction mode through the fraction generator.
old_makeq_start = 'function makeQ(){let mode=mathMode;if(mode==="mixed")'
new_makeq_start = 'function makeQ(){let mode=mathMode;if(mode==="fraction")return makeFractionQ();if(mode==="mixed")'
replace_once(old_makeq_start, new_makeq_start, 'makeQ fraction route')

# 8) Share the visual metadata with teacher observer mode.
old_send_visual = 'targetName:liveQuestion.targetName,ts:Date.now()});'
new_send_visual = 'targetName:liveQuestion.targetName,visual:liveQuestion.visual||null,ts:Date.now()});'
replace_once(old_send_visual, new_send_visual, 'questionState visual payload')

old_apply_visual = 'result:d.result==="correct"?"correct":d.result==="wrong"?"wrong":"",targetName:safe(d.targetName||""),updatedAt:Date.now()}'
new_apply_visual = 'result:d.result==="correct"?"correct":d.result==="wrong"?"wrong":"",targetName:safe(d.targetName||""),visual:normaliseFractionVisual(d.visual),updatedAt:Date.now()}'
replace_once(old_apply_visual, new_apply_visual, 'observer question visual state')

old_observer = 'const qt=document.createElement("div");qt.className="oqQuestion";qt.textContent=q.text||"Question";observerQuestion.appendChild(qt);\n  const choices=document.createElement("div");'
new_observer = 'const qt=document.createElement("div");qt.className="oqQuestion";qt.textContent=q.text||"Question";observerQuestion.appendChild(qt);\n  if(q.visual){const cv=document.createElement("canvas");cv.className="oqFractionCanvas";cv.width=300;cv.height=170;observerQuestion.appendChild(cv);drawFractionVisual(cv,q.visual)}\n  const choices=document.createElement("div");'
replace_once(old_observer, new_observer, 'observer fraction canvas')

# 9) Show/hide the diagram whenever a question opens and retain its metadata.
old_open = 'const q=makeQ();liveQuestion={mode,text:q.text,options:q.options.map(String),selected:null,result:"",targetName:stealTargetName};sendQuestionState(true);qText.textContent=q.text;'
new_open = 'const q=makeQ();question.classList.toggle("fractionQ",!!q.visual);if(fractionCanvas){if(q.visual)drawFractionVisual(fractionCanvas,q.visual);else{fractionCanvas.style.display="none";fractionCanvas.getContext("2d").clearRect(0,0,fractionCanvas.width,fractionCanvas.height)}}liveQuestion={mode,text:q.text,options:q.options.map(String),selected:null,result:"",targetName:stealTargetName,visual:q.visual||null};sendQuestionState(true);qText.textContent=q.text;'
replace_once(old_open, new_open, 'openQuestion fraction rendering')

# 10) Make wrong-answer highlighting work for numeric and fraction-string answers.
old_highlight = 'if(Number(b.textContent)===c)b.classList.add("good")'
new_highlight = 'if(String(b.textContent)===String(c))b.classList.add("good")'
replace_once(old_highlight, new_highlight, 'generic correct answer highlight')

path.write_text(s, encoding='utf-8')
print('Installed Identify Fractions mode')
