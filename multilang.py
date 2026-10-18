#!/usr/bin/env python3
"""Genera el mismo video en varios idiomas con una sola orden.

Construye un manifiesto por lotes (JSONL) con la voz y la fuente correctas para
cada idioma y lo ejecuta con el modo ``--batch-file`` de ``cli.py``.

Ejemplos:
  # Mismo tema en espanol, ingles, portugues y frances (guion generado por el LLM)
  uv run python multilang.py --subject "Como recuperar el abdomen despues del parto"

  # Idiomas y genero de voz a eleccion
  uv run python multilang.py --subject "5 habitos para dormir mejor" \\
      --languages es,en,pt --voice-gender male

  # Guiones propios (sin LLM): un archivo por idioma
  uv run python multilang.py --script es=guion_es.txt --script en=guion_en.txt

  # Varios temas desde un archivo (uno por linea) x todos los idiomas
  uv run python multilang.py --subjects-file temas.txt --languages es,en

  # Solo ver el plan sin generar nada
  uv run python multilang.py --subject "Tema" --dry-run

Los argumentos que no reconoce este script se pasan tal cual a cli.py
(por ejemplo --video-aspect 16:9 o --stop-at script).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.multilang import (  # noqa: E402
    DEFAULT_LANGUAGES,
    PROFILES,
    get_profile,
    parse_language_list,
)

MAX_BATCH = 100


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read().strip()


def _parse_script_args(values: list[str]) -> dict[str, str]:
    scripts: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"--script espera idioma=archivo, recibido: {item!r}")
        code, path = item.split("=", 1)
        code = get_profile(code).code
        if not os.path.isfile(path):
            raise SystemExit(f"no existe el archivo de guion: {path}")
        text = _read_text(path)
        if not text:
            raise SystemExit(f"el archivo de guion esta vacio: {path}")
        scripts[code] = text
    return scripts


def build_entries(args: argparse.Namespace) -> list[dict]:
    entries: list[dict] = []

    def base(profile) -> dict:
        entry = {
            "video_language": profile.video_language,
            "voice_name": profile.voice(args.voice_gender),
            "font_name": profile.font,
            "paragraph_number": args.paragraphs,
        }
        if args.aspect:
            entry["video_aspect"] = args.aspect
        return entry

    scripts = _parse_script_args(args.script or [])
    for code, text in scripts.items():
        profile = get_profile(code)
        entries.append({**base(profile), "video_script": text})

    subjects = list(args.subject or [])
    if args.subjects_file:
        subjects += [
            line.strip()
            for line in _read_text(args.subjects_file).splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    if subjects:
        for subject in subjects:
            for profile in parse_language_list(args.languages):
                if profile.code in scripts and len(subjects) == 1:
                    continue  # ya hay guion propio para ese idioma
                entries.append({**base(profile), "video_subject": subject})

    if not entries:
        raise SystemExit("indica --subject, --subjects-file o --script")
    if len(entries) > MAX_BATCH:
        raise SystemExit(f"{len(entries)} tareas superan el limite de {MAX_BATCH} por lote")
    return entries


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--subject", action="append", help="tema del video (repetible)")
    parser.add_argument("--subjects-file", help="archivo con un tema por linea")
    parser.add_argument(
        "--script",
        action="append",
        help="guion propio por idioma: es=archivo.txt (repetible)",
    )
    parser.add_argument(
        "--languages",
        default=",".join(DEFAULT_LANGUAGES),
        help=f"codigos separados por coma. Disponibles: {', '.join(sorted(PROFILES))}",
    )
    parser.add_argument("--voice-gender", choices=("female", "male"), default="female")
    parser.add_argument("--paragraphs", type=int, default=1, help="parrafos del guion (1-10)")
    parser.add_argument("--aspect", choices=("9:16", "16:9", "1:1"), default="9:16")
    parser.add_argument("--out-dir", default=os.path.join(ROOT, "storage", "multilang"))
    parser.add_argument("--dry-run", action="store_true", help="solo escribe el manifiesto")
    return parser.parse_known_args(argv)


def main(argv: list[str] | None = None) -> int:
    args, passthrough = parse_args(sys.argv[1:] if argv is None else argv)
    entries = build_entries(args)

    for profile in parse_language_list(args.languages):
        if profile.needs_extra_font:
            print(
                f"AVISO: {profile.name} necesita una fuente con su escritura; las fuentes "
                "incluidas no la cubren y los subtitulos saldran con cuadros. Copia una "
                "fuente Noto a resource/fonts y ajusta app/services/multilang.py.",
                file=sys.stderr,
            )

    os.makedirs(args.out_dir, exist_ok=True)
    manifest = os.path.join(args.out_dir, time.strftime("manifest-%Y%m%d-%H%M%S.jsonl"))
    with open(manifest, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Plan: {len(entries)} video(s)")
    for entry in entries:
        what = entry.get("video_subject") or (entry.get("video_script", "")[:50] + "...")
        print(f"  [{entry['video_language']}] {entry['voice_name']}  <-  {what}")
    print(f"Manifiesto: {manifest}")

    if args.dry_run:
        return 0

    command = [sys.executable, os.path.join(ROOT, "cli.py"), "--batch-file", manifest, *passthrough]
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
