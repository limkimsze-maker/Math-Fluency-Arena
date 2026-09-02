from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

MARKER = 'EQUIVALENT_FRACTIONS_V1'
if MARKER in s:
    raise SystemExit('Equivalent fractions mode already installed')

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

# 1) Give the fraction modes clearer names and add one combined equivalent/simplest-form option in both selectors.
old_options = '<option value="fraction">Identify Fractions</option><option value="likefrac">Adding &amp; Subtracting Like Fractions</option><option value="mixed">Mixed: + − × ÷</option>'
new_options = '<option value="fraction">Identify Shaded Fractions</option><option value="likefrac">Add &amp; Subtract Like Fractions</option><option value="equivfrac">Equivalent Fractions &amp; Simplest Form</option><option value="mixed">Mixed: + − × ÷</option>'
replace_count(old_options, new_options, 2, 'fraction selector names/options')

# 2) Register the clearer display names.
old_modes = 'fraction:"Identify Fractions",likefrac:"Adding & Subtracting Like Fractions",mixed:"Mixed: + − × ÷"'
new_modes = 'fraction:"Identify Shaded Fractions",likefrac:"Add & Subtract Like Fractions",equivfrac:"Equivalent Fractions & Simplest Form",mixed:"Mixed: + − × ÷"'
replace_once(old_modes, new_modes, 'modeNames equivalent fractions')

# 3) Add lightweight generators. Half the questions identify an equivalent fraction; half ask for simplest form.
helpers = r'''// EQUIVALENT_FRACTIONS_V1 — identify equivalent fractions + simplify to simplest form
function simplestFractionPair(n,d){const g=fractionGcd(n,d);return{n:n/g,d:d/g}}
function makeEquivalentChoiceOptions(baseN,baseD,correctN,correctD){
  const correct=correctN+"/"+correctD,out=[correct],seen=new Set([correct]);
  const add=(n,d)=>{if(d<2||d>12||n<1||n>=d)return;const k=n+"/"+d;if(seen.has(k))return;if(n*baseD===baseN*d)return;seen.add(k);out.push(k)};
  add(correctN-1,correctD);add(correctN+1,correctD);add(correctN,correctD-1);add(correctN,correctD+1);add(baseN,Math.min(12,baseD+1));
  let guard=0;while(out.length<4&&guard++<160){const d=rand(2,12),n=rand(1,d-1);add(n,d)}
  return out.slice(0,4).sort(()=>Math.random()-.5)
}
function makeSimplestChoiceOptions(sourceN,sourceD,simpleN,simpleD){
  const correct=simpleN+"/"+simpleD,out=[correct],seen=new Set([correct]);
  const add=(n,d)=>{if(d<2||d>12||n<1||n>=d)return;const k=n+"/"+d;if(!seen.has(k)){seen.add(k);out.push(k)}};
  add(sourceN,sourceD);add(simpleN-1,simpleD);add(simpleN+1,simpleD);add(simpleN,simpleD-1);add(simpleN,simpleD+1);
  let guard=0;while(out.length<4&&guard++<160){const d=rand(2,12),n=rand(1,d-1);add(n,d)}
  return out.slice(0,4).sort(()=>Math.random()-.5)
}
function makeEquivalentFractionQ(){
  const simplify=Math.random()<.5;
  const candidates=[];
  for(let d=2;d<=6;d++)for(let n=1;n<d;n++)if(fractionGcd(n,d)===1)for(let factor=2;factor<=4;factor++)if(d*factor<=12)candidates.push({n,d,factor});
  const c=candidates[rand(0,candidates.length-1)],sourceN=c.n*c.factor,sourceD=c.d*c.factor;
  if(simplify){
    const simple=simplestFractionPair(sourceN,sourceD),correct=simple.n+"/"+simple.d;
    return{text:"Write "+sourceN+"/"+sourceD+" in its simplest form.",correct,options:makeSimplestChoiceOptions(sourceN,sourceD,simple.n,simple.d)}
  }
  const correct=sourceN+"/"+sourceD;
  return{text:"Which fraction is equivalent to "+c.n+"/"+c.d+"?",correct,options:makeEquivalentChoiceOptions(c.n,c.d,sourceN,sourceD)}
}
'''
replace_once('function drawFractionVisual(canvas,visual){', helpers + 'function drawFractionVisual(canvas,visual){', 'equivalent fractions helper insertion')

# 4) Route the new mode through its generator.
old_route = 'if(mode==="fraction")return makeFractionQ();if(mode==="likefrac")return makeLikeFractionQ();if(mode==="mixed")'
new_route = 'if(mode==="fraction")return makeFractionQ();if(mode==="likefrac")return makeLikeFractionQ();if(mode==="equivfrac")return makeEquivalentFractionQ();if(mode==="mixed")'
replace_once(old_route, new_route, 'makeQ equivalent fractions route')

path.write_text(s, encoding='utf-8')
print('Installed Equivalent Fractions & Simplest Form mode')
