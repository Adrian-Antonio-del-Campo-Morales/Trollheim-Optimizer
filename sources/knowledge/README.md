# Base de conocimiento de Trollheim

Esta carpeta es la referencia canónica y consultable del proyecto. Contiene los
datos necesarios para revisar reglas, equipo y bandas sin volver a procesar los
PDF en el trabajo normal.

## Contenido

- `bands/`: 34 bandas con 222 perfiles. Cada ficha incluye cupos, coste,
  atributos, experiencia, listas de equipo, restricciones, acceso a habilidades
  y reglas completas de banda y de perfil.
- `catalog/combat-rules.yaml`: resolución general del combate y modificaciones
  prioritarias del reglamento de Trollheim.
- `catalog/weapons.yaml`: armas generales y exclusivas con sus reglas.
- `catalog/armour-and-equipment.yaml`: armaduras, protecciones, materiales y
  objetos de equipo con efecto en combate.
- `catalog/consumables.yaml`: drogas, hongos y venenos.
- `catalog/skills.yaml`: habilidades generales no ligadas a una única banda.
  Las habilidades propias de una banda están en la ficha de esa banda.
- `catalog/market-prices.yaml`: comercio general y de Lustria.
- `catalog/market-prices-khemri.yaml`: tabla comercial completa de Khemri.
- `corpus/`: volcado íntegro de los cuatro manuales recortados, separado por
  página. Es material de respaldo y búsqueda, no sustituye a los datos
  canónicos.
- `index/manifest.json`: inventario de manuales y páginas conservadas.
- `schema/`: contratos JSON Schema para los registros canónicos.

## Alcance

La capa canónica cubre reglas generales de combate, perfiles, bandas, armas,
armaduras, equipo, consumibles, costes, restricciones y habilidades. También
registra quién tiene acceso a plegarias, saberes o magia y cualquier limitación
para utilizarlos.

Por decisión de proyecto, no se incluyen las listas ni los efectos concretos de
plegarias, hechizos, saberes de magia, sermones o equivalentes. Es la única
exclusión deliberada de esta versión.

## Fuentes y citas

Los manuales de `sources/short` fueron la fuente principal. Los de
`sources/full` se reservan para contrastar una cifra ilegible o una
inconsistencia real.

Las citas canónicas usan el número impreso en el pie de página. Ese número se
mantiene tanto en el manual recortado como en el completo, aunque la página
física del PDF sea distinta.

## Consulta y validación

Para buscar una regla o un guerrero, `rg` recorre directamente las fichas y el
corpus sin mantener una segunda copia del texto:

```powershell
rg -n -i "regla o guerrero" sources\knowledge
```

Para comprobar sintaxis, referencias internas, perfiles y marcadores obsoletos:

```powershell
python tools\validate_knowledge_base.py
```

La base canónica y los volcados se mantienen como documentación versionada. El
validador es deliberadamente de solo lectura: no genera ni modifica fichas.
