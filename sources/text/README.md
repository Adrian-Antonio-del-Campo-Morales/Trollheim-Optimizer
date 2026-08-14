# Referencia de reglas del simulador

Resumen temático de las reglas que pueden alterar un duelo cuerpo a cuerpo en
el simulador. Se han eliminado trasfondo, relatos, escenarios, magia, disparo,
psicología, campaña y reglas de banda sin efecto directo sobre el duelo.

Los PDF originales siguen siendo la fuente canónica. Cada regla incluye la
página física del PDF para poder comprobar tablas o texto dudoso del OCR. Los
manuales deben aportarse por separado: no se distribuyen con el repositorio.

## Documentos

- [Combate](combate.md): secuencia, impacto, heridas, armadura y estados.
- [Armas](armas.md): catálogo cuerpo a cuerpo y reglas propias.
- [Protecciones y equipo](protecciones-y-equipo.md): armaduras, escudos,
  materiales, venenos y objetos relevantes.
- [Consumibles](consumibles.md): drogas, antídotos y venenos que se aplican
  directamente al duelo.
- [Habilidades](habilidades.md): mejoras elegibles que afectan al duelo.
- [Cobertura del simulador](cobertura-simulador.md): qué está implementado,
  qué falta y qué se ha descartado por alcance.

## Volcados completos locales

Para reglas que no entren todavía en las fichas temáticas, se conserva también
todo el texto incrustado de los manuales originales, sin aplicar OCR. Estos
ficheros están excluidos de Git junto con los PDF:

- `trollheim.md`
- `caos-en-las-calles.md`
- `khemri.md`
- `lustria.md`

Cada fichero está separado mediante encabezados `Página PDF N`, de modo que el
resultado de una búsqueda lleva directamente a la página que hay que contrastar
en el original. Los resúmenes temáticos siguen siendo la opción rápida; los
volcados completos son la red de seguridad para las reglas marcianas que puedan
aparecer más adelante en el entorno local.

## Cómo buscar

```powershell
rg -n -i "texto a buscar" sources\text
```

## Convenciones

- **Fuente:** `manual.pdf`, página PDF física.
- **Implementado:** existe una mecánica específica en el motor.
- **Parcial:** está disponible, pero falta alguna parte relevante de su regla.
- **Ausente:** la regla es pertinente para el simulador y no está representada.
- **Fuera de alcance:** requiere terreno, varios combatientes, magia,
  psicología, monturas, campaña o decisiones tácticas que el duelo actual no
  modela.

Las reglas resumidas están redactadas para consulta y programación; no son una
transcripción literal del manual.
