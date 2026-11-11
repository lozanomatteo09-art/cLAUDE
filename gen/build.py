#!/usr/bin/env python3
"""Generador de muestras premium (estilo Zimo).

Uso:  python3 gen/build.py gen/data/<slug>.json
Sale: <slug>/index.html en la raíz del repo (Cloudflare Pages lo publica en
      https://muestras-web-ay2.pages.dev/<slug>/ unos minutos después del push).

Solo usa la biblioteca estándar. Las fotos se enlazan por URL (no se descargan).
Si el JSON no pasa el control de calidad, no escribe nada y sale con código 2.
"""
import html, json, os, sys, urllib.parse

E = lambda s: html.escape(str(s), quote=True)

PALETAS = {
    # fondo hero, fondo footer, crema, papel, tinta, gris, acento, acento claro (sobre oscuro), eyebrow sobre oscuro
    "olivo":  ("#33382a", "#272b20", "#f4ede1", "#fbf7f0", "#24211c", "#6f685c", "#c2502c", "#e9a07f", "#d8c9a8"),
    "noche":  ("#1f2633", "#161b24", "#efeae1", "#faf8f4", "#1d1f24", "#666a72", "#b8873f", "#e2bb7c", "#cdbb98"),
    "vino":   ("#3b1e23", "#2b1519", "#f5ece7", "#fcf8f6", "#26191b", "#6f6062", "#b4473b", "#e89a8c", "#dcbcae"),
    "cacao":  ("#3a2a20", "#2a1e17", "#f5ece2", "#fcf8f3", "#261d17", "#6f6358", "#c0703a", "#e8ad80", "#d9c2a5"),
    "rosa":   ("#46303a", "#33232a", "#f8eef0", "#fdf9fa", "#2a1f23", "#74656b", "#c8647d", "#efa6b7", "#e3c6cd"),
    "carbon": ("#1d1d1b", "#141413", "#efeae2", "#faf8f5", "#1b1b19", "#6b6862", "#b8893c", "#e0bd7c", "#cfc3ab"),
    "verde":  ("#203a33", "#172b25", "#eef1ea", "#f9faf7", "#18211e", "#5f6964", "#c96a3b", "#eaa47f", "#bfd1c4"),
}
FUENTES = {
    "cormorant": ("Cormorant Garamond", "Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,600;1,700"),
    "fraunces":  ("Fraunces", "Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,600"),
    "dmserif":   ("DM Serif Display", "DM+Serif+Display:ital@0;1"),
    "playfair":  ("Playfair Display", "Playfair+Display:ital,wght@0,500;0,600;1,600"),
}


def falla(msg):
    print("NO PASA CALIDAD:", msg)
    sys.exit(2)


def validar(d):
    for k in ("slug", "nombre", "tipo", "h1", "intro", "direccion", "telefono", "maps_url"):
        if not str(d.get(k, "")).strip():
            falla(f"falta '{k}'")
    if d["tipo"] not in ("comida", "cita"):
        falla("tipo debe ser 'comida' o 'cita'")
    fotos = [f for f in d.get("fotos", []) if str(f).startswith("https://")]
    if len(fotos) < 5:
        falla(f"se necesitan al menos 5 fotos https (hay {len(fotos)})")
    if len(d.get("resenas", [])) < 3:
        falla("se necesitan al menos 3 reseñas reales")
    if len(d.get("horario", [])) < 1:
        falla("falta horario")
    if not d.get("rating") or not d.get("num_resenas"):
        falla("falta calificación o número de reseñas")
    for s in d["slug"]:
        if not (s.islower() or s.isdigit() or s == "-"):
            falla("slug solo con minúsculas, números y guiones")


def construir(d):
    validar(d)
    hero, ink_bg_footer, cream, paper, ink, muted, acc, acc_l, eyeb = PALETAS.get(d.get("paleta", "olivo"), PALETAS["olivo"])
    fam, gf = FUENTES.get(d.get("fuente", "cormorant"), FUENTES["cormorant"])
    cita = d["tipo"] == "cita"
    verbo = "Agendar cita" if cita else "Reservar mesa"
    verbo_corto = "Agendar" if cita else "Reservar"
    nombre = d["nombre"]
    tel = d["telefono"]
    tel_dig = "".join(c for c in tel if c.isdigit())
    tel_href = "tel:+52" + tel_dig[-10:]
    wa = d.get("whatsapp", "").strip()
    if wa:
        wa_dig = "".join(c for c in wa if c.isdigit())
        if len(wa_dig) == 10:
            wa_dig = "52" + wa_dig
        msg = f"Hola, quiero {'agendar una cita' if cita else 'reservar una mesa'} en {nombre}"
        accion = f"https://wa.me/{wa_dig}?text=" + urllib.parse.quote(msg)
        accion_txt = f"{verbo_corto} por WhatsApp"
        tgt = ' target="_blank" rel="noopener"'
    else:
        accion, accion_txt, tgt = tel_href, f"{verbo_corto} por teléfono", ""
    maps = d["maps_url"]
    f = [x for x in d["fotos"] if str(x).startswith("https://")]
    HERO, LADO, CARTA, VISITA = f[0], f[1], f[2], f[3]
    galeria = (f[4:] + f[:4])[:4]
    logo = d.get("logo_texto") or nombre.lower()
    seccion_menu = "Servicios" if cita else "La carta"
    eyebrow_menu = "Lo que hacemos" if cita else "El menú"
    menu = d.get("menu") or []

    if menu:
        filas = ""
        for cat in menu:
            filas += f'<h4 class="cat">{E(cat["categoria"])}</h4>'
            for it in cat["items"]:
                n, desc = it[0], (it[1] if len(it) > 1 else "")
                precio = it[2] if len(it) > 2 and it[2] else ""
                pr = f'<span class="pr">{E(precio)}</span>' if precio else ""
                dd = f"<p>{E(desc)}</p>" if desc else ""
                filas += f'<div class="item"><div><h3>{E(n)}</h3>{dd}</div>{pr}</div>'
        nota = d.get("nota_menu") or ("Una selección de nuestros servicios. Pregunta por precios y disponibilidad al agendar." if cita else "Una selección de nuestra carta. Pregunta por los platillos del día al reservar.")
        cuerpo_menu = filas + f'<p class="note">{E(nota)}</p>'
    else:
        txt = d.get("sin_menu_texto") or ("Escríbenos y te mandamos la lista de servicios y precios." if cita else "Escríbenos y te mandamos el menú completo del día.")
        cuerpo_menu = f'<p class="lead">{E(txt)}</p>'

    quotes = "".join(f'<div class="quote"><p>“{E(r[0])}”</p><span>{E(r[1] if len(r) > 1 else "Reseña en Google")}</span></div>' for r in d["resenas"][:3])
    rows = "".join(f'<div class="row"><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in d["horario"])
    hor_pie = "".join(f"<li>{E(a)} · {E(b)}</li>" for a, b in d["horario"])
    strip = "".join(f'<figure><img src="{E(s)}" alt="{E(nombre)}" loading="lazy"></figure>' for s in galeria)
    rating, nres = d["rating"], d["num_resenas"]
    meta2 = d.get("meta2") or ["", ""]
    meta2_html = f'<div><b>{E(meta2[0])}</b>{E(meta2[1])}</div>' if meta2[0] else ""
    colonia = d.get("colonia", "")
    titulo = d.get("titulo") or f"{nombre} · {d.get('eyebrow', '')}".strip(" ·")
    ig = d.get("instagram", "").strip()
    ig_li = f'<li><a href="{E(ig)}" target="_blank" rel="noopener">Instagram</a></li>' if ig.startswith("https://") else ""

    css = f"""
:root{{--hero:{hero};--foot:{ink_bg_footer};--cream:{cream};--paper:{paper};--ink:{ink};--muted:{muted};--acc:{acc};--accl:{acc_l};--eyeb:{eyeb};--line:rgba(0,0,0,.12)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font:400 16px/1.6 Manrope,system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}img{{display:block;width:100%;height:100%;object-fit:cover;background:#ddd}}
.w{{max-width:1180px;margin:0 auto;padding:0 24px}}
.serif{{font-family:'{fam}',Georgia,serif;font-weight:500;letter-spacing:-.01em}}
.demo{{background:#111;color:#eee;font-size:12px;text-align:center;padding:7px 12px;letter-spacing:.02em}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase}}
.btn{{display:inline-flex;align-items:center;justify-content:center;height:50px;padding:0 28px;border-radius:999px;font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;border:1.5px solid currentColor;text-align:center}}
.btn.fill{{background:var(--acc);border-color:var(--acc);color:#fff}}
nav{{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--line)}}
nav .w{{display:flex;align-items:center;justify-content:space-between;height:72px;gap:16px}}
.logo{{font-family:'{fam}',serif;font-size:30px;font-weight:700;font-style:italic;color:var(--acc);line-height:1}}
.links{{display:flex;align-items:center;gap:32px;font-size:14px;color:var(--muted)}}
.links .btn{{height:42px;padding:0 22px;font-size:12px}}
.hero{{background:var(--hero);color:var(--cream)}}
.hero .w{{display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center;padding-top:80px;padding-bottom:80px}}
.hero .eyebrow{{color:var(--eyeb);margin-bottom:22px}}
.hero h1{{font-size:clamp(42px,5.6vw,72px);line-height:1.03;margin-bottom:24px}}
.hero p{{font-size:17px;opacity:.85;max-width:450px;margin-bottom:36px}}
.cta{{display:flex;gap:12px;flex-wrap:wrap}}
.hero .btn.line{{color:var(--cream)}}
.hero figure{{border-radius:28px;overflow:hidden;aspect-ratio:4/5}}
.meta{{display:flex;gap:28px;margin-top:40px;padding-top:28px;border-top:1px solid rgba(255,255,255,.18);font-size:14px;opacity:.9}}
.meta b{{display:block;font-family:'{fam}',serif;font-size:30px;font-weight:600;line-height:1.1}}
section{{padding:110px 0}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center}}
.split figure{{border-radius:28px;overflow:hidden;aspect-ratio:4/3}}
.split .eyebrow{{color:var(--acc);margin-bottom:18px}}
h2{{font-size:clamp(34px,4.2vw,54px);line-height:1.06;margin-bottom:22px}}
.lead{{color:var(--muted);font-size:17px;max-width:470px;margin-bottom:30px}}
.menu{{background:var(--cream)}}
.menu .grid{{display:grid;grid-template-columns:.9fr 1.1fr;gap:72px;align-items:start}}
.menu figure{{border-radius:28px;overflow:hidden;aspect-ratio:4/5;position:sticky;top:110px}}
.item{{display:flex;justify-content:space-between;gap:24px;padding:22px 0;border-bottom:1px solid var(--line)}}
.item h3{{font-family:'{fam}',serif;font-size:24px;font-weight:600;line-height:1.15;margin-bottom:4px}}
.item p{{color:var(--muted);font-size:15px}}
.item .pr{{font-weight:700;white-space:nowrap;padding-top:4px}}
.cat{{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--acc);margin:34px 0 4px}}.cat:first-of-type{{margin-top:8px}}
.menu .note{{margin-top:28px;font-size:14px;color:var(--muted)}}
.band{{background:var(--acc);color:#fff;padding:96px 0}}
.band .eyebrow{{opacity:.85;margin-bottom:28px;text-align:center}}
.quotes{{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}}
.quote{{border-top:1px solid rgba(255,255,255,.35);padding-top:24px}}
.quote p{{font-family:'{fam}',serif;font-size:24px;line-height:1.28;font-weight:500;margin-bottom:18px}}
.quote span{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.85}}
.score{{text-align:center;margin-top:56px;font-size:15px;opacity:.9}}
.score b{{font-family:'{fam}',serif;font-size:44px;font-weight:600;display:block;line-height:1}}
.visit .rows{{margin:8px 0 30px}}
.visit .row{{display:grid;grid-template-columns:150px 1fr;gap:16px;padding:16px 0;border-bottom:1px solid var(--line);font-size:15px}}
.visit .row dt{{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--acc);padding-top:3px}}
.visit .row a{{border-bottom:1px solid var(--acc)}}
.visit figure{{aspect-ratio:4/5;border-radius:28px;overflow:hidden}}
footer{{background:var(--foot);color:rgba(255,255,255,.75);padding:72px 0 40px}}
footer .eyebrow{{color:var(--eyeb);margin-bottom:22px}}
.strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:64px}}
.strip figure{{border-radius:18px;overflow:hidden;aspect-ratio:1}}
.cols{{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:40px;font-size:14px}}
.cols .logo{{font-size:46px;margin-bottom:16px;color:var(--accl)}}
.cols h4{{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--eyeb);margin-bottom:14px}}
.cols li{{list-style:none;margin-bottom:8px}}
.legal{{margin-top:56px;padding-top:24px;border-top:1px solid rgba(255,255,255,.12);font-size:12px;opacity:.6;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
.mbar{{display:none}}
@media(max-width:860px){{
 .links a:not(.btn){{display:none}}
 .hero .w{{grid-template-columns:1fr;gap:36px;padding-top:44px;padding-bottom:56px}}
 .hero figure{{aspect-ratio:4/4.4;order:-1;border-radius:22px}}
 .split,.menu .grid{{grid-template-columns:1fr;gap:36px}}
 .menu figure{{position:static;aspect-ratio:4/3.4}}
 section{{padding:72px 0}}.band{{padding:72px 0}}
 .quotes{{grid-template-columns:1fr;gap:22px}}
 .strip{{grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:44px}}
 .cols{{grid-template-columns:1fr 1fr;gap:28px}}.cols>div:first-child{{grid-column:1/-1}}
 .visit .row{{grid-template-columns:110px 1fr}}
 .visit figure{{order:-1;aspect-ratio:4/3}}
 body{{padding-bottom:76px}}
 .mbar{{display:flex;gap:10px;position:fixed;left:0;right:0;bottom:0;padding:12px 16px calc(12px + env(safe-area-inset-bottom));background:var(--paper);border-top:1px solid var(--line);z-index:6}}
 .mbar .btn{{flex:1;height:48px;padding:0 12px}}
}}"""

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{E(titulo)}</title>
<meta name="description" content="{E(d['intro'])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={gf}&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="demo">MUESTRA DE DISEÑO PARA {E(nombre.upper())} · Preparada por Matteo · No es el sitio oficial del negocio</div>
<nav><div class="w"><a href="#" class="logo">{E(logo)}</a><div class="links"><a href="#menu">{'Servicios' if cita else 'Menú'}</a><a href="#nosotros">Nosotros</a><a href="#visitanos">Visítanos</a><a class="btn fill" href="{E(accion)}"{tgt}>{E(verbo_corto)}</a></div></div></nav>
<header class="hero"><div class="w"><div>
<p class="eyebrow">{E(d.get('eyebrow', ''))}</p>
<h1 class="serif">{E(d['h1'])}</h1>
<p>{E(d['intro'])}</p>
<div class="cta"><a class="btn line" href="#menu">{'Ver servicios' if cita else 'Ver menú'}</a><a class="btn fill" href="{E(accion)}"{tgt}>{E(verbo)}</a></div>
<div class="meta"><div><b>{E(rating)} ★</b>{E(nres)} reseñas en Google</div>{meta2_html}</div>
</div><figure><img src="{E(HERO)}" alt="{E(nombre)}"></figure></div></header>
<section id="nosotros"><div class="w split"><figure><img src="{E(LADO)}" alt="{E(nombre)}" loading="lazy"></figure><div>
<p class="eyebrow">{E(d.get('nosotros_eyebrow', 'Nosotros'))}</p><h2 class="serif">{E(d.get('nosotros_titulo', nombre))}</h2>
<p class="lead">{E(d.get('nosotros_texto', d['intro']))}</p>
<a class="btn" style="color:var(--acc)" href="#menu">{'Ver servicios' if cita else 'Ver la carta'}</a></div></div></section>
<section class="menu" id="menu"><div class="w grid"><figure><img src="{E(CARTA)}" alt="{E(nombre)}" loading="lazy"></figure><div>
<p class="eyebrow" style="color:var(--acc);margin-bottom:18px">{eyebrow_menu}</p><h2 class="serif">{seccion_menu}</h2>
{cuerpo_menu}
<div class="cta" style="margin-top:30px"><a class="btn fill" href="{E(accion)}"{tgt}>{E(verbo)}</a></div></div></div></section>
<div class="band"><div class="w"><p class="eyebrow">Lo que dicen nuestros clientes</p><div class="quotes">{quotes}</div>
<div class="score"><b>{E(rating)} de 5</b>con {E(nres)} reseñas en Google</div></div></div>
<section class="visit" id="visitanos"><div class="w split"><div>
<p class="eyebrow">Visítanos</p><h2 class="serif">{E(d.get('visita_titulo', 'Te esperamos' + (' en la ' + colonia if colonia else '') + '.'))}</h2>
<dl class="rows">{rows}<div class="row"><dt>Dirección</dt><dd>{E(d['direccion'])} · <a href="{E(maps)}" target="_blank" rel="noopener">Abrir en Google Maps</a></dd></div><div class="row"><dt>Teléfono</dt><dd><a href="{tel_href}">{E(tel)}</a></dd></div></dl>
<div class="cta"><a class="btn fill" href="{E(accion)}"{tgt}>{E(accion_txt)}</a><a class="btn" style="color:var(--ink)" href="{E(maps)}" target="_blank" rel="noopener">Cómo llegar</a></div>
</div><figure><img src="{E(VISITA)}" alt="{E(nombre)}" loading="lazy"></figure></div></section>
<footer><div class="w"><p class="eyebrow">Galería</p><div class="strip">{strip}</div>
<div class="cols"><div><div class="logo">{E(logo)}</div><p>{E(d['direccion'])}</p></div>
<div><h4>Horario</h4><ul>{hor_pie}</ul></div>
<div><h4>Visita</h4><ul><li><a href="#menu">{'Servicios' if cita else 'Menú'}</a></li><li><a href="#nosotros">Nosotros</a></li><li><a href="{E(maps)}" target="_blank" rel="noopener">Cómo llegar</a></li>{ig_li}</ul></div>
<div><h4>{'Citas' if cita else 'Reservas'}</h4><ul><li><a href="{E(accion)}"{tgt}>{'WhatsApp' if wa else 'Llamar'}</a></li><li><a href="{tel_href}">{E(tel)}</a></li></ul></div></div>
<div class="legal"><span>© 2026 {E(nombre)}</span><span>Muestra de diseño · Fotos y reseñas de Google</span></div></div></footer>
<div class="mbar"><a class="btn" href="#menu" style="color:var(--ink)">{'Servicios' if cita else 'Ver menú'}</a><a class="btn fill" href="{E(accion)}"{tgt}>{E(verbo_corto)}</a></div>
</body></html>"""


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = construir(data)
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta = os.path.join(raiz, data["slug"])
    os.makedirs(carpeta, exist_ok=True)
    open(os.path.join(carpeta, "index.html"), "w", encoding="utf-8").write(out)
    print("OK", data["slug"], f"{len(out)//1024} KB", f"https://muestras-web-ay2.pages.dev/{data['slug']}/")
