import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio,json,sys
from playwright.async_api import async_playwright
SPEED=float(sys.argv[1]) if len(sys.argv)>1 else 7.0
QLO=float(sys.argv[2]) if len(sys.argv)>2 else 0.78
JS="""
async ([SPEED,QLO])=>{
const log=[];const S=()=>SAVE;
function mkCup(o){const gl=o.base[0]==='冰';const c=newCup(gl,null,W/2,L.trayY);c.loc={t:'tray'};c.hasShot=true;c.q1=rand(QLO,1);c.settled=true;
 const st={'浓缩':'shot','热美式':'americano','热拿铁':'latte','冰美式':'iceA','冰拿铁':'iceL'}[o.base];c.stage=st;c.cubes=gl?(o.mod==='less'?3:o.mod==='more'?6:5):0;c.mq=rand(QLO,1);c.artQ=rand(QLO,1);c.cmQ=rand(QLO,1);c.topQ=rand(QLO,1);c.art={shape:'heart',size:0.8,q:c.artQ};c.artT=0.7;c.milkT=63;c.top=o.top||null;return c;}
let day0=SAVE.day;
for(let guard=0;guard<60&&SAVE.day<=51;guard++){
 go('open');if(SAVE.story){joinStaff(SAVE.story);}startPlay();G.clockIn.slice().forEach(k=>clockIn(k,true));if(SAVE.drawer){const o=G.customers;}
 let t=0,busy=0;const T=()=>Math.max(2.8,SPEED-1.0*staffCount());
 while(G.scene==='play'&&t<400){Scenes.play.update(0.05);t+=0.05;busy-=0.05;
  if(busy<=0){const cu=G.customers.find(c=>c.state==='wait');if(cu&&(cu.waitT||0)>1){const o=cu.items[0];serve(cu,mkCup(o));busy=T();}}}
 // close
 go('summary');const d=G.endedDay;
 const rec={d,money:G.money,served:G.served,lost:G.lost,save:SAVE.weekMoney,rep:Math.round(SAVE.totalMoney),staff:staffCount(),review:G.reviewDay||0,got:G.gotToday.slice()};
 if(G.reviewDay||d===FINAL_DAY){go('review');if(Scenes.review.final){rec.ending=SAVE.ending;log.push(rec);break;}}
 if(G.wasSunday){go('weekend');rec.rentPaid=Scenes.weekend.paid;rec.after=SAVE.weekMoney;}
 go('shop');const sh=Scenes.shop;
 // policy: lures first when affordable, then core devices, keep buffer for rent on sundays
 const rentNeed=()=>{const wd=((SAVE.day-1)%7)+1;return wd>=5?rentOf(week())*0.6:0;};
 const buy=(it,isL)=>{if(SAVE.weekMoney-it.price<rentNeed())return;SAVE.weekMoney-=it.price;if(isL){SAVE.lures.push(it.k);rec.bought=(rec.bought||[]).concat(it.name);}else{SAVE.perks[it.id]=1;if(it.id==='drawer')SAVE.drawer=true;rec.bought=(rec.bought||[]).concat(it.name);}};
 if(SAVE.day>14)for(const l of DATA.lures)if(!SAVE.lures.includes(l.k)&&(!l.req||l.req()))buy(l,true);
 for(const id of ['ice','milk','board','wide','big','kettle','drawer','cinp','caramelp','coaster','plants','lamps','frame','awning','neon']){const it=sh.lists.dev.concat(sh.lists.cup,sh.lists.front||[]).find(x=>x.id===id);if(it&&!P(id)&&!(it.fork&&forkTaken(it.fork)))buy(it,false);}
 save();
 log.push(rec);
}
return log;}
"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':390,'height':844})
        errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(GAME); await pg.wait_for_timeout(300)
        await pg.evaluate("localStorage.clear();SAVE=freshSave();SAVE.introSeen=1;save();")
        log=await pg.evaluate(JS,[SPEED,QLO])
        for r in log:
            print(r['d'],'¥',r['money'],'srv',r['served'],'lost',r['lost'],'save',r['save'],'rep',r['rep'],'staff',r['staff'],('REVIEW' if r['review'] else ''),('rent:'+str(r.get('rentPaid'))+'→'+str(r.get('after')) if 'rentPaid' in r else ''),r.get('bought',''),'|'.join(g for g in r['got'] if '入职' in g or '回头' in g or '房东' in g or '留下' in g),r.get('ending',''))
        print('errors',errs[:8])
        await b.close()
asyncio.run(main())
