# Combate cuerpo a cuerpo

Referencia del núcleo que utiliza el motor. Las modificaciones situadas al
final de `trollheim.pdf` tienen prioridad sobre el texto anterior.

## Secuencia del duelo

1. En la primera ronda ataca antes quien carga.
2. Si ambos tienen la misma prioridad, se compara la Iniciativa.
3. Las reglas `Ataca primero` y `Ataca último` alteran ese orden.
4. Cada ataque tira para impactar, herir, salvar y, si se pierde la última
   Herida, determina el estado del defensor.

**Fuente:** `trollheim.pdf`, pp. 34-37 y 167. **Estado:** implementado.

## Tirada para impactar

Se compara HA del atacante contra HA del defensor:

| Relación | Resultado necesario |
|---|---:|
| HA atacante mayor | 3+ |
| HA defensora mayor que el doble de la atacante | 5+ |
| Resto | 4+ |
| Defensor con HA 0 | 2+ |

**Fuente:** `trollheim.pdf`, pp. 35 y 167. **Estado:** implementado.

## Combatir con dos armas

Un arma de una mano en cada mano concede un ataque adicional. Cada ataque usa
las reglas del arma con la que se realiza. Las armas a dos manos, los pares de
armas indivisibles y otras armas marcadas como incompatibles anulan la mano
secundaria.

**Fuente:** `trollheim.pdf`, p. 35. **Estado:** implementado para el catálogo
actual.

## Tirada para herir

| Fuerza respecto a Resistencia | Resultado necesario |
|---|---:|
| F >= R + 2 | 2+ |
| F = R + 1 | 3+ |
| F = R | 4+ |
| F = R - 1 | 5+ |
| F entre R - 2 y R - 3 | 6+ |
| F <= R - 4 | Imposible |

**Fuente:** `trollheim.pdf`, pp. 31-32 y 167. **Estado:** implementado.

## Armadura y penetración

| Protección | Salvación base |
|---|---:|
| Armadura ligera | 6+ |
| Armadura pesada | 5+ |
| Armadura de gromril | 4+ |
| Escudo | mejora la salvación en 1 |

La Fuerza 4 o superior empeora la salvación en `F - 3`. Algunas armas y
materiales añaden penetración adicional.

**Fuente:** `trollheim.pdf`, pp. 32, 50 y 167. **Estado:** implementado para
las protecciones incluidas; véase el catálogo de ausencias.

## Impactos críticos

Un 6 natural para herir produce crítico si no era necesario un 6 para herir.
Solo puede causarse un crítico por combatiente y fase.

| 1D6 | Efecto |
|---|---|
| 1-2 | Dos heridas; permite armadura. |
| 3-4 | Dos heridas; ignora armadura. |
| 5-6 | Dos heridas; ignora armadura y +2 a la tirada de Heridas. |

**Fuente:** `trollheim.pdf`, pp. 32 y 167. **Estado:** implementado. Las tablas
opcionales de críticos por tipo de arma de la p. 161 no se usan: el reglamento
básico presenta la tabla general y el simulador conserva ese modelo.

## Tabla de Heridas y recuperación

| 1D6 al perder la última Herida | Estado |
|---|---|
| 1-2 | Derribado |
| 3-4 | Aturdido |
| 5-6 | Fuera de combate |

Un aturdido pasa a derribado y después se levanta. Quien se levanta ataca
último esa ronda. Un enemigo aturdido queda fuera de combate al ser atacado;
un derribado recibe impactos automáticos y queda fuera si sufre una herida no
salvada. No se puede derribar y rematar con los ataques restantes del mismo
combatiente en la misma fase.

**Fuente:** `trollheim.pdf`, pp. 33 y 37. **Estado:** implementado.

## Parada

Se tira 1D6 y debe superarse el mayor resultado de impacto del atacante; un 6
enemigo no se puede parar. Solo se detiene un impacto. No se pueden parar
ataques con Fuerza igual o superior al doble de la Fuerza básica del defensor.
Espada más rodela permite repetir la parada; dos espadas no.

**Fuente:** `trollheim.pdf`, pp. 36-37 y 51. **Estado:** parcial. Las armas con
parada están modeladas, pero la rodela no existe y algunas armas que conceden
doble parada solo reciben una segunda parada aproximada.

## Modificaciones prioritarias del reglamento

- `Reflejos Felinos`: al recibir una carga obtiene `Ataca primero`; el orden
  contra quienes también atacan primero se decide por Iniciativa.
- `En Pie de un Salto`: ignora Derribado salvo cuando lo causa una salvación de
  casco o la regla `Sin dolor`.
- Las correcciones de campaña, disparo y reclutamiento no afectan al duelo.

**Fuente:** `trollheim.pdf`, p. 179. **Estado:** implementado.
