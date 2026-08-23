# Estado del simulador

Este es el único documento dedicado al estado, las decisiones de modelado y el
trabajo pendiente. Las reglas y los datos canónicos viven en
`sources/knowledge`; no deben duplicarse aquí.

## Alcance

El programa simula mediante Monte Carlo duelos cuerpo a cuerpo uno contra uno.
Los combatientes empiezan trabados, se sortea cuál de ellos cargó y se resuelven
ataques, heridas, salvaciones, críticos, estados y recuperación. Los combates que
siguen sin resolverse tras 50 turnos no participan en el porcentaje final.

Están cubiertos:

- las modificaciones finales de Trollheim aplicables al duelo;
- armas generales y exclusivas con efecto directo;
- armaduras, protecciones, materiales, drogas, venenos y consumibles;
- habilidades visibles en el simulador;
- rivales configurables y perfiles aleatorios ponderados con equipo legal.

Quedan fuera de alcance el movimiento, terreno, combates múltiples, psicología,
magia, plegarias, campaña y cualquier efecto que necesite decisiones ajenas al
duelo representado.

## Decisiones de modelado

- El Báculo de Serpiente usa siempre su ataque especial.
- `Barrido` se activa automáticamente cuando su expectativa supera a los
  ataques normales.
- La Bola con Kadena conserva sus efectos de combate, pero no su movimiento
  incontrolable ni las colisiones con el escenario.
- La pica se simula con ambos guerreros ya en contacto; no se presupone la
  ventaja opcional de atacar desde 8 cm.
- Los perfiles y pesos aleatorios son representativos. No pretenden reconstruir
  una banda completa ni un presupuesto real.
- El equipo aleatorio favorece moderadamente las opciones baratas y comunes.

## Pendiente

- Incorporar al motor las mecánicas de las habilidades especiales de banda que
  ya expone el selector contextual del candidato. Se conservan en la ficha y
  en el Excel, pero no deben considerarse cubiertas estadísticamente hasta que
  tengan resolución y pruebas propias.

- `Desarmar`: necesita elegir el arma afectada y representar su recuperación.
- `Estocada Mortal`: requiere decidir cuándo sustituye ventajosamente los
  ataques normales.
- `Pugilista`: necesita representar expresamente el combate desarmado.
- Permitir elegir por ronda entre los ataques normales y el ataque especial del
  Báculo de Serpiente.
- Sustituir progresivamente los perfiles representativos por filtros basados en
  las bandas de la base canónica.

## Rendimiento

- El motor NumPy procesa los combates en bloques de 100.000 para limitar los
  picos de memoria y repartir mejor el trabajo.
- Los lotes de configuraciones se entregan a los procesos en grupos de dos para
  evitar que un trabajador se quede con media eternidad mientras los demás
  contemplan el vacío.
- Las configuraciones que producen exactamente la misma ficha efectiva se
  calculan una sola vez. Sus filas comparten el resultado porque no existe
  ninguna diferencia mecánica que pudiera justificar otra simulación.
- El kernel Cython acelera los duelos con armas y reglas sencillas. Si una ficha
  usa habilidades, venenos, materiales u otra mecánica no cubierta, se deriva
  al motor NumPy completo sin alterar la simulación.
- El kernel compilado se incluye dentro del ejecutable portable; no impone
  dependencias al usuario final.

## Verificación

Ejecutar antes de preparar una distribución:

```powershell
python -m pytest -q
python tools\validate_knowledge_base.py
python tools\benchmark_native_kernel.py -n 500000
```

El ejecutable portable solo se regenera cuando se prepara una nueva versión.
