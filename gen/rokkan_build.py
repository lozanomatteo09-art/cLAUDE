#!/usr/bin/env python3
"""Página premium de Rokkan (cliente). Lee las fotos y el menú de las versiones anteriores
(/home/claude/rokkan.html y /home/claude/menu.html) y escribe rokkan/index.html."""
import re, base64, io, html, os
from PIL import Image

SRC = '/home/claude/'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rokkan')
E = lambda s: html.escape(str(s), quote=True)

old = open(SRC + 'rokkan.html', encoding='utf-8').read()
tags = re.findall(r'<img[^>]*>', old)

def uri(i, w=1200, crop=None, q=80):
    m = re.search(r'src="data:image/(\w+);base64,([^"]+)"', tags[i])
    b = base64.b64decode(m.group(2))
    if m.group(1) == 'png':
        return 'data:image/png;base64,' + m.group(2)
    im = Image.open(io.BytesIO(b)).convert('RGB')
    if crop:
        W, H = im.size; nh = int(W / crop)
        if nh < H:
            t = (H - nh) // 2; im = im.crop((0, t, W, t + nh))
        else:
            nw = int(H * crop); l = (W - nw) // 2; im = im.crop((l, 0, l + nw, H))
    if im.width > w:
        im = im.resize((w, int(im.height * w / im.width)))
    o = io.BytesIO(); im.save(o, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(o.getvalue()).decode()

LOGO_D, LOGO_L, FLOR = uri(0), uri(2), uri(3)
HERO = uri(1, 1100, 4 / 5)
CHIRASHI = uri(4, 1000, 4 / 3)
TORCH = uri(14, 1000, 4 / 5)
SUSHI = uri(20, 1000, 4 / 5)
SUC = {'coy': uri(8, 900, 4 / 3), 'coa': uri(9, 900, 4 / 3), 'dv': uri(10, 900, 4 / 3)}
GAL = [uri(i, 600, 1) for i in (21, 18, 19, 5)]

# ---------- menú completo desde menu.html ----------
mh = open(SRC + 'menu.html', encoding='utf-8').read()
cats = []
for cm in re.finditer(r'<div class="cat" id="c\d+"><div class="ch"><span class="jp">(.*?)</span><h3>(.*?)</h3></div><div class="its">(.*?)</div></div>(?=<div class="cat"|</div></section>|\s*</div>)', mh, re.S):
    jp, name, body = cm.groups()
    items = []
    for im in re.finditer(r'<div class="it( cf)?">(.*?)</div></div>(?=<div class="it|$)', body, re.S):
        blk = im.group(2)
        img = re.search(r'<img src="(data:[^"]+)"', blk)
        n = re.search(r'<h4>(.*?)</h4>', blk); pr = re.search(r'<span class="pr">(.*?)</span>', blk)
        ps = re.findall(r'<p(?: class="vo")?>(.*?)</p>', blk)
        vr = re.findall(r'<li><span>(.*?)</span><b>(.*?)</b></li>', blk)
        items.append(dict(img=img.group(1) if img else None, n=n.group(1) if n else '', pr=pr.group(1) if pr else '', ps=ps, vr=vr))
    cats.append((jp, name, items))
assert len(cats) >= 6, len(cats)

def small(datauri):
    try:
        b = base64.b64decode(datauri.split(',', 1)[1])
        im = Image.open(io.BytesIO(b)).convert('RGB')
        s = min(im.size); l = (im.width - s) // 2; t = (im.height - s) // 2
        im = im.crop((l, t, l + s, t + s)).resize((220, 220))
        o = io.BytesIO(); im.save(o, 'JPEG', quality=72, optimize=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(o.getvalue()).decode()
    except Exception:
        return None

chips = ''.join(f'<a href="#c{i}">{c[1]}</a>' for i, c in enumerate(cats))
menu_html = ''
for i, (jp, name, items) in enumerate(cats):
    its = ''
    for it in items:
        ph = small(it['img']) if it['img'] else None
        fig = f'<img class="th" src="{ph}" alt="{E(html.unescape(it["n"]))}">' if ph else ''
        ps = ''.join(f'<p>{p}</p>' for p in it['ps'])
        vr = ('<ul class="vr">' + ''.join(f'<li><span>{a}</span><b>{b}</b></li>' for a, b in it['vr']) + '</ul>') if it['vr'] else ''
        its += f'<div class="mi{" con" if ph else ""}">{fig}<div class="tx"><div class="nl"><h4>{it["n"]}</h4><span class="pr">{it["pr"]}</span></div>{ps}{vr}</div></div>'
    menu_html += f'<div class="mc" id="c{i}"><div class="mh"><span class="jp">{jp}</span><h3>{name}</h3></div><div class="mg">{its}</div></div>'

# ---------- datos de sucursales ----------
def maps(pid): return f'https://www.google.com/maps/search/?api=1&query=Rokkan+cocina+japonesa&query_place_id={pid}'
SUCS = [
    dict(k='coy', n='Coyoacán', tag='La más nueva', dir='Av. Miguel Ángel de Quevedo 600, Santa Catarina, Coyoacán', tel='56 3542 2435', wa='525635422435',
         hor=[('Dom a jue', '1:30 – 9:30 pm'), ('Vie y sáb', '1:30 – 10:00 pm')], r='4.8', rc='9', pid='ChIJa3T2p0P_0YUR5ySyIJXEUIk', dom=None),
    dict(k='coa', n='Coapa', tag='La original · con jardín', dir='Prol. División del Norte 4215, Prados Coapa 2ª Secc., Tlalpan', tel='55 5554 8850', wa='525555548850',
         hor=[('Lun a sáb', '2:00 – 9:30 pm'), ('Domingo', '2:00 – 8:30 pm')], r='4.8', rc='807', pid='ChIJc3cuzF8BzoURqI4Ql9JITsI', dom='https://www.maspedidos.menu/rokkan/rokkan'),
    dict(k='dv', n='Del Valle', tag='Benito Juárez', dir='San Lorenzo 177, Tlacoquemécatl del Valle, Benito Juárez', tel='56 3457 0735', wa='525634570735',
         hor=[('Dom a mié', '1:30 – 9:00 pm'), ('Jue a sáb', '1:30 – 10:00 pm')], r='4.8', rc='307', pid='ChIJfbQ9YgD_0YURSDSCSrZ8YLc', dom='https://www.maspedidos.menu/rokkan/delvalle'),
]
suc_html = ''
for s in SUCS:
    hrs = ''.join(f'<div class="row"><dt>{a}</dt><dd>{b}</dd></div>' for a, b in s['hor'])
    dom = f'<a class="lnk" href="{s["dom"]}" target="_blank" rel="noopener">Pedir a domicilio</a>' if s['dom'] else ''
    suc_html += f'''<article class="suc"><figure><img src="{SUC[s["k"]]}" alt="Rokkan {s["n"]}"></figure>
<div class="sb"><p class="eyebrow">{s["tag"]}</p><h3 class="serif">{s["n"]}</h3><p class="dir">{s["dir"]}, CDMX</p>
<p class="rt">★ {s["r"]} · {s["rc"]} reseñas en Google</p><dl class="rows">{hrs}</dl>
<div class="cta"><a class="btn fill" href="#reservar" data-suc="{s["k"]}">Reservar aquí</a><a class="btn" href="{maps(s["pid"])}" target="_blank" rel="noopener">Cómo llegar</a></div>
<p class="links"><a class="lnk" href="tel:+52{s["tel"].replace(" ", "")}">{s["tel"]}</a>{dom}</p></div></article>'''

RES = [
    ('Excelente lugar para cenar en familia, en una cita o solo. La comida es muy buena y el jardín le da el paisaje perfecto. El sake de la casa es el mejor.', 'Coapa'),
    ('Su ramen es el mejor, con muy buenos precios y excelente servicio. Somos clientes de Coapa y qué gusto que abrieran esta sucursal.', 'Coyoacán'),
    ('Fuimos sin expectativas y nos sorprendió muchísimo. Gran sabor y gran servicio. Recomiendo especialmente el ramen vegano.', 'Del Valle'),
]
quotes = ''.join(f'<div class="quote"><p>“{q}”</p><span>Reseña de Google · {s}</span></div>' for q, s in RES)
gal = ''.join(f'<figure><img src="{g}" alt="Platillo de Rokkan"></figure>' for g in GAL)
opts = ''.join(f'<option value="{s["k"]}">{s["n"]}</option>' for s in SUCS)
wa_js = '{' + ','.join(f'"{s["k"]}":["{s["wa"]}","{s["n"]}"]' for s in SUCS) + '}'

CSS = """
:root{--ink:#1b1e23;--ink2:#14161a;--paper:#f8f5ef;--cream:#efe8dc;--muted:#6c675f;--red:#c4452d;--line:rgba(27,30,35,.13)}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font:400 16px/1.65 'Zen Kaku Gothic New',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}img{display:block;width:100%;height:100%;object-fit:cover}
.w{max-width:1180px;margin:0 auto;padding:0 24px}
.serif{font-family:'Shippori Mincho',Georgia,serif;font-weight:600;letter-spacing:-.005em}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--red)}
.jp{font-family:'Shippori Mincho',serif;color:var(--red);font-size:14px;letter-spacing:.3em}
.btn{display:inline-flex;align-items:center;justify-content:center;height:50px;padding:0 26px;border-radius:999px;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;border:1.5px solid currentColor;cursor:pointer;background:none;font-family:inherit;color:inherit}
.btn.fill{background:var(--red);border-color:var(--red);color:#fff}
nav.top{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--line)}
nav.top .w{display:flex;align-items:center;justify-content:space-between;height:72px;gap:16px}
nav.top .logo img{height:30px;width:auto}
.links{display:flex;align-items:center;gap:30px;font-size:14px;color:var(--muted)}
.links .btn{height:42px;padding:0 22px;font-size:12px;color:#fff}
.hero{background:var(--ink);color:#f3eee6}
.hero .w{display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center;padding-top:84px;padding-bottom:84px}
.hero .jp{display:block;margin-bottom:14px}
.hero .eyebrow{color:#e3a08f;margin-bottom:22px}
.hero h1{font-size:clamp(40px,5.4vw,70px);line-height:1.08;margin-bottom:24px}
.hero p.lead{font-size:17px;color:#cdc7bd;max-width:460px;margin-bottom:36px}
.cta{display:flex;gap:12px;flex-wrap:wrap}
.hero .btn.line{color:#f3eee6}
.hero figure{border-radius:28px;overflow:hidden;aspect-ratio:4/5}
.meta{display:flex;gap:32px;margin-top:40px;padding-top:28px;border-top:1px solid rgba(255,255,255,.16);font-size:14px;color:#bdb6aa}
.meta b{display:block;font-family:'Shippori Mincho',serif;font-size:30px;color:#fff;font-weight:600;line-height:1.15}
section{padding:110px 0}
.split{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center}
.split figure{border-radius:28px;overflow:hidden;aspect-ratio:4/5}
h2{font-size:clamp(34px,4.2vw,54px);line-height:1.1;margin:14px 0 22px}
.lead2{color:var(--muted);font-size:17px;max-width:480px;margin-bottom:30px}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:30px}
.pills span{border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:14px}
/* menú */
.menu{background:var(--cream)}
.menu .head{display:flex;justify-content:space-between;align-items:end;gap:24px;flex-wrap:wrap;margin-bottom:28px}
.chips{display:flex;gap:8px;overflow-x:auto;padding:14px 0;position:sticky;top:72px;background:var(--cream);z-index:3;border-bottom:1px solid var(--line);scrollbar-width:none}
.chips a{flex:none;border:1px solid var(--line);border-radius:999px;padding:8px 16px;font-size:14px;background:var(--paper)}
.mc{padding-top:44px;scroll-margin-top:140px}
.mh{display:flex;align-items:baseline;gap:14px;margin-bottom:10px}
.mh h3{font-family:'Shippori Mincho',serif;font-size:32px;font-weight:600}
.mg{display:grid;grid-template-columns:1fr 1fr;column-gap:56px}
.mi{display:flex;gap:16px;padding:18px 0;border-bottom:1px solid var(--line)}
.mi .th{width:84px;height:84px;border-radius:14px;flex:none}
.mi .tx{flex:1;min-width:0}
.nl{display:flex;justify-content:space-between;gap:16px;align-items:baseline}
.nl h4{font-family:'Shippori Mincho',serif;font-size:19px;font-weight:600;line-height:1.25}
.pr{font-weight:700;white-space:nowrap}
.mi p{color:var(--muted);font-size:14.5px;margin-top:3px}
.vr{list-style:none;margin-top:8px;font-size:14px}
.vr li{display:flex;justify-content:space-between;gap:12px;padding:3px 0;border-top:1px dashed var(--line)}
.mnote{margin-top:30px;font-size:14px;color:var(--muted)}
/* reservar */
.res{background:var(--ink);color:#f3eee6}
.res .split{align-items:start}
.res .lead2{color:#bdb6aa}
.steps{list-style:none;counter-reset:s;margin-top:8px}
.steps li{counter-increment:s;display:flex;gap:14px;padding:14px 0;border-top:1px solid rgba(255,255,255,.12);color:#d8d1c6}
.steps li:before{content:counter(s);font-family:'Shippori Mincho',serif;color:#e3a08f;font-size:20px;width:22px}
form{background:var(--paper);color:var(--ink);border-radius:24px;padding:32px;display:grid;gap:16px}
label{font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);display:grid;gap:6px}
input,select,textarea{font:inherit;font-size:16px;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px;width:100%}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
form .btn{width:100%;margin-top:6px}
.fnote{font-size:13px;color:var(--muted);text-align:center}
/* sucursales */
.sucs{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px}
.suc{background:#fff;border:1px solid var(--line);border-radius:24px;overflow:hidden;display:flex;flex-direction:column}
.suc figure{aspect-ratio:4/3}
.sb{padding:26px;display:flex;flex-direction:column;flex:1}
.sb h3{font-size:32px;margin:6px 0 8px}
.dir{color:var(--muted);font-size:15px}
.rt{font-size:14px;margin:8px 0 14px}
.rows{margin-bottom:22px}
.row{display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid var(--line);font-size:15px}
.row dt{color:var(--muted)}
.sb .cta{margin-top:auto}.sb .btn{height:46px;padding:0 18px;font-size:12px;flex:1}
.sb .links{display:flex;gap:18px;font-size:14px;color:var(--ink);margin-top:16px}
.lnk{border-bottom:1px solid var(--red)}
/* reseñas */
.band{background:var(--red);color:#fff;padding:96px 0}
.band .eyebrow{color:#ffd8cc;text-align:center;margin-bottom:30px}
.quotes{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
.quote{border-top:1px solid rgba(255,255,255,.4);padding-top:24px}
.quote p{font-family:'Shippori Mincho',serif;font-size:21px;line-height:1.45;margin-bottom:16px}
.quote span{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#ffe2d8}
.score{text-align:center;margin-top:52px;font-size:15px;color:#ffe2d8}
.score b{font-family:'Shippori Mincho',serif;font-size:44px;color:#fff;display:block;line-height:1.1}
/* footer */
footer{background:var(--ink2);color:#bdb6aa;padding:72px 0 40px}
footer .eyebrow{color:#e3a08f;margin-bottom:22px}
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:64px}
.strip figure{border-radius:18px;overflow:hidden;aspect-ratio:1}
.cols{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:40px;font-size:14px}
.cols img.lg{height:34px;width:auto;margin-bottom:16px}
.cols h4{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#e3a08f;margin-bottom:14px}
.cols li{list-style:none;margin-bottom:8px}
.legal{margin-top:56px;padding-top:24px;border-top:1px solid rgba(255,255,255,.1);font-size:12px;color:#7d776d;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.mbar{display:none}
@media(max-width:900px){
 .links a:not(.btn){display:none}
 .hero .w{grid-template-columns:1fr;gap:36px;padding-top:40px;padding-bottom:56px}
 .hero figure{aspect-ratio:4/4.2;order:-1;border-radius:22px}
 .split{grid-template-columns:1fr;gap:36px}
 .split figure{aspect-ratio:4/3.4}
 section{padding:72px 0}.band{padding:72px 0}
 .mg{grid-template-columns:1fr}
 .sucs,.quotes{grid-template-columns:1fr}
 .strip{grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:44px}
 .cols{grid-template-columns:1fr 1fr;gap:28px}.cols>div:first-child{grid-column:1/-1}
 form{padding:22px}.two{grid-template-columns:1fr 1fr}
 body{padding-bottom:76px}
 .mbar{display:flex;gap:10px;position:fixed;left:0;right:0;bottom:0;padding:12px 16px calc(12px + env(safe-area-inset-bottom));background:var(--paper);border-top:1px solid var(--line);z-index:6}
 .mbar .btn{flex:1;height:48px;padding:0 12px}
}
"""

JS = """
const WA=%s;
document.querySelectorAll('[data-suc]').forEach(a=>a.addEventListener('click',()=>{document.getElementById('f-suc').value=a.dataset.suc}));
const d=document.getElementById('f-dia');const t=new Date();d.min=t.toISOString().slice(0,10);d.value=d.min;
document.getElementById('rf').addEventListener('submit',e=>{e.preventDefault();
 const f=e.target,s=WA[f.suc.value];
 const fe=new Date(f.dia.value+'T12:00').toLocaleDateString('es-MX',{weekday:'long',day:'numeric',month:'long'});
 let m=`Hola, quiero reservar en Rokkan ${s[1]}.\\nNombre: ${f.nombre.value}\\nDía: ${fe}\\nHora: ${f.hora.value}\\nPersonas: ${f.personas.value}`;
 if(f.com.value.trim())m+=`\\nComentarios: ${f.com.value.trim()}`;
 window.open('https://wa.me/'+s[0]+'?text='+encodeURIComponent(m),'_blank');});
""" % wa_js

horas = ''.join(f'<option>{h}</option>' for h in ['1:30 pm','2:00 pm','2:30 pm','3:00 pm','3:30 pm','4:00 pm','4:30 pm','5:00 pm','5:30 pm','6:00 pm','6:30 pm','7:00 pm','7:30 pm','8:00 pm','8:30 pm','9:00 pm'])
pers = ''.join(f'<option{" selected" if n==2 else ""}>{n}</option>' for n in range(1, 13))

page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Rokkan · Cocina japonesa en Coyoacán, Coapa y Del Valle</title>
<meta name="description" content="Ramen, sushi tradicional, makis, tempura y más. Rokkan Cocina Japonesa en Coyoacán, Coapa y Del Valle, CDMX. Reserva por WhatsApp.">
<link rel="icon" href="{FLOR}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<nav class="top"><div class="w"><a href="#" class="logo"><img src="{LOGO_D}" alt="Rokkan"></a><div class="links"><a href="#menu">Menú</a><a href="#sucursales">Sucursales</a><a href="#resenas">Reseñas</a><a class="btn fill" href="#reservar">Reservar</a></div></div></nav>
<header class="hero"><div class="w"><div>
<span class="jp">六感 · ROKKAN</span>
<p class="eyebrow">Cocina japonesa · Coyoacán · Coapa · Del Valle</p>
<h1 class="serif">Del ramen a la barra de sushi, cocina japonesa hecha con calma.</h1>
<p class="lead">Ramen de caldo lento, sushi tradicional, makis, udon, yakisoba y tempura en tres sucursales del sur de la ciudad.</p>
<div class="cta"><a class="btn line" href="#menu">Ver menú</a><a class="btn fill" href="#reservar">Reservar mesa</a></div>
<div class="meta"><div><b>4.8 ★</b>más de 1,100 reseñas en Google</div><div><b>3</b>sucursales en CDMX</div></div>
</div><figure><img src="{HERO}" alt="Ramen de Rokkan"></figure></div></header>

<section id="nosotros"><div class="w split"><figure><img src="{TORCH}" alt="Cocina de Rokkan"></figure><div>
<span class="jp">私たち</span><h2 class="serif">Tradición japonesa con un toque moderno.</h2>
<p class="lead2">En Rokkan fusionamos la tradición japonesa con toques innovadores, sin renunciar a la calidad. Sashimi, nigiri y temaki frescos; ramen de caldo lento; y para cerrar, mochi o un calpis de la casa.</p>
<div class="pills"><span>Ramen</span><span>Sushi tradicional</span><span>Makis</span><span>Udon</span><span>Yakisoba</span><span>Tempura</span><span>Teppanyaki</span><span>Sake</span></div>
<a class="btn" style="color:var(--red)" href="#menu">Ver el menú</a></div></div></section>

<section class="menu" id="menu"><div class="w">
<div class="head"><div><span class="jp">お品書き</span><h2 class="serif" style="margin-bottom:0">Nuestro menú</h2></div><a class="btn fill" href="#reservar">Reservar mesa</a></div>
<nav class="chips">{chips}</nav>
{menu_html}
<p class="mnote">Precios en pesos mexicanos, IVA incluido. Pueden variar por sucursal.</p>
</div></section>

<section class="res" id="reservar"><div class="w split"><div>
<span class="jp">ご予約</span><h2 class="serif">Reserva tu mesa.</h2>
<p class="lead2">Elige sucursal, día, hora y cuántos son. Tu reservación llega por WhatsApp a la sucursal y ahí mismo te la confirman.</p>
<ol class="steps"><li>Elige tu sucursal</li><li>Día, hora y número de personas</li><li>Envía por WhatsApp y espera tu confirmación</li></ol>
</div>
<form id="rf"><label>Sucursal<select name="suc" id="f-suc">{opts}</select></label>
<div class="two"><label>Día<input type="date" name="dia" id="f-dia" required></label><label>Hora<select name="hora">{horas}</select></label></div>
<div class="two"><label>Personas<select name="personas">{pers}</select></label><label>Tu nombre<input name="nombre" required autocomplete="name"></label></div>
<label>Comentarios (opcional)<textarea name="com" rows="2" placeholder="Cumpleaños, silla para bebé, terraza…"></textarea></label>
<button class="btn fill" type="submit">Enviar reservación por WhatsApp</button>
<p class="fnote">La sucursal confirma tu reservación por WhatsApp.</p></form>
</div></section>

<section id="sucursales"><div class="w">
<span class="jp">店舗</span><h2 class="serif">Tres sucursales, el mismo sabor.</h2>
<div class="sucs">{suc_html}</div></div></section>

<div class="band" id="resenas"><div class="w"><p class="eyebrow">Lo que dicen nuestros clientes</p><div class="quotes">{quotes}</div>
<div class="score"><b>4.8 de 5</b>con más de 1,100 reseñas en Google entre las tres sucursales</div></div></div>

<footer><div class="w"><p class="eyebrow">Galería</p><div class="strip">{gal}</div>
<div class="cols"><div><img class="lg" src="{LOGO_L}" alt="Rokkan"><p>Cocina japonesa en Coyoacán, Coapa y Del Valle, Ciudad de México.</p></div>
<div><h4>Sucursales</h4><ul><li>Coyoacán · 56 3542 2435</li><li>Coapa · 55 5554 8850</li><li>Del Valle · 56 3457 0735</li></ul></div>
<div><h4>Visita</h4><ul><li><a href="#menu">Menú</a></li><li><a href="#sucursales">Sucursales</a></li><li><a href="#reservar">Reservar</a></li></ul></div>
<div><h4>Síguenos</h4><ul><li><a href="https://www.instagram.com/rokkan.mx/" target="_blank" rel="noopener">Instagram</a></li><li><a href="https://www.tiktok.com/@rokkan.mx" target="_blank" rel="noopener">TikTok</a></li><li><a href="https://www.maspedidos.menu/rokkan/rokkan" target="_blank" rel="noopener">Pedir a domicilio</a></li></ul></div></div>
<div class="legal"><span>© 2026 Rokkan Cocina Japonesa</span><span>Diseño: Matteo</span></div></div></footer>
<div class="mbar"><a class="btn" href="#menu" style="color:var(--ink)">Ver menú</a><a class="btn fill" href="#reservar">Reservar</a></div>
<script>{JS}</script>
</body></html>"""

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
print('OK', len(cats), 'categorías', sum(len(c[2]) for c in cats), 'platillos', len(page) // 1024, 'KB')
