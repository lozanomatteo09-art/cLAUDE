# Generador de muestras

1. Crear `gen/data/<slug>.json` (ver `gen/data/santino-polanco.json` como ejemplo).
2. `python3 gen/build.py gen/data/<slug>.json` → escribe `<slug>/index.html`.
   Si sale "NO PASA CALIDAD", no se publica ese negocio.
3. `git add -A && git commit && git push` → Cloudflare Pages publica en
   `https://muestras-web-ay2.pages.dev/<slug>/` en 1–3 minutos.

Campos obligatorios: slug, nombre, tipo ("comida" | "cita"), h1, intro, direccion,
telefono, maps_url, rating, num_resenas, fotos (≥5 URLs https), resenas (≥3 textos
reales de Google), horario (lista de [días, horas]).
Opcionales: paleta (olivo, noche, vino, cacao, rosa, carbon, verde), fuente
(cormorant, fraunces, dmserif, playfair), logo_texto, eyebrow, colonia, meta2,
nosotros_eyebrow/titulo/texto, menu ([{categoria, items:[[nombre, descripción, precio?]]}]),
sin_menu_texto, nota_menu, whatsapp (solo si está publicado por el negocio), instagram.
Nada inventado: ni reseñas, ni precios, ni WhatsApp.
