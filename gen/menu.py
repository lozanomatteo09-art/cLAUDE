"""Genera <slug>/menu/index.html a partir de gen/data/<slug>.json (usa la misma paleta, fuente y logo)."""
import json, sys, os, html, importlib.util

spec = importlib.util.spec_from_file_location("build", os.path.join(os.path.dirname(__file__), "build.py"))
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
E = lambda s: html.escape(str(s), quote=True)

d = json.load(open(sys.argv[1]))
hero, foot, cream, paper, ink, muted, acc, accl, eyeb = B.PALETAS.get(d.get("paleta", "olivo"), B.PALETAS["olivo"])
fam, gf = B.FUENTES.get(d.get("fuente", "cormorant"), B.FUENTES["cormorant"])
nombre = d["nombre"]
logo_img = d.get("logo_img", "")
logo_src = "../" + logo_img if logo_img and not logo_img.startswith("http") else logo_img
fotos = [f for f in d["fotos"] if str(f).startswith("https://")]
menu = d.get("menu_completo") or d.get("menu") or []
maps = d["maps_url"]

secciones = ""
for i, cat in enumerate(menu):
    items = ""
    for it in cat["items"]:
        n, desc = it[0], (it[1] if len(it) > 1 else "")
        pr = it[2] if len(it) > 2 and it[2] else ""
        items += (f'<div class="it"><div class="top"><h3>{E(n)}</h3><span class="dots"></span>'
                  f'{f"<b>{E(pr)}</b>" if pr else ""}</div>{f"<p>{E(desc)}</p>" if desc else ""}</div>')
    nota = f'<p class="cnota">{E(cat["nota"])}</p>' if cat.get("nota") else ""
    foto = fotos[cat["foto"]] if "foto" in cat else fotos[(i + 2) % len(fotos)]
    secciones += (f'<section class="cat" id="c{i}"><div class="w g"><figure><img src="{E(foto)}" alt="{E(cat["categoria"])}" loading="lazy"></figure>'
                  f'<div><p class="eb">{E(nombre)}</p><h2>{E(cat["categoria"])}</h2>{nota}<div class="items">{items}</div></div></div></section>')
chips = "".join(f'<a href="#c{i}">{E(c["categoria"].split(" · ")[0])}</a>' for i, c in enumerate(menu))
nota_gral = d.get("nota_menu", "")
horario = " · ".join(f"{a} {b}" for a, b in d["horario"])

out = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Menú · {E(nombre)}</title><meta name="description" content="Menú de {E(nombre)}: {E(d['intro'])}">
{f'<link rel="icon" href="{E(logo_src)}">' if logo_src else ''}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={gf}&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}html{{scroll-behavior:smooth;scroll-padding-top:130px}}
body{{font-family:Manrope,system-ui,sans-serif;background:{paper};color:{ink};-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}img{{display:block;width:100%;height:100%;object-fit:cover}}
.w{{max-width:1120px;margin:0 auto;padding:0 24px}}
nav{{position:sticky;top:0;z-index:20;background:{paper}ee;backdrop-filter:blur(10px);border-bottom:1px solid rgba(0,0,0,.08)}}
nav .w{{display:flex;align-items:center;justify-content:space-between;height:72px}}
.logo{{display:flex;align-items:center;gap:12px;font-family:'{fam}',serif;font-size:26px;font-weight:700;font-style:italic;color:{acc}}}
.logo img{{width:46px;height:46px;border-radius:50%}}
.back{{font-size:14px;font-weight:600;color:{muted}}}.back:hover{{color:{acc}}}
.chips{{display:flex;gap:10px;overflow-x:auto;padding:12px 24px;max-width:1120px;margin:0 auto;scrollbar-width:none}}
.chips a{{flex:none;padding:8px 16px;border-radius:99px;border:1px solid rgba(0,0,0,.14);font-size:13px;font-weight:600}}
.chips a:hover{{background:{acc};border-color:{acc};color:#fff}}
header{{background:{hero};color:{cream};padding:80px 0 72px}}
header .eb{{color:{eyeb}}}header h1{{font-family:'{fam}',serif;font-size:clamp(46px,7vw,84px);line-height:1;margin:14px 0 18px}}
header p.l{{max-width:560px;opacity:.85;line-height:1.6}}
.eb{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;font-weight:700;color:{acc}}}
.cat{{padding:72px 0;border-bottom:1px solid rgba(0,0,0,.08)}}.cat:nth-child(even){{background:{cream}}}
.g{{display:grid;grid-template-columns:.8fr 1.2fr;gap:56px;align-items:start}}
.g figure{{border-radius:22px;overflow:hidden;aspect-ratio:4/5;position:sticky;top:150px}}
h2{{font-family:'{fam}',serif;font-size:clamp(32px,4vw,46px);line-height:1.05;margin:10px 0 18px}}
.cnota{{display:inline-block;background:{accl}33;border:1px solid {accl};padding:10px 14px;border-radius:12px;font-size:14px;margin-bottom:22px}}
.it{{padding:18px 0;border-bottom:1px dashed rgba(0,0,0,.15)}}
.top{{display:flex;align-items:baseline;gap:12px}}.top h3{{font-size:18px;font-weight:700}}
.dots{{flex:1;border-bottom:1px dotted rgba(0,0,0,.25);transform:translateY(-4px)}}.top b{{color:{acc};font-size:17px}}
.it p{{color:{muted};font-size:14.5px;line-height:1.55;margin-top:6px;max-width:560px}}
.fin{{padding:72px 0;text-align:center}}.fin p{{color:{muted};max-width:560px;margin:0 auto 26px;line-height:1.6}}
.btn{{display:inline-block;padding:15px 26px;border-radius:99px;font-weight:700;font-size:13px;letter-spacing:.08em;text-transform:uppercase;background:{acc};color:#fff}}
footer{{background:{foot};color:{cream};padding:34px 0;font-size:13px}}footer .w{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;opacity:.75}}
@media(max-width:820px){{.g{{grid-template-columns:1fr;gap:28px}}.g figure{{position:static;aspect-ratio:16/10}}header{{padding:56px 0}}.cat{{padding:52px 0}}}}
</style></head><body>
<nav><div class="w"><a href="../" class="logo">{f'<img src="{E(logo_src)}" alt="{E(nombre)}">' if logo_src else ''}<span>{E(d.get('logo_texto', nombre))}</span></a><a class="back" href="../">← Volver al inicio</a></div>
<div class="chips">{chips}</div></nav>
<header><div class="w"><p class="eb">{E(d.get('eyebrow', ''))}</p><h1>Nuestro menú</h1><p class="l">{E(d.get('menu_intro', d['intro']))}</p></div></header>
{secciones}
<section class="fin"><div class="w"><p>{E(nota_gral)}</p><p>{E(d['direccion'])} · {E(horario)}</p><a class="btn" href="{E(maps)}" target="_blank" rel="noopener">Cómo llegar</a></div></section>
<footer><div class="w"><span>© 2026 {E(nombre)}</span><span>{E(d.get('legal', ''))}</span></div></footer>
</body></html>"""
os.makedirs(os.path.join(d["slug"], "menu"), exist_ok=True)
open(os.path.join(d["slug"], "menu", "index.html"), "w").write(out)
print("OK menú", d["slug"])
