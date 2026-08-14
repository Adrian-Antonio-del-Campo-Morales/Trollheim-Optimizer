# Cobertura del simulador

Auditoría del código frente a los cuatro manuales. Se ha comprobado el catálogo
de `rules.py` y las mecánicas aplicadas en `engine.py`.

## Resumen

| Área | Resultado |
|---|---|
| Núcleo de impacto, herida, armadura y estados | Cubierto |
| Modificaciones finales de Trollheim relevantes | Cubiertas |
| Habilidades generales seleccionadas actualmente | Cubiertas, salvo decisiones/terreno excluidos |
| Armas ya visibles en la interfaz | Todas codificadas, pero hay reglas parciales |
| Catálogo completo de armas relevantes de los manuales | Incompleto |
| Consumibles de efecto directo | Cubiertos |
| Protecciones adicionales | Incompleto |

## Errores o inconsistencias actuales

- Las listas de mano principal y secundaria siguen mantenidas manualmente. Las
  opciones actuales ya tienen código válido, pero al añadir un arma nueva hay
  que declarar expresamente si puede ir en la mano secundaria.
- El Alfanje permite parar, pero no está implementado su contraataque. El ataque
  sucede durante la resolución del rival y requiere que el motor pueda devolver
  daño en ambos sentidos dentro de una misma fase.
- Los efectos que añaden ataques en manos secundarias exclusivas no pueden
  expresarse siempre con fidelidad. Por ejemplo, todavía no se ofrecen dos
  látigos o dos azotes como configuración.
- Falta la rodela, por lo que tampoco existe la repetición de parada concedida
  por espada + rodela.
- `Obsidiana`, `Acero oscuro` e `Incansable` son adaptaciones o expansiones, no
  reglas generales del manual básico; deben mantenerse identificadas como tales.

## Correcciones verificadas en esta revisión

- La lanza descarta ataques de la segunda mano, pero conserva correctamente la
  bonificación defensiva del escudo permitida por la modificación de Trollheim.
- La Espada Bruja ya tiene código de mano secundaria y aplica Parada y Corrosiva.
- El Martillo Sigmarita usa el perfil de las Hermanas de Sigmar de Trollheim:
  una mano, F+1 y Conmoción. La variante a dos manos del Protectorado es otra
  ficha y no se mezcla con ella.
- La Rebanadora permite escudo o Guantelete con Pincho, pero no otra arma;
  aplica F+1 en la primera ronda y el penalizador adicional a la armadura.
- El Azote aplica la mejora de +1 a la salvación del enemigo, incluida la
  salvación de 6+ cuando no llevaba armadura.
- La Espada de Doble Hoja intenta dos paradas, tal como dice su ficha. Las Garras
  Eshin, en cambio, repiten una parada fallida y no anulan dos impactos.

## Elementos relevantes que faltan

### Prioridad alta

- Rodela.
- Armadura de Ithilmar, cuero endurecido y armadura de placas.
- Pistola y pistola de duelo usadas en cuerpo a cuerpo: el reglamento básico
  permite un disparo por pistola en la primera ronda, con F4, penetración y las
  reglas propias del arma (`trollheim.pdf`, pp. 47-48).
- Bo (`khemri.pdf`, p. 121): dos manos, parada y ataque adicional.
- Dagas envenenadas (`khemri.pdf`, p. 78): par, +1 I y 6 para impactar hiere
  automáticamente.
- Látigo ofidio (`khemri.pdf`, reglas de Hermanas de Sangre): no puede pararse,
  ataque adicional al cargar/ser cargada y loto negro permanente.
- Látigo del Señor de las Bestias (`lustria.pdf`, p. 60): no puede pararse y
  ataque adicional al cargar/ser cargado; el miedo a animales queda fuera.
- Guantelete solar (`lustria.pdf`, p. 69): arma secundaria F4 que ignora
  armadura.
- Garra de los Ancestrales y Draich (`lustria.pdf`, pp. 69 y 60): alteran
  Fuerza, armadura, críticos, parada y Tabla de Heridas.
- Yari y Cuchillo de Muerte (`caos-en-las-calles.pdf`, p. 159).
- Daga de Ponzoña e Incensario (`lustria.pdf`, p. 76).
- `Barrido` (`caos-en-las-calles.pdf`, p. 189): habilidad general de combate
  que también tiene efecto en un duelo uno contra uno.

### Prioridad media o específica de banda

- Espada de transformación impía (`khemri.pdf`, p. 21): parada; la creación de
  muertos vivientes no afecta al duelo.
- Armas exclusivas adicionales: Bola con Cadena y cualquier artefacto cuya
  ficha completa no haya podido vincularse a una regla de duelo. El Báculo
  solar y el Bastón de mago son armas de disparo/magia; la Daga de Zakrificioz
  combate como una daga normal.
- Estilete de mercado negro: +1 ataque con -1 Fuerza
  (`caos-en-las-calles.pdf`, p. 271).
- Protecciones equivalentes o exclusivas: túnica de mago, ropajes ninja,
  ropajes de Asesino Eshin, armadura kitinoza y capa de dragón marino.

## Elementos actuales con cobertura parcial

- Vara brasero: F+1 y dos manos están; falta el efecto de fuego persistente.
- Rompe Espadas: parada está; falta Hoja Trampa.
- Mazo de Guerra: perfil ofensivo está; revisar por completo `Lento` y las
  restricciones de parada.
- Garrapato Encadenado: F3, ataca primero y no se puede parar están; falta su
  comportamiento impredecible completo.
- Pinchagarrapatos: prioridad está; faltan reglas situacionales contra
  garrapatos.
- Báculo de Serpiente: parada/dos manos y ataque especial están aproximados;
  el manual exige renunciar a los ataques normales.
- Garras Eshin: par, ataque adicional, repetición de una parada fallida y
  penetración están; faltan restricciones que no afectan directamente al duelo.
- Espadas Supurantes: par, parada y daño extra aproximan el veneno, pero el
  manual las trata como loto negro permanente.
- Kusara Kama: dos manos y penetración están; falta `Entorpecer Arma`, que puede
  reducir en 1 los ataques del rival.
- Guantelete con Pincho: parada está; falta `Versátil`, que permite combinarlo
  con armas `Difícil de usar`.
- Látigo de Acero y Azote Pirata: el ataque adicional y bloqueo de parada
  están; el Azote también concede la mejora de salvación al rival. El alcance
  no importa en un duelo ya trabado.
- `Curtido` sí está separado correctamente: reduce la Fuerza para herir, pero
  `_armour_strength` calcula la penetración con la Fuerza original.

## Fuera de alcance

- Armas exclusivamente montadas, porque no se simulan monturas.
- Alcance, movimiento, interceptación, terreno, saltos y edificios.
- Psicología, miedo, odio y furia asesina.
- Magia, plegarias y objetos activables con decisiones complejas.
- Reglas contra múltiples adversarios o que dependen de aliados.
- Efectos posteriores al combate, experiencia, comercio y creación de
  miniaturas.

## Conclusión

No todas las reglas, armas, protecciones y habilidades relevantes están
representadas. El núcleo del duelo sí lo está, pero el catálogo ampliado tiene
ausencias concretas y varias aproximaciones. Este documento es la lista de
trabajo para incorporarlas sin tener que releer los cuatro PDF.
