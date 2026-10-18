"""Perfiles por idioma para generar el mismo video en varios idiomas.

Cada perfil define: el codigo de idioma que se le pasa al LLM (``video_language``),
la voz neuronal de Edge TTS (gratuita, sin API key) por genero y la fuente que
cubre los glifos del idioma para los subtitulos.

Las voces fueron verificadas contra ``app/services/data/azure_voices.json``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Fuentes incluidas en resource/fonts. BeVietnamPro cubre latin extendido
# (tildes, n con tilde, cedilla, vietnamita); STHeitiMedium cubre CJK.
FONT_LATIN = "BeVietnamPro-Bold.ttf"
FONT_CJK = "STHeitiMedium.ttc"


@dataclass(frozen=True)
class LanguageProfile:
    code: str  # codigo corto usado en CLI: es, en, pt...
    name: str  # nombre legible
    video_language: str  # locale que se envia al LLM
    voice_female: str
    voice_male: str
    font: str = FONT_LATIN
    # True si las fuentes incluidas no cubren la escritura (arabe, hindi, tailandes).
    needs_extra_font: bool = False

    def voice(self, gender: str = "female") -> str:
        gender = (gender or "female").strip().lower()
        if gender not in ("female", "male"):
            raise ValueError(f"gender must be 'female' or 'male', got {gender!r}")
        base = self.voice_female if gender == "female" else self.voice_male
        # El formato interno de la app es "<voz>-Female" / "<voz>-Male".
        return f"{base}-{gender.capitalize()}"


_PROFILES = [
    LanguageProfile("es", "Espanol", "es-EC", "es-EC-AndreaNeural", "es-EC-LuisNeural"),
    LanguageProfile("es-mx", "Espanol (Mexico)", "es-MX", "es-MX-DaliaNeural", "es-MX-JorgeNeural"),
    LanguageProfile("es-es", "Espanol (Espana)", "es-ES", "es-ES-ElviraNeural", "es-ES-AlvaroNeural"),
    LanguageProfile("en", "English", "en-US", "en-US-JennyNeural", "en-US-GuyNeural"),
    LanguageProfile("pt", "Portugues (Brasil)", "pt-BR", "pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"),
    LanguageProfile("fr", "Francais", "fr-FR", "fr-FR-DeniseNeural", "fr-FR-HenriNeural"),
    LanguageProfile("de", "Deutsch", "de-DE", "de-DE-KatjaNeural", "de-DE-ConradNeural"),
    LanguageProfile("it", "Italiano", "it-IT", "it-IT-ElsaNeural", "it-IT-DiegoNeural"),
    LanguageProfile("nl", "Nederlands", "nl-NL", "nl-NL-ColetteNeural", "nl-NL-MaartenNeural"),
    LanguageProfile("pl", "Polski", "pl-PL", "pl-PL-ZofiaNeural", "pl-PL-MarekNeural"),
    LanguageProfile("ru", "Russkiy", "ru-RU", "ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"),
    LanguageProfile("tr", "Turkce", "tr-TR", "tr-TR-EmelNeural", "tr-TR-AhmetNeural"),
    LanguageProfile("id", "Bahasa Indonesia", "id-ID", "id-ID-GadisNeural", "id-ID-ArdiNeural"),
    LanguageProfile("vi", "Tieng Viet", "vi-VN", "vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"),
    LanguageProfile("ja", "Nihongo", "ja-JP", "ja-JP-NanamiNeural", "ja-JP-KeitaNeural", FONT_CJK),
    LanguageProfile("ko", "Hangugeo", "ko-KR", "ko-KR-SunHiNeural", "ko-KR-InJoonNeural", FONT_CJK),
    LanguageProfile("zh", "Zhongwen", "zh-CN", "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", FONT_CJK),
    LanguageProfile("ar", "Arabic", "ar-SA", "ar-SA-ZariyahNeural", "ar-SA-HamedNeural", FONT_LATIN, True),
    LanguageProfile("hi", "Hindi", "hi-IN", "hi-IN-SwaraNeural", "hi-IN-MadhurNeural", FONT_LATIN, True),
    LanguageProfile("th", "Thai", "th-TH", "th-TH-PremwadeeNeural", "th-TH-NiwatNeural", FONT_LATIN, True),
]

PROFILES: dict[str, LanguageProfile] = {p.code: p for p in _PROFILES}

# Idiomas recomendados para empezar: tienen fuente incluida y voz verificada.
DEFAULT_LANGUAGES = ("es", "en", "pt", "fr")


def get_profile(code: str) -> LanguageProfile:
    key = (code or "").strip().lower().replace("_", "-")
    if key not in PROFILES:
        raise KeyError(
            f"idioma no soportado: {code!r}. Disponibles: {', '.join(sorted(PROFILES))}"
        )
    return PROFILES[key]


def parse_language_list(value: Optional[str]) -> list[LanguageProfile]:
    """'es,en,pt' -> lista de perfiles, sin duplicados y respetando el orden."""
    codes = [c for c in (value or "").split(",") if c.strip()] or list(DEFAULT_LANGUAGES)
    seen: set[str] = set()
    profiles: list[LanguageProfile] = []
    for code in codes:
        profile = get_profile(code)
        if profile.code not in seen:
            seen.add(profile.code)
            profiles.append(profile)
    return profiles
