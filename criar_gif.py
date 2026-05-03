#!/usr/bin/env python3
"""
criar_gif.py — Captura frames do demo-animacao.html e monta GIF animado.
Roda com:  py criar_gif.py
Gera:      demo-catalogo.gif  (na mesma pasta)
"""

import asyncio, math, http.server, threading, time
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image
import io

# ── Configuração ──────────────────────────────────────────────────
VIEWPORT_W   = 360          # largura do "celular"
VIEWPORT_H   = 760          # altura do "celular"
DURATION_S   = 12           # quantos segundos gravar (1 loop completo)
FPS          = 5            # frames por segundo → 250 ms / frame
GIF_OUT      = Path("demo-catalogo.gif")
PORT         = 8765
ROOT_DIR     = Path(__file__).parent
# ──────────────────────────────────────────────────────────────────


def start_server():
    """Sobe um servidor HTTP estático na pasta do projeto."""
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *_: None   # silencia logs
    httpd = http.server.HTTPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


async def capture_frames():
    url    = f"http://127.0.0.1:{PORT}/demo-animacao.html"
    n      = math.ceil(DURATION_S * FPS)
    delay  = 1000 // FPS        # ms entre frames (playwright usa ms)
    frames = []

    print(f"Abrindo {url} …")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx     = await browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,              # retina → imagem mais nítida
        )
        page = await ctx.new_page()
        await page.goto(url, wait_until="networkidle")

        # aguarda a animação iniciar (100 ms)
        await page.wait_for_timeout(100)

        print(f"Capturando {n} frames a {FPS} fps …")
        for i in range(n):
            png  = await page.screenshot(full_page=False)
            img  = Image.open(io.BytesIO(png)).convert("RGBA")
            # reduz para metade (device_scale_factor=2 duplicou)
            img  = img.resize((VIEWPORT_W, VIEWPORT_H), Image.LANCZOS)
            frames.append(img)
            if (i + 1) % 5 == 0:
                print(f"  {i+1}/{n}")
            await page.wait_for_timeout(delay)

        await browser.close()

    return frames


def save_gif(frames):
    print(f"Montando GIF com {len(frames)} frames …")
    duration_ms = 1000 // FPS

    # converte para modo P (paleta) para GIF menor
    pal_frames = []
    for f in frames:
        bg = Image.new("RGBA", f.size, (255, 255, 255, 255))
        bg.paste(f, mask=f.split()[3])
        pal_frames.append(bg.convert("RGB").quantize(colors=256, method=Image.Quantize.FASTOCTREE))

    pal_frames[0].save(
        GIF_OUT,
        format="GIF",
        save_all=True,
        append_images=pal_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )
    size_mb = GIF_OUT.stat().st_size / 1_048_576
    print(f"\nGIF salvo: {GIF_OUT}  ({size_mb:.1f} MB)  {len(frames)} frames")


async def main():
    import os
    os.chdir(ROOT_DIR)          # garante que o servidor sirva da pasta certa
    srv = start_server()
    time.sleep(0.3)             # deixa o servidor subir
    try:
        frames = await capture_frames()
        save_gif(frames)
    finally:
        srv.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
