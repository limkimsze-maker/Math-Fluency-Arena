from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

MARKER = 'LIKE_FRACTIONS_V1'
if MARKER in s:
    raise SystemExit('Like fractions mode already installed')

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

# 1) One combined selector option for both operations, in live class and bot mode.
old_option = '<option value="fraction">Identify Fractions</option><option value="mixed">Mixed: + − × ÷</option>'
new_option = '<option value="fraction">Identify Fractions</option><option value="likefrac">Adding &amp; Subtracting Like Fractions</option><option value="mixed">Mixed: + − × ÷</option>'
replace_count(old_option, new_option, 2, 'like fractions selector option')

# 2) Register the combined mode name.
old_mode = 'fraction:"Identify Fractions",mixed:"Mixed: + − × ÷"'
new_mode = 'fraction:"Identify Fractions",likefrac:"Adding & Subtracting Like Fractions",mixed:"Mixed: + − × ÷"'
replace_once(old_mode, new_mode, 'modeNames like fractions')

# 3) Add lightweight like-fraction question generation. Results stay proper and are chosen in simplest form to avoid equivalent-answer ambiguity.
helpers = r'''// LIKE_FRACTIONS_V1 — one combined mode for adding and subtracting like fractions
function fractionGcd(a,b){a=Math.abs(a);b=Math.abs(b);while(b){const t=a%b;a=b;b=t}return a||1}
function makeLikeFractionOptions(num,den){
  const correct=num+"/"+den,out=[correct],seen=new Set([correct]);
  const add=(n,d)=>{if(d<2||d>12||n<1||n>=d||n*den===num*d)return;const k=n+"/"+d;if(!seen.has(k)){seen.add(k);out.push(k)}};
  add(num-1,den);add(num+1,den);add(num-2,den);add(num+2,den);add(num,den-1);add(num,den+1);
  let guard=0;while(out.length<4&&guard++<120){const d=rand(2,12),n=rand(1,d-1);add(n,d)}
  return out.slice(0,4).sort(()=>Math.random()-.5)
}
function makeLikeFractionQ(){
  const addition=Math.random()<.5;
  let den,a,b,c,guard=0;
  do{
    den=rand(3,12);
    if(addition){a=rand(1,den-2);b=rand(1,den-a-1);c=a+b}
    else{a=rand(2,den-1);b=rand(1,a-1);c=a-b}
  }while(fractionGcd(c,den)!==1&&guard++<80);
  return{text:a+"/"+den+(addition?" + ":" − ")+b+"/"+den,correct:c+"/"+den,options:makeLikeFractionOptions(c,den)}
}
'''
replace_once('function drawFractionVisual(canvas,visual){', helpers + 'function drawFractionVisual(canvas,visual){', 'like fractions helper insertion')

# 4) Route the combined mode through its generator.
old_route = 'if(mode==="fraction")return makeFractionQ();if(mode==="mixed")'
new_route = 'if(mode==="fraction")return makeFractionQ();if(mode==="likefrac")return makeLikeFractionQ();if(mode==="mixed")'
replace_once(old_route, new_route, 'makeQ like fractions route')

path.write_text(s, encoding='utf-8')
print('Installed combined Adding & Subtracting Like Fractions mode')
