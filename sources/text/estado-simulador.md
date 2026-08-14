# Estado del simulador

Este es el único documento de `sources/text` que describe la implementación.
Las demás fichas son una referencia neutral de reglas y los cuatro volcados
completos conservan el texto extraído de los manuales.

## Alcance actual

El programa compara mediante simulación Monte Carlo duelos cuerpo a cuerpo uno
contra uno. Ambos combatientes empiezan trabados y se resuelven ataques,
heridas, salvaciones, críticos, estados y recuperación hasta que uno queda fuera
de combate o se alcanza el límite de 50 turnos. Los duelos no resueltos no
participan en el porcentaje final.

Al empezar cada duelo se sortea con la misma probabilidad cuál de los dos
guerreros ha cargado. El resultado se decide de forma independiente para cada
caso, incluso cuando todos pertenecen al mismo lote de simulación.

La aplicación contiene simulaciones de mejoras individuales, combinaciones de
mejoras, equipamiento, armas, un rival configurable y muestras ponderadas de
rivales aleatorios.

## Cobertura

| Área | Estado actual |
|---|---|
| Impactar, herir, armadura, críticos y estados | Cubierto |
| Modificaciones finales de Trollheim aplicables al duelo | Cubiertas |
| Armas generales y exclusivas con efecto directo | Cubiertas |
| Protecciones con efecto directo | Cubiertas |
| Drogas, venenos y consumibles seleccionables | Cubiertos |
| Habilidades disponibles en los selectores | Cubiertas |
| Habilidades generales adicionales de decisión táctica | Pendientes |
| Movimiento, terreno, psicología, magia y campaña | Fuera de alcance |

El catálogo actual tiene 58 armas, 27 opciones de mano secundaria y 12
protecciones. Las pruebas comprueban que no haya entradas visibles sin código
de motor.

## Mecánicas destacadas ya representadas

- Pistolas en cuerpo a cuerpo sólo durante la primera ronda, incluida la
  precisión de la Pistola de Duelo.
- Bonificaciones por cargar y por recibir una carga aplicadas al combatiente
  correspondiente según el sorteo inicial de cada duelo.
- Paradas, repeticiones por rodela, dobles intentos y contraataque del Alfanje.
- Hoja Trampa del Rompe Espadas y sustitución del arma rota.
- Fuego persistente de la Vara Brasero y vulnerabilidad de la Armadura
  Kitinoza.
- Enredo del Garrapato Encadenado y Entorpecer Arma del Kusara Kama.
- Restallido y bloqueo de parada de los látigos, incluidas configuraciones con
  dos látigos sin duplicar el restallido.
- Ataques especiales del Báculo de Serpiente, Daga de Ponzoña e Incensario.
- Inmunidad infecciosa de los perfiles aleatorios no muertos y poseídos.
- Bola con Kadena con Hongos Pirakabezas obligatorios, 1D3 heridas, protección
  anulada y penalizador para impactar a su portador.
- `Barrido`, utilizado sólo cuando su esperanza de impactos supera la de los
  ataques normales.
- Restricciones legales de manos y protecciones, incluido `Versátil` del
  Guantelete con Pincho.

## Decisiones de modelado

- El ataque especial del Báculo de Serpiente se considera su forma de combatir;
  no se elige entre el ataque especial y los ataques normales en cada ronda.
- `Barrido` es opcional en el manual. Se activa automáticamente cuando resulta
  favorable para evitar que una mejora perjudique al combatiente por usarla a
  ciegas.
- La Bola con Kadena conserva su perfil ofensivo y defensivo, pero no su
  movimiento incontrolable ni las colisiones con miniaturas, edificios o
  escenografía.
- Los nombres de protecciones equivalentes permanecen separados para que los
  resultados indiquen qué objeto se ha comparado.
- `Obsidiana`, `Acero Oscuro` e `Incansable` son adaptaciones o expansiones, no
  reglas generales del manual básico. La procedencia exacta de `Incansable`
  sigue pendiente de vincular a una página concreta; actualmente mantiene en
  rondas posteriores la bonificación temporal de Fuerza de las armas pesadas.
- Los duelos aleatorios usan perfiles representativos y pesos derivados de las
  listas de banda, no probabilidades oficiales publicadas.
- La selección aleatoria de equipo favorece moderadamente las opciones baratas
  y comunes; no intenta reconstruir bandas completas ni presupuestos reales.
- Los rivales aleatorios no muertos y poseídos no reciben preparativos que sus
  reglas raciales les impiden utilizar.

## Pendiente

### Habilidades generales

- `Desarmar`: requiere elegir qué arma se inutiliza y modelar su recuperación.
- `Estocada Mortal`: sustituye los ataques por uno de F+2 que ataca último;
  falta decidir automáticamente cuándo compensa usarla.
- `Pugilista`: exige representar de forma explícita el combate desarmado.

### Mejoras posibles del modelo

- Permitir elegir por ronda entre los ataques normales y el ataque especial del
  Báculo de Serpiente.
- Incorporar etiquetas raciales al rival configurable para aplicar inmunidades
  que actualmente sólo conocen los perfiles aleatorios.
- Revisar los pesos de aparición y las listas legales cuando se añadan nuevas
  bandas o manuales.
- Añadir pruebas estadísticas específicas para cada efecto persistente; las
  pruebas actuales cubren catálogo, perfiles y regresiones deterministas.

## Fuera de alcance

- Alcance, movimiento, interceptación, terreno, edificios y direcciones.
- Armas montadas y reglas que requieren una montura.
- Combates contra varios adversarios, aliados o blancos adyacentes.
- Psicología, miedo, odio y chequeos de liderazgo sin efecto directo en las
  heridas del duelo.
- Magia, plegarias y objetos activables que requieren decisiones tácticas.
- Experiencia, comercio, adicción, heridas permanentes y efectos pospartida.
- Bonificaciones contra una especie concreta cuando el rival configurable no
  dispone de esa etiqueta, como el Pinchagarrapatos contra Garrapatos.

## Verificación

- 68 pruebas automatizadas superadas en la última revisión.
- Barrido de ejecución superado para todas las armas, manos secundarias y
  protecciones disponibles.
- Referencias contrastadas con `trollheim.pdf`, `khemri.pdf`, `lustria.pdf` y
  `caos-en-las-calles.pdf`.

Este recuento debe actualizarse cuando cambien las pruebas o los catálogos. El
ejecutable portable no se regenera con cada cambio de código; se construye sólo
cuando se prepara una nueva distribución.
