# Habilidades relevantes

El selector de nivel del simulador usa mejoras generales elegibles al subir de
nivel. Las habilidades específicas de banda se inventarían un árbol distinto
para cada perfil y quedan fuera del selector, pero se anotan en la auditoría si
su efecto revela una mecánica ausente.

## Implementadas

| Habilidad | Regla resumida | Fuente |
|---|---|---|
| Combatiente Experto | +1 a las tiradas para herir en cuerpo a cuerpo. | `trollheim.pdf`, p. 122 |
| A Fondo | +1 a la tirada de efecto del impacto crítico. | `trollheim.pdf`, p. 122 |
| Experto en Esgrima | Repite fallos para impactar con espadas al cargar. | `trollheim.pdf`, p. 122 |
| Echarse a un Lado | Salvación especial 5+ tras la armadura contra heridas cuerpo a cuerpo. | `trollheim.pdf`, p. 122 |
| Golpe Poderoso | +1 Fuerza en cuerpo a cuerpo. | `trollheim.pdf`, p. 123 |
| Curtido | Resta 1 a la Fuerza de impactos cuerpo a cuerpo recibidos, sin alterar su penetración original. | `trollheim.pdf`, p. 123 |
| Fortachón | Las armas a dos manos dejan de atacar últimas. | `trollheim.pdf`, p. 123 |
| Carga Imparable | +1 HA al cargar. | `trollheim.pdf`, p. 123 |
| Reflejos Felinos | Al recibir carga, ataca primero y desempata por Iniciativa. | `trollheim.pdf`, pp. 123 y 179 |
| En Pie de un Salto | Ignora Derribado salvo las excepciones corregidas. | `trollheim.pdf`, pp. 123 y 179 |
| Maestro del Hacha | Permite parar con hachas normales. | `caos-en-las-calles.pdf`, p. 189 |
| Experto en Hachas | Repite fallos para impactar con hachas al cargar. | `caos-en-las-calles.pdf`, p. 189 |
| Golpe con el Escudo | Con escudo obtiene un ataque adicional con +1 a la salvación enemiga. | `khemri.pdf`, p. 95 |

`Experto en Esgrima` también admite cimitarra por la modificación de Khemri
(`khemri.pdf`, p. 94); el motor ya incluye cimitarra y gran cimitarra.

## Implementada como extensión del simulador

| Habilidad | Regla usada | Observación |
|---|---|---|
| Incansable | Mantiene en rondas posteriores la Fuerza temporal de armas pesadas. | Aparece como nombre/regla en material de banda, no como mejora general claramente localizada. Conviene conservarla separada de las habilidades básicas. |

## Relevantes y ausentes

| Habilidad | Efecto relevante | Fuente | Motivo |
|---|---|---|---|
| Desarmar | Renuncia a ataques para inutilizar un arma enemiga hasta que pueda recuperarse. | `caos-en-las-calles.pdf`, p. 189 | Requiere seleccionar arma y modelar recuperación; ausente. |
| Estocada Mortal | Sustituye todos los ataques por uno con +2 F que ataca último. | `caos-en-las-calles.pdf`, p. 189 | Decisión táctica por ronda; ausente. |
| Pugilista | Mejora el combate sin armas y añade ataque. | `caos-en-las-calles.pdf`, p. 189 | El simulador no ofrece puños como equipo normal. |
| Barrido | Cambia todos los ataques por un impacto automático si el rival falla un chequeo de I; requiere arma a dos manos. | `caos-en-las-calles.pdf`, p. 189 | Afecta incluso a un duelo uno contra uno; ausente. |
| Luchador de Pozo | +1 HA y +1 A dentro de edificios o ruinas. | `trollheim.pdf`, p. 123 | Depende del terreno; fuera del duelo abstracto. |
| Maestro en Combate | Bonificaciones al combatir contra varios enemigos. | `trollheim.pdf`, p. 122 | El simulador es uno contra uno. |
| Agilidad élfica | Salvación especial 6+ contra ataques; mejora combinada con Echarse a un Lado. | `lustria.pdf`, pp. 65 y 80 | Habilidad específica de banda; ausente del perfil aleatorio. |
| Ignorar el dolor | Aturdido se trata como Derribado. | `lustria.pdf`, p. 80 | Habilidad específica de banda; ausente del perfil aleatorio. |
| Fintar | Al recibir una carga enfrenta Iniciativa y puede evitar el contacto. | `khemri.pdf`, p. 95 | Depende del movimiento previo al duelo; no está modelada. |

## Fuera de alcance deliberadamente

Entrenamiento extensivo solo cambia qué equipo puede comprarse; las habilidades
de disparo, magia, comercio, exploración, movimiento, monturas, psicología o
varios oponentes no cambian el duelo abstracto actual y no se incluyen en el
selector.
