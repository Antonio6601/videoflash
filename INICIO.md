# Inicio rápido: videos multi-idioma

## 1. Instalar (una sola vez)
```bash
uv sync                      # dependencias
sudo apt install ffmpeg      # o: brew install ffmpeg
```

## 2. Configurar claves (no se guardan en el código)
```bash
LLM_PROVIDER=openai LLM_API_KEY=sk-... PEXELS_API_KEY=... python configure.py
```
- `LLM_PROVIDER`: openai, gemini, deepseek, moonshot, anthropic, qwen...
- Pexels es gratis: https://www.pexels.com/api/
- También puedes pegar las claves después en la interfaz web (Configuración).
- Valores por defecto: español (Ecuador), voz Andrea (Edge TTS, gratis), formato 9:16.

## 3. Usar

**Interfaz web:** `./webui.sh` → http://127.0.0.1:8501

**Mismo video en varios idiomas (línea de comandos):**
```bash
# Guion generado por el LLM en cada idioma
python multilang.py --subject "Cómo recuperar el abdomen después del parto" --languages es,en,pt,fr

# Guiones propios (sin LLM; ideal para textos comerciales exactos)
python multilang.py --script es=guion_es.txt --script en=guion_en.txt

# Varios temas (uno por línea) en varios idiomas
python multilang.py --subjects-file temas.txt --languages es,en

# Solo ver el plan, sin generar
python multilang.py --subject "Tema" --dry-run
```
Opciones útiles: `--voice-gender male`, `--aspect 16:9`, `--paragraphs 3`.
Cualquier otra opción se pasa a `cli.py` (ej. `--stop-at script`).

Los videos quedan en `storage/tasks/<id>/`.

## Idiomas
es, es-mx, es-es, en, pt (Brasil), fr, de, it, nl, pl, ru, tr, id, vi, ja, ko, zh.
Árabe (ar), hindi (hi) y tailandés (th) están definidos pero necesitan una fuente
Noto en `resource/fonts` para que los subtítulos se vean bien.

## Requisitos de red
Edge TTS (voz), Pexels y el proveedor LLM necesitan acceso a internet.
