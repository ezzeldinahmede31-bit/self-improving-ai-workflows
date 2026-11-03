import React from "react";
import {
  AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame, useVideoConfig
} from "remotion";

const C = {
  navy: "#0a1128", black: "#05070d", gold: "#d4af37",
  cyan: "#00f0ff", white: "#f4f5f7", muted: "#8d9bb5"
};

const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const Grain: React.FC = () => (
  <AbsoluteFill style={{ opacity: 0.12, pointerEvents: "none", mixBlendMode: "soft-light" }}>
    <svg width="100%" height="100%">
      <filter id="noise">
        <feTurbulence type="fractalNoise" baseFrequency=".82" numOctaves="3" stitchTiles="stitch"/>
        <feColorMatrix type="saturate" values="0"/>
      </filter>
      <rect width="100%" height="100%" filter="url(#noise)" opacity=".24"/>
    </svg>
  </AbsoluteFill>
);

const Grid: React.FC<{opacity?:number}> = ({opacity=.18}) => (
  <AbsoluteFill style={{opacity, backgroundImage:
    "linear-gradient(rgba(0,240,255,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,.12) 1px, transparent 1px)",
    backgroundSize:"80px 80px", maskImage:"linear-gradient(to bottom, transparent, black 18%, black 82%, transparent)"}}/>
);

const Eyebrow: React.FC<{children:string}> = ({children}) => (
  <div style={{fontFamily:"Arial",fontSize:17,letterSpacing:5,color:C.cyan,fontWeight:700}}>{children}</div>
);

const Title: React.FC<{children:React.ReactNode; size?:number; align?:"left"|"center"}> =
({children,size=76,align="left"}) => (
  <div style={{fontFamily:"Arial, sans-serif",fontSize:size,fontWeight:800,lineHeight:1.02,
    letterSpacing:-2.8,color:C.white,textAlign:align,textShadow:"0 8px 50px rgba(0,0,0,.5)"}}>{children}</div>
);

const Background: React.FC<{accent?:string}> = ({accent=C.cyan}) => {
  const f=useCurrentFrame();
  const drift=interpolate(f,[0,900],[-80,80]);
  return <AbsoluteFill style={{background:`radial-gradient(ellipse at ${55+drift/18}% 42%, #14264a 0%, ${C.navy} 42%, ${C.black} 100%)`}}>
    <div style={{position:"absolute",width:900,height:900,borderRadius:"50%",border:`1px solid ${accent}22`,
      right:-280,top:-350,transform:`rotate(${f*.025}deg)`,boxShadow:`0 0 100px ${accent}0b`}}/>
    <Grid/><Grain/>
  </AbsoluteFill>;
};

const Reveal: React.FC<{start:number; children:React.ReactNode; y?:number}> = ({start,children,y=35}) => {
  const f=useCurrentFrame();
  const p=interpolate(f,[start,start+24],[0,1],{...clamp,easing:Easing.out(Easing.cubic)});
  return <div style={{opacity:p,transform:`translateY(${(1-p)*y}px)`}}>{children}</div>;
};

const Contract: React.FC<{index:number}> = ({index}) => {
  const f=useCurrentFrame();
  const x=interpolate(f,[0,120],[100+index*28,-20-index*10],clamp);
  const rotate=interpolate(f,[0,120],[index%2?5:-4,0],clamp);
  return <div style={{position:"absolute",left:`${x}%`,top:`${18+index*12}%`,width:360,height:470,
    border:"1px solid rgba(0,240,255,.28)",background:"linear-gradient(145deg,rgba(18,35,65,.92),rgba(4,10,22,.88))",
    boxShadow:"0 35px 90px rgba(0,0,0,.45)",padding:28,transform:`rotate(${rotate}deg) scale(${.9+index*.025})`,
    opacity:.82-index*.12}}>
    <div style={{display:"flex",justifyContent:"space-between",color:C.cyan,fontSize:11,letterSpacing:3}}>
      <span>AGREEMENT / {String(index+1).padStart(2,"0")}</span><span>CONFIDENTIAL</span>
    </div>
    <div style={{height:1,background:"#00f0ff55",margin:"24px 0"}}/>
    {[88,64,95,72,84,54,92,68,82,46].map((w,i)=><div key={i} style={{height:5,width:`${w}%`,marginBottom:13,
      background:i===3?"#d4af3780":"#8fa8c344",borderRadius:5}}/>)}
    <div style={{position:"absolute",bottom:28,left:28,right:28,display:"flex",justifyContent:"space-between",
      color:"#8192ac",fontSize:10,letterSpacing:2}}><span>LEGAL REVIEW</span><span>PAGE 0{index+1}</span></div>
  </div>;
};

const Intro: React.FC = () => {
  const f=useCurrentFrame();
  const scale=interpolate(f,[0,80],[1.18,1],clamp);
  const line=interpolate(f,[30,85],[0,1],clamp);
  return <AbsoluteFill>
    <Background accent={C.gold}/>
    <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",padding:"0 150px"}}>
      <div style={{transform:`scale(${scale})`,transformOrigin:"left center"}}>
        <Eyebrow>THE INTELLIGENCE SHIFT  /  STORY 01</Eyebrow>
        <div style={{height:2,width:700*line,background:C.gold,margin:"30px 0"}}/>
        <Title size={112}>JPMORGAN<br/><span style={{color:C.gold}}>COiN</span></Title>
        <div style={{marginTop:34,fontSize:25,letterSpacing:7,color:"#c0c9d8",fontFamily:"Arial"}}>THE 360,000 HOUR PROBLEM</div>
      </div>
    </div>
    <div style={{position:"absolute",right:150,bottom:100,color:"#64748b",fontSize:13,letterSpacing:4}}>A STORY ABOUT TIME</div>
  </AbsoluteFill>;
};

const Problem: React.FC = () => {
  const f=useCurrentFrame();
  const n=interpolate(f,[18,95],[0,360000],{...clamp,easing:Easing.out(Easing.exp)});
  return <AbsoluteFill>
    <Background/>
    <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",padding:"0 150px"}}>
      <div style={{width:"58%"}}>
        <Reveal start={4}><Eyebrow>THE HIDDEN COST</Eyebrow></Reveal>
        <Reveal start={14}><Title>Thousands of contracts.<br/>One impossible backlog.</Title></Reveal>
        <Reveal start={40}><div style={{marginTop:35,fontSize:23,color:C.muted,lineHeight:1.5,maxWidth:760}}>
          A mountain of legal documents. Repetitive review. Critical details buried in pages of text.
        </div></Reveal>
      </div>
      <div style={{position:"absolute",right:120,top:300,textAlign:"right"}}>
        <div style={{fontSize:112,fontWeight:800,color:C.gold,fontFamily:"Arial",fontVariantNumeric:"tabular-nums"}}>
          {Math.round(n).toLocaleString("en-US")}
        </div>
        <div style={{fontSize:19,letterSpacing:5,color:C.cyan}}>HOURS / YEAR</div>
        <div style={{fontSize:14,letterSpacing:3,color:C.muted,marginTop:15}}>SPENT ON CONTRACT REVIEW</div>
      </div>
    </div>
  </AbsoluteFill>;
};

const Machine: React.FC = () => {
  const f=useCurrentFrame();
  const pulse=1+Math.sin(f*.09)*.035;
  return <AbsoluteFill>
    <Background/>
    <div style={{position:"absolute",left:130,top:140}}><Eyebrow>THE BREAKTHROUGH</Eyebrow>
      <div style={{marginTop:24}}><Title>Meet COiN.</Title></div>
      <div style={{fontSize:22,color:C.muted,marginTop:18}}>Contract Intelligence</div>
    </div>
    {[0,1,2,3].map(i=><Contract key={i} index={i}/>)}
    <div style={{position:"absolute",left:"48%",top:"35%",width:360,height:360,borderRadius:"50%",
      border:`1px solid ${C.cyan}88`,background:"radial-gradient(circle,rgba(0,240,255,.16),rgba(8,18,40,.92) 65%)",
      boxShadow:"0 0 100px #00f0ff22,inset 0 0 80px #00f0ff18",transform:`scale(${pulse})`,
      display:"flex",alignItems:"center",justifyContent:"center"}}>
      <div style={{textAlign:"center"}}>
        <div style={{fontSize:64,fontWeight:900,color:C.cyan,letterSpacing:-4}}>COiN</div>
        <div style={{fontSize:12,color:"#b6c8df",letterSpacing:4,marginTop:12}}>READ · EXTRACT · VERIFY</div>
      </div>
    </div>
    <div style={{position:"absolute",left:"42%",top:"52%",width:180,height:1,background:C.cyan,transform:"rotate(-18deg)",opacity:.5}}/>
  </AbsoluteFill>;
};

const Extraction: React.FC = () => {
  const f=useCurrentFrame();
  const progress=interpolate(f,[5,140],[0,100],clamp);
  const rows=["Borrower name","Effective date","Maturity date","Interest rate","Covenant terms"];
  return <AbsoluteFill>
    <Background/>
    <div style={{position:"absolute",left:140,top:130}}><Eyebrow>FROM DOCUMENTS TO DECISIONS</Eyebrow>
      <div style={{marginTop:22}}><Title>Find the signal.<br/>Ignore the noise.</Title></div>
    </div>
    <div style={{position:"absolute",left:150,bottom:115,width:700}}>
      <div style={{display:"flex",justifyContent:"space-between",color:C.cyan,fontSize:13,letterSpacing:3}}>
        <span>DOCUMENT ANALYSIS</span><span>{Math.round(progress)}%</span>
      </div>
      <div style={{height:4,background:"#243653",marginTop:15}}>
        <div style={{height:4,width:`${progress}%`,background:C.cyan,boxShadow:"0 0 18px #00f0ff"}}/>
      </div>
    </div>
    <div style={{position:"absolute",right:145,top:170,width:610,padding:35,border:"1px solid #00f0ff55",
      background:"rgba(5,12,27,.88)",boxShadow:"0 35px 100px #0008"}}>
      <div style={{display:"flex",justifyContent:"space-between",color:C.gold,fontSize:13,letterSpacing:3}}>
        <span>EXTRACTED FIELDS</span><span>LIVE SCAN</span>
      </div>
      {rows.map((r,i)=>{
        const p=interpolate(f,[20+i*18,42+i*18],[0,1],clamp);
        return <div key={r} style={{display:"flex",justifyContent:"space-between",padding:"22px 0",
          borderBottom:"1px solid #25334b",opacity:p,transform:`translateX(${(1-p)*30}px)`}}>
          <span style={{fontSize:19,color:"#c5d0df"}}>{r}</span>
          <span style={{fontSize:13,color:C.cyan,letterSpacing:2}}>IDENTIFIED ✓</span>
        </div>;
      })}
    </div>
  </AbsoluteFill>;
};

const Result: React.FC = () => {
  const f=useCurrentFrame();
  const count=interpolate(f,[10,95],[0,360000],{...clamp,easing:Easing.out(Easing.exp)});
  return <AbsoluteFill>
    <Background accent={C.gold}/>
    <div style={{position:"absolute",inset:0,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center"}}>
      <Reveal start={0}><Eyebrow>THE IMPACT</Eyebrow></Reveal>
      <div style={{fontSize:190,fontWeight:900,letterSpacing:-9,color:C.gold,fontFamily:"Arial",fontVariantNumeric:"tabular-nums",
        textShadow:"0 0 90px #d4af3722",marginTop:25}}>
        {Math.round(count).toLocaleString("en-US")}
      </div>
      <Reveal start={35}><div style={{fontSize:25,letterSpacing:8,color:C.white,marginTop:8}}>HOURS OF WORK — EVERY YEAR</div></Reveal>
      <Reveal start={65}><div style={{height:1,width:480,background:C.gold,margin:"40px 0"}}/></Reveal>
      <Reveal start={78}><Title size={47} align="center">Time returned to the people<br/>who make the decisions.</Title></Reveal>
      <div style={{position:"absolute",bottom:55,fontSize:12,letterSpacing:4,color:"#77849a"}}>JPMORGAN COiN  /  STORY 01</div>
    </div>
  </AbsoluteFill>;
};

const Outro: React.FC = () => (
  <AbsoluteFill>
    <Background accent={C.gold}/>
    <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column"}}>
      <Eyebrow>THE INTELLIGENCE SHIFT</Eyebrow>
      <div style={{marginTop:30}}><Title size={88} align="center">What would you do<br/>with 360,000 hours?</Title></div>
      <div style={{width:100,height:2,background:C.gold,marginTop:45}}/>
      <div style={{marginTop:28,fontSize:15,letterSpacing:5,color:C.muted}}>STORY 01  /  JPMORGAN COiN</div>
    </div>
  </AbsoluteFill>
);

export const COINFilm: React.FC = () => {
  const {fps}=useVideoConfig();
  const scenes=[
    {from:0,duration:150,component:<Intro/>},
    {from:130,duration:150,component:<Problem/>},
    {from:260,duration:180,component:<Machine/>},
    {from:420,duration:180,component:<Extraction/>},
    {from:580,duration:170,component:<Result/>},
    {from:730,duration:170,component:<Outro/>}
  ];
  return <AbsoluteFill style={{background:C.black}}>
    {scenes.map((s,i)=><Sequence key={i} from={s.from} durationInFrames={s.duration}>
      <AbsoluteFill style={{opacity:1}}>{s.component}</AbsoluteFill>
    </Sequence>)}
    <AbsoluteFill style={{pointerEvents:"none"}}>
      <div style={{position:"absolute",top:0,left:0,right:0,height:5,background:"rgba(255,255,255,.06)"}}/>
      <div style={{position:"absolute",bottom:0,left:0,right:0,height:3,background:"rgba(255,255,255,.08)"}}/>
    </AbsoluteFill>
  </AbsoluteFill>;
};