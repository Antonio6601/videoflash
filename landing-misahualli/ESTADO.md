# Landing terreno vía a Misahuallí — estado del proyecto

Última actualización: 2026-10-18

## Qué es
Landing page de venta de un terreno en la vía a Misahuallí (Napo, Ecuador).
Público: inversionistas, gerentes de empresas, emprendedores y accionistas.
Secciones: hero con titular y CTA, tres beneficios con iconos, testimonios, formulario de contacto, pie legal.

## Dónde está
- Página publicada (privada, solo el dueño la abre hasta que la comparta): https://claude.ai/artifact/BF88sjQZHfjsXK6nGtB5s3
- Código fuente: `project/Main.dc.html` (la página) y `project/canvas.json` (índice del lienzo), en esta carpeta.

## Decisiones de diseño
- Paleta: verde claro amazonía como fondo (`#E3F2D8`, secciones `#D2E8C3`, tarjetas `#F4FAEE`), texto verde bosque (`#10331F`), acento amarillo oro (`#EBB000`, editable en la pestaña de ajustes), pie en verde selva (`#0F3B24`).
- Tipografías: Bricolage Grotesque (títulos) y DM Sans (texto).
- El oro se usa en botones, iconos y pie. Los textos pequeños dorados usan `#7A5A00` para que se lean sobre fondo claro.
- Formulario: al enviarlo abre WhatsApp (+593 96 155 5587) con el mensaje armado. No guarda los contactos en ninguna base de datos.

## Pendiente (datos que faltan)
- [ ] Superficie real del terreno (hoy `[X] hectáreas`)
- [ ] Precio de referencia (hoy `[$ XX] / m²`)
- [ ] Distancia real a Tena (hoy `[X] km a Tena`)
- [ ] Testimonios reales (hoy 3 tarjetas marcadas "Ejemplo · reemplazar por uno real")
- [ ] Fotos del terreno y mapa de ubicación
- [ ] Confirmar con el municipio de Tena los usos de suelo permitidos antes de publicar los textos de "potencial de desarrollo"
- [ ] Decidir si el formulario debe guardar los contactos (base de datos) además de abrir WhatsApp
- [ ] Compartir la página desde su menú Share cuando esté lista

## Cómo continuar
Abre una sesión nueva con Claude y pide: "Continúa la landing del terreno en la vía a Misahuallí". Pasa los datos pendientes de arriba. Si la página publicada ya no está disponible, se puede recrear desde `project/Main.dc.html`.

## Otros proyectos relacionados (misma cuenta de GitHub)
- Fork de MoneyPrinterTurbo con generador de videos multi-idioma: https://github.com/Antonio6601/MoneyPrinterTurbo-antonio (rama `multilang-es-setup`).
- Copia completa del proyecto de video en este repositorio: rama `multilang-es-setup` de `videoflash` (ver `INICIO.md` allí).
- Las claves de API nunca se guardan en el repositorio: van en `config.toml`, que git ignora.
