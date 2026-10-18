#!/usr/bin/env python3
"""Crea y deja lista config.toml para generar videos multi-idioma.

Es idempotente: se puede ejecutar varias veces. Las claves de API NO se escriben
en el codigo; se leen de variables de entorno (o se pueden pegar luego en la
interfaz web, seccion de configuracion):

  LLM_PROVIDER   openai | gemini | deepseek | moonshot | anthropic | qwen ...
  LLM_API_KEY    clave del proveedor de texto (genera guiones y terminos)
  LLM_MODEL      (opcional) nombre del modelo
  PEXELS_API_KEY clave gratuita de https://www.pexels.com/api/

Ejemplo:
  LLM_PROVIDER=openai LLM_API_KEY=sk-... PEXELS_API_KEY=... python configure.py
"""

from __future__ import annotations

import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.join(ROOT, "config.example.toml")
TARGET = os.path.join(ROOT, "config.toml")

# Valores por defecto: espanol (Ecuador), voz gratuita de Edge TTS, 9:16.
UI_DEFAULTS = {
    "language": "es",
    "video_language": "es-EC",
    "tts_server": "azure-tts-v1",
    "voice_name": "es-EC-AndreaNeural-Female",
    "voice_mode": "tts",
    "font_name": "BeVietnamPro-Bold.ttf",
    "font_size": 60,
    "subtitle_enabled": True,
    "video_aspect_pexels": "9:16",
}


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def set_line(text: str, key: str, value) -> str:
    """Reemplaza `key = ...` (sin comentar) por el valor nuevo; lo anade si no existe."""
    pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)
    line = f"{key} = {_toml_value(value)}"
    if pattern.search(text):
        return pattern.sub(lambda _m: line, text, count=1)
    raise KeyError(key)


def main() -> int:
    if not os.path.isfile(EXAMPLE):
        print(f"No encuentro {EXAMPLE}", file=sys.stderr)
        return 1
    if not os.path.isfile(TARGET):
        shutil.copyfile(EXAMPLE, TARGET)
        print("config.toml creado desde config.example.toml")

    with open(TARGET, encoding="utf-8") as handle:
        text = handle.read()

    # Solo escucha en local por seguridad (la API no tiene clave por defecto).
    text = set_line(text, "listen_host", "127.0.0.1")
    text = set_line(text, "video_source", "pexels")

    provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
    llm_key = os.environ.get("LLM_API_KEY", "").strip()
    llm_model = os.environ.get("LLM_MODEL", "").strip()
    pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()

    if provider:
        try:
            text = set_line(text, "llm_provider", provider)
            if llm_key:
                text = set_line(text, f"{provider}_api_key", llm_key)
            if llm_model:
                text = set_line(text, f"{provider}_model_name", llm_model)
        except KeyError as exc:
            print(f"Proveedor LLM no reconocido en la plantilla: {exc}", file=sys.stderr)
            return 1
    if pexels_key:
        text = re.sub(
            r"^pexels_api_keys\s*=.*$",
            lambda _m: f'pexels_api_keys = ["{pexels_key}"]',
            text,
            count=1,
            flags=re.MULTILINE,
        )

    # [ui] es la ultima seccion: se anaden o actualizan sus claves al final.
    for key, value in UI_DEFAULTS.items():
        active = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)
        line = f"{key} = {_toml_value(value)}"
        if active.search(text):
            text = active.sub(lambda _m: line, text, count=1)
        else:
            text = text.rstrip("\n") + "\n" + line + "\n"

    with open(TARGET, "w", encoding="utf-8") as handle:
        handle.write(text)

    cfg = {}
    try:
        import toml  # noqa: WPS433

        cfg = toml.load(TARGET)
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO: no pude releer config.toml para validar: {exc}", file=sys.stderr)
        return 1

    app = cfg.get("app", {})
    prov = app.get("llm_provider", "")
    print("config.toml listo.")
    print(f"  Proveedor LLM : {prov or '(sin definir)'}")
    print(f"  Clave LLM     : {'OK' if app.get(prov + '_api_key') else 'FALTA'}")
    print(f"  Clave Pexels  : {'OK' if app.get('pexels_api_keys') else 'FALTA'}")
    print(f"  Idioma/voz    : {cfg['ui']['video_language']} / {cfg['ui']['voice_name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
