import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio,sys,json
from playwright.async_api import async_playwright
DAY=int(sys.argv[1]) if len(sys.argv)>1 else 1
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
        errs=[];pg.on('pageerror',lambda e: errs.append(str(e)));pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(GAME); await pg.wait_for_timeout(300)
        if DAY==1:
            await pg.evaluate("localStorage.clear();location.reload()"); await pg.wait_for_timeout(600)
            print('scene',await pg.evaluate("G.scene"))
            await pg.mouse.click(195,500); await pg.wait_for_timeout(500)
            for i in range(14):
                await pg.mouse.click(195,500); await pg.wait_for_timeout(250)
                if await pg.evaluate("G.scene")!='intro': break
        else:
            await pg.evaluate(f"devState({DAY});SAVE.menuSeen=['浓缩','热美式'];save();go('open');G.tutor=true")
        print('scene',await pg.evaluate("[G.scene,OP.hint]"))
        r=await pg.evaluate("(()=>{const r=opRect();return [r.dy,r.dh,r.gy]})()")
        dy,dh,gy=r
        await pg.mouse.move(195,dy+dh*0.6);await pg.mouse.down();await pg.mouse.move(195,dy-60,steps=10);await pg.mouse.up();await pg.wait_for_timeout(900)
        print('open hint',await pg.evaluate("OP.hint"))
        await pg.mouse.click(195,gy-30); await pg.wait_for_timeout(1200)
        print('scene',await pg.evaluate("G.scene"))
        seen=[];shots=0
        ORD=sys.argv[2].split(',') if len(sys.argv)>2 else []
        for step in range(160):
            if ORD: await pg.evaluate("(o)=>{const w=G.customers.find(c=>c.state==='wait'&&!c._f);if(w){w._f=1;const [b,t]=o[Math.min(G.served,o.length-1)].split('+');w.items=[{base:b,top:t||null}];w.order=w.items[0];w.pat=w.max=999;}}",ORD)
            st=await pg.evaluate("(()=>{const ns=nextStep();return {t:ns&&ns.text,h:ns&&ns.hand||null,served:G.served,hint:G.hintT>0?G.hintMsg:'',gold:G.proc.map(p=>p?!!procState(p).gold:null),brew:G.groups.map(g=>g&&g.stage==='brew'?!!brewState(g).gold:null),clock:Math.round(G.clock)}})()")
            key=(st['t'],st['hint'])
            if not seen or seen[-1]!=key:
                seen.append(key);print(st['clock'],'|',st['t'],'|',st['hint'],'| hand',json.dumps(st['h']))
                if shots<6: await pg.screenshot(path=os.path.join(OUT,f'tut{DAY}_{shots}.png'));shots+=1
            if st['served']>=3: break
            h=st['h']
            # wait for gold if a process is running
            if any(st['gold'])or any(st['brew']):
                gi=[i for i,g in enumerate(st['gold']) if g]; bi=[i for i,g in enumerate(st['brew']) if g]
                if bi:
                    L=await pg.evaluate("({...__L})");await pg.mouse.click(L['groupX'][bi[0]],L['machBot']+5)
                elif gi:
                    L=await pg.evaluate("({...__L})");await pg.mouse.click(L['stageX'][gi[0]],L['rowY']-20)
                await pg.wait_for_timeout(200);continue
            if h and 'drag' in h:
                a,bb=h['drag'],h['to'];await pg.mouse.move(*a);await pg.mouse.down();await pg.mouse.move(*bb,steps=8);await pg.wait_for_timeout(60);await pg.mouse.up();await pg.wait_for_timeout(250);continue
            if h and 'tap' in h:
                await pg.mouse.click(*h['tap']);await pg.wait_for_timeout(250);continue
            if h and 'fling' in h:
                a=h['fling'];await pg.mouse.move(*a);await pg.mouse.down();await pg.mouse.move(a[0],a[1]-200,steps=3);await pg.mouse.up();await pg.wait_for_timeout(400);continue
            await pg.wait_for_timeout(400)
        print('served',await pg.evaluate("G.served"),'errors',errs[:5])
        await b.close()
asyncio.run(main())
