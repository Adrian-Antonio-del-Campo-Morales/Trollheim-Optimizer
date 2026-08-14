# Referencia de reglas de combate

Resumen temático de las reglas que pueden alterar un duelo cuerpo a cuerpo.
Se han eliminado trasfondo, relatos y otros contenidos ajenos a estas fichas.

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
- [Habilidades](habilidades.md): habilidades relacionadas con el combate.
- [Estado del simulador](estado-simulador.md): cobertura, decisiones de
  implementación, limitaciones y trabajo pendiente.

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

Las reglas resumidas son material de consulta, no una transcripción literal.
Su relación con la aplicación se documenta exclusivamente en
`estado-simulador.md`.
