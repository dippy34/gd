/** Render explanatory figures from untouched screenshots and explicit annotations.
 * Optional dependency: sharp (0.34+). No game resources or image generation needed.
 * SHARP_MODULE may point at an existing sharp installation; otherwise npm resolution.
 * Sources, crop rectangles, judgments and provenance live in docs/visual-guide.json.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
const sharp = require(process.env.SHARP_MODULE || 'sharp');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'docs/visual-guide.json')));
const out = path.join(root, 'docs/images/visual-guide');
const intermediate = path.join(root, 'build/visual-guide');
fs.mkdirSync(out, {recursive:true}); fs.mkdirSync(intermediate, {recursive:true});
const C = {bg:'#101722', panel:'#1b2635', text:'#f3f3ee', muted:'#b5c3d3', line:'#536579',
  bad:'#ff9b8f', good:'#8edcbb', lesson:'#8fc8ff', future:'#d6b5ff', amber:'#f4bf78'};
let svg = [];
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
function rect(x,y,w,h,fill=C.panel,stroke='none',r=0) {
  svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`);
}
function line(x1,y1,x2,y2,color=C.line,width=2,dash='') {
  svg.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" ${dash?`stroke-dasharray="${dash}"`:''}/>`);
}
function text(x,y,s,size=24,color=C.text,weight=400) {
  svg.push(`<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${color}">${esc(s)}</text>`);
}
function wrap(x,y,s,max=48,size=24,color=C.muted,lineH=33) {
  let row='', lines=[];
  for(const word of s.split(' ')) {if((row+' '+word).trim().length>max && row){lines.push(row);row=word;}else row+=(row?' ':'')+word;}
  if(row)lines.push(row);
  lines.forEach((s,i)=>text(x,y+i*lineH,s,size,color));
  return y+lines.length*lineH;
}
function circle(x,y,r,fill,stroke='none',width=2) {
  svg.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`);
}
function pin(x,y,n,color) {
  circle(x,y,19,C.bg,color,3);text(x-7,y+8,n,23,color,700);
}
function arrow(x1,y1,x2,y2,color=C.good) {
  line(x1,y1,x2,y2,color,3);
  const a=Math.atan2(y2-y1,x2-x1),d=12;
  line(x2,y2,x2-d*Math.cos(a-0.5),y2-d*Math.sin(a-0.5),color,3);
  line(x2,y2,x2-d*Math.cos(a+0.5),y2-d*Math.sin(a+0.5),color,3);
}
function imagePanel(p,x,y,w,h,color) {
  const src=manifest.sources[p.source];
  const crop=p.crop || [0,0,...src.size];
  const [cx,cy,cw,ch]=crop;
  const scale=Math.min(w/cw,h/ch), dw=cw*scale,dh=ch*scale;
  const dx=x+(w-dw)/2,dy=y+(h-dh)/2;
  rect(x,y,w,h,'#080c12');
  // SVG viewport crops the displayed source; the source PNG is never altered.
  const bytes=fs.readFileSync(path.join(root,src.path));
  svg.push(`<svg x="${dx}" y="${dy}" width="${dw}" height="${dh}" viewBox="${cx} ${cy} ${cw} ${ch}" overflow="hidden"><image width="${src.size[0]}" height="${src.size[1]}" href="data:image/png;base64,${bytes.toString('base64')}"/></svg>`);
  for(const a of p.marks||[]) {
    const ac=C[a.tone]||color;
    if(a.box) {
      const [bx,by,bw,bh]=a.box;
      rect(dx+(bx-cx)*scale,dy+(by-cy)*scale,bw*scale,bh*scale,'none',ac);
    }
    pin(dx+(a.at[0]-cx)*scale,dy+(a.at[1]-cy)*scale,a.id,ac);
  }
  rect(x,y,w,h,'none',C.line);
}
function note(x,y,n,title,body,width=29,color=C.amber) {
  pin(x+18,y-7,n,color);text(x+50,y,title,26,C.text,700);
  return wrap(x+50,y+38,body,width,23,C.muted,31);
}
function header(b) {
  const col=C[b.tone];
  rect(0,0,1600,1000,C.bg);
  text(40,43,`${b.category.toUpperCase()}  /  ${b.id.slice(0,2)}`,22,col,700);
  text(40,96,b.title,43,C.text,700);
  text(40,136,b.subtitle,23,C.muted);
}
function footer(b) {
  line(40,878,1560,878,C.line);
  text(40,919,b.takeaway,27,C[b.tone],700);
  text(40,961,b.evidence,20,C.muted);
}
function single(b) {
  text(40,181,b.panels[0].label,21,C[b.tone],600);
  imagePanel(b.panels[0],40,200,1030,630,C[b.tone]);
  b.notes.forEach((n,i)=>note(1100,231+i*204,n.id,n.title,n.body,27,C[n.tone]||C[b.tone]));
}
function pair(b) {
  b.panels.forEach((p,i)=>{
    const x=40+774*i;
    text(x,182,p.label,22,C[p.tone]||C[b.tone],700);
    imagePanel(p,x,201,746,420,C[p.tone]||C[b.tone]);
    p.notes.forEach((n,j)=>note(x,665+j*103,n.id,n.title,n.body,50,C[n.tone]||C[p.tone]||C[b.tone]));
  });
}
function boxText(x,y,w,h,title,body,color=C.good) {
  rect(x,y,w,h,C.panel,color,8);text(x+20,y+36,title,26,C.text,700);wrap(x+20,y+70,body,Math.floor(w/14),22,C.muted,30);
}
function groups(b) {
  text(40,190,'BEFORE: one group, unrelated objects',26,C.bad,700);
  boxText(40,215,310,100,'Move trigger','Target = 24',C.bad);
  boxText(510,215,500,100,'Group 24','Blue orb + later scenery',C.bad);
  arrow(350,265,510,265,C.bad);
  arrow(1010,265,1120,265,C.bad);
  boxText(1120,215,440,100,'Both move','The ending appears to vanish.',C.bad);
  text(40,374,'AFTER: separate behavior, preserve the later pulse',26,C.good,700);
  boxText(40,401,310,100,'Move trigger','Target = 1156');
  boxText(510,401,500,118,'Group 1156','Blue orb + 105 attached trim objects');
  arrow(350,451,510,451);
  boxText(1120,401,440,118,'Group 24 stays separate','29 later objects + original pulse');
  line(1070,392,1070,530,C.line,2,'8 8');
  text(40,583,'ALSO: organizing the editor must not change draw order',26,C.lesson,700);
  const labels=[['90 · SHIP','100–109'],['91 · WAVE','110–119'],['92 · ROBOT','120–129'],['93 · CUBE','130–139'],['94 · UFO','140–149'],['95 · EXIT','150–159']];
  labels.forEach(([a,z],i)=>{rect(40+i*255,610,240,90,C.panel,C.line,5);text(56+i*255,642,a,22,C.text,700);text(56+i*255,676,z,24,C.lesson);});
  boxText(40,730,740,113,'Editor fields 20 / 61','Select by object role and section. Example: 131 = cube interactions.',C.lesson);
  boxText(810,730,750,113,'Render fields 24 / 25','Control depth and order. These are NOT editor-layer fields.',C.lesson);
}
function polygon(points,fill,stroke='none',width=2) {
  svg.push(`<polygon points="${points.map(p=>p.join(',')).join(' ')}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`);
}
function assemblyScene(x,y,good) {
  rect(x,y,746,420,'#170f12',C.line);
  rect(x+34,y+45,677,260,'#26232b','#655155');
  rect(x+34,y+305,677,16,'#55515b');
  for(let i=0;i<7;i++)polygon([[x+56+i*91,y+321],[x+86+i*91,y+367],[x+116+i*91,y+321]],'#3d3334','#b78462');
  if(!good) {
    for(const [a,top,bot] of [[100,12,380],[200,65,405],[490,0,390],[550,40,340]]){
      rect(x+a,y+top,12,bot-top,'#947b70');
    }
    rect(x+290,y+112,90,120,'#30272c','#b78462');
    rect(x+625,y+130,80,65,'#30272c','#b78462');
    circle(x+430,y+145,43,'#472923','#b78462');
    line(x+10,y+200,x+730,y+200,'#aa7d69',6);
    pin(x+203,y+385,1,C.bad);pin(x+333,y+124,2,C.bad);
  } else {
    // Proposed support, casing, inset seams and one functional vent; not GD art.
    rect(x+128,y+5,32,40,'#403b40','#92786a');
    rect(x+590,y+5,32,40,'#403b40','#92786a');
    rect(x+53,y+65,639,220,'#211d23','#8c7265');
    line(x+82,y+85,x+82,y+264,'#5b4d50',3);
    line(x+660,y+85,x+660,y+264,'#5b4d50',3);
    rect(x+270,y+115,220,90,'#101116','#ad7454');
    for(let i=0;i<7;i++)rect(x+287+i*28,y+129,10,62,'#ac4b2c');
    for(const xx of [66,679])for(const yy of [78,273])circle(x+xx,y+yy,5,'#aa8970');
    pin(x+144,y+25,1,C.good);pin(x+491,y+114,2,C.good);
    text(x+270,y+395,'OPEN ROUTE BELOW',19,C.muted);
  }
}
function assembly(b) {
  text(40,181,'AVOID · unrelated additions',23,C.bad,700);
  text(814,181,'TRY · one supported furnace housing',23,C.good,700);
  assemblyScene(40,201,false);assemblyScene(814,201,true);
  note(40,665,1,'Endpoints without a reason','Rods continue through the casing and into open air.',48,C.bad);
  note(40,768,2,'Several competing props','More shapes add noise without explaining the machine.',48,C.bad);
  note(814,665,1,'Supports carry the body','Use visible mount points and keep the route silhouette.',48,C.good);
  note(814,768,2,'Detail belongs to the surface','Inset a vent, seams and fasteners inside one casing.',48,C.good);
}
function motionFrame(x,y,phase) {
  rect(x,y,490,320,'#17121a',C.line);
  for(let j=0;j<3;j++)line(x+10,y+60+j*75,x+480,y+60+j*75,'#35262c',3);
  rect(x+25,y+150,80,150,'#602b22','#8e4a30');
  for(let i=0;i<3;i++)rect(x+37+i*22,y+175,11,105,'#bd602e');
  circle(x+333,y+106,78,'#201d26','#68504a',8);
  for(let i=0;i<5;i++){
    const a=2*Math.PI*i/5+phase*.36;
    const pts=[[0,0],[Math.cos(a)*66,Math.sin(a)*66],[Math.cos(a+.45)*50,Math.sin(a+.45)*50]].map(([a,b])=>[x+333+a,y+106+b]);
    polygon(pts,'#5f4540');
  }
  circle(x+333,y+106,10,'#bc693c');
  rect(x+175,y+262,266,14,'#776355');
  circle(x+220,y+238,17,'#422a29','#c68e66',3);
  const flakes=[[119,37,5],[179,79,3],[242,22,4],[283,163,3],[415,159,5],[465,23,3],[147,173,3]];
  flakes.forEach(([a,b,s],i)=>{
    const dx=phase*(i%2?5:-3),dy=phase*(8+i*2);
    polygon([[x+a+dx,y+b+dy],[x+a+dx+s,y+b+dy+2],[x+a+dx+1,y+b+dy+s]],i===3?'#b07345':'#695751');
  });
  text(x+16,y+304,['A · initial','B · drifting / turning','C · movement extreme'][phase],20,C.muted);
}
function motion(b) {
  [40,555,1070].forEach((x,i)=>motionFrame(x,203,i));
  text(40,182,'ILLUSTRATIVE STATES · not rendered gameplay, not an approved animation',23,C.future,700);
  const captions=[['Small, varied ash','Sparse irregular flakes. Different drift rates. Mostly dim, with occasional warm embers.'],['Motion with a cause','Fan blades turn inside a fixed casing. Attachments travel with their parent assembly.'],['Review it in the game','Keep interactions legible at every state. Record matching camera, time and aspect ratio.']];
  captions.forEach(([a,b],i)=>{text(40+i*515,568,a,25,C.text,700);wrap(40+i*515,605,b,35,23,C.muted,32);});
  rect(40,735,1520,108,C.panel,C.line,7);
  text(62,772,'BEFORE EXPANDING IT',24,C.future,700);
  text(62,812,'Test one room → capture its motion → compare readability → measure cost → decide whether to extend.',24,C.text);
}
let rendered=[];
for(const b of manifest.boards) {
  svg=[`<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000"><g font-family="DejaVu Sans,Arial,sans-serif">`];
  header(b);
  ({single,pair,groups,assembly,motion}[b.layout])(b);
  footer(b);svg.push('</g></svg>');
  const document=svg.join('\n');
  fs.writeFileSync(path.join(intermediate,b.id+'.svg'),document);
  const filename=b.id+'.png';
  await sharp(Buffer.from(document)).png().toFile(path.join(out,filename));
  rendered.push({id:b.id,path:'docs/images/visual-guide/'+filename,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,filename))).digest('hex')});
  console.log(filename);
}
const sha = filename => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,filename))).digest('hex');
fs.writeFileSync(path.join(out,'rendered.json'),JSON.stringify({generator:'tools/build_visual_guide.mjs',
  generator_sha256:sha('tools/build_visual_guide.mjs'), manifest_sha256:sha('docs/visual-guide.json'),
  size:[1600,1000], boards:rendered},null,2)+'\n');
