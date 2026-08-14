# Trollheim Simulator

Simulador Monte Carlo para comparar configuraciones y mejoras de guerreros de
Trollheim. La interfaz está hecha con Tkinter y el motor Monte Carlo procesa
los combates por lotes vectorizados con NumPy.

## Estado del proyecto

La aplicación está en desarrollo y se centra exclusivamente en duelos cuerpo a
cuerpo. Los resultados son estimaciones Monte Carlo: sirven para comparar
opciones, no para sustituir al árbitro ni al inevitable amigo que recuerda una
regla distinta cada jueves.

## Estructura

- `src/trollheim_simulator/rules.py`: perfiles, equipo, habilidades y constantes.
- `src/trollheim_simulator/enemies.py`: perfiles de rival, dificultad, frecuencia y equipo legal.
- `src/trollheim_simulator/engine.py`: preparación y simulación de combates.
- `src/trollheim_simulator/ui.py`: interfaz gráfica y presentación de resultados.
- `src/trollheim_simulator/app.py`: arranque y gestión de errores.
- `Trollheim_Simulator.py`: lanzador directo para arrancar la aplicación.
- `tests/`: pruebas rápidas del catálogo y las reglas fundamentales.
- `sources/text/`: referencia temática de las reglas que afectan al simulador.

## Consultar los manuales

Los PDF originales siguen siendo la referencia. En el entorno de desarrollo,
`sources/text` contiene una versión curada y mucho más manejable sobre combate,
armas, protecciones, equipo y habilidades. Cada entrada mantiene el manual y la
página física del PDF:

```powershell
rg -n -i "texto a buscar" sources\text
```

El índice y el estado de cobertura están en `sources/text/README.md` y
`sources/text/cobertura-simulador.md`.

La cobertura ampliada aún tiene armas y protecciones pendientes o aproximadas.
La lista detallada está en
[`sources/text/cobertura-simulador.md`](sources/text/cobertura-simulador.md);
conviene consultarla antes de interpretar como definitiva una combinación
exótica de equipo.

Los PDF y sus volcados completos se conservan localmente, pero están excluidos
de Git. Son material de consulta de terceros, ocupan más de 200 MB y no forman
parte de la distribución del simulador. Para reproducir la documentación local,
copia tus propios manuales en `sources/` sin añadirlos al repositorio.

## Rivales aleatorios

La muestra aleatoria se construye con perfiles representativos de las bandas de
los manuales incluidos en `sources`. Los perfiles están agrupados por dificultad
baja, media y alta. Su peso combina cuántas listas de banda los incluyen y el
cupo habitual permitido; una tropa sin límite aparece más que un monstruo 0-1.

En cada combate se escoge una variante de equipo legal para el perfil. El coste
y la rareza reducen moderadamente la probabilidad de los objetos caros o raros,
sin hacerlos desaparecer. El selector de nivel aplica una mejora aleatoria y
efectiva por cada nivel indicado.

Cada mano muestra desplegables separados para `Armas generales`, `Armas
especiales` y material. Las dos listas de armas son mutuamente excluyentes y el
material es opcional e independiente para cada mano.

Los objetos opcionales se comparan en la pestaña `Equipamiento`, separada de la
ficha base y de las mejoras de nivel. La tabla incluye tanto cada objeto por sí
solo como todas las parejas legales de armaduras, casco, amuleto, preparativos y
venenos. Cuando una pareja contiene dos venenos, se aplican respectivamente al
arma principal y a la secundaria.

Todas las pestañas de comparación (`Mejoras`, `Combos mejoras`, `Equipamiento`
y `Configuraciones de armas`) permiten alternar entre `Por equipo` y `Óptima`.
La primera conserva una columna para cada configuración de manos; la segunda
muestra sólo el mejor resultado visible y el equipo con el que se obtuvo. Una
estrella señala la mejor opción de cada fila. Los cuadros de configuración
permiten mostrar u ocultar modos y también determinan qué opciones participan
en la vista óptima.

El desplegable `Objetos incluidos` permite excluir objetos antes de simular; así
se ocultan sus resultados, sus parejas y también se ahorra el cálculo asociado.
El selector `Máximo de objetos`, con valor inicial 3, permite calcular sólo
objetos individuales o ampliar la tabla con todas las parejas y tríos legales,
conservando también los resultados de menor tamaño.

Las tablas mantienen visibles las barras de desplazamiento vertical y
horizontal para dejar claro cuándo quedan resultados o columnas fuera del área
disponible.

Los preparativos incluyen los Hongos Sombrero Loco y Pirakabezas. Ambos aplican
Furia Asesina durante el duelo: duplican el atributo de Ataques hasta que el
guerrero queda derribado o aturdido.

La pestaña `Configuraciones de Armas` compara armas solas, con escudo, parejas
legales y armas que ocupan ambas manos. Una checklist permite limitar el
catálogo usado; inicialmente sólo están marcadas las armas generales más
comunes. Sus cuatro cuadros de configuración también permiten mostrar u ocultar
grupos de resultados.

El Amuleto de la Suerte ya no aparece como mejora de nivel ni como casilla de la
ficha. Se evalúa junto al resto de objetos en esta comparativa específica.

En la pestaña de enemigos sólo se eligen los grupos de dificultad Baja, Media y
Alta. Los perfiles concretos y sus frecuencias permanecen dentro de cada grupo.
El nivel del rival es común a los modos aleatorio y configurable, y sus mejoras
se sortean de nuevo para cada combate.

El editor presenta ambas manos en paralelo, los accesorios en una sola fila y
las habilidades en una cuadrícula compacta para que la ficha completa sea
visible también en la pestaña de enemigo.

La pestaña de mejoras parte de 100.000 simulaciones; combos, equipamiento y
configuraciones de armas parten de 10.000. Cada comparativa tiene su propio
campo para cambiar esa cantidad.

El motor no usa Numba ni realiza calentamiento o compilación al arrancar. Cada
lote conserva tiradas aleatorias independientes, pero agrupa los combates con
el mismo perfil para resolverlos mediante operaciones vectorizadas.

## Ejecutar en desarrollo

Abre una terminal en la carpeta del proyecto e instala las dependencias la
primera vez:

```powershell
python -m pip install -r requirements.txt
```

Después puedes ejecutar la aplicación directamente con:

```powershell
python Trollheim_Simulator.py
```

El lanzador añade automáticamente la carpeta `src` a la ruta de Python, así que
no hace falta configurar `PYTHONPATH`.

Como alternativa, también puedes arrancar el paquete sin usar el lanzador:

```powershell
$env:PYTHONPATH = "src"
python -m trollheim_simulator
```

Otra opción es instalar el proyecto en modo editable:

```powershell
python -m pip install -e .
trollheim
```

## Crear el ejecutable

Ejecuta `build_Trollheim_ONEFILE.bat`. El resultado se guarda en
`dist\Trollheim.exe`.

El script necesita Python 3.10 o posterior, NumPy, Tkinter y PyInstaller. Las
dependencias de desarrollo se instalan con:

```powershell
python -m pip install -r requirements-dev.txt
```

Los ejecutables generados tampoco se guardan en Git. Es preferible adjuntarlos
a una versión de GitHub Releases para no convertir el historial en un vertedero
de binarios.

## Pruebas

```powershell
python -m pytest -q
```

## Licencia

Todavía no se ha elegido una licencia para el código. Antes de publicar el
repositorio, añade un fichero `LICENSE` con la licencia que prefieras. Los
manuales, nombres y demás material de Trollheim/Mordheim pertenecen a sus
respectivos titulares y no quedan cubiertos por esa licencia.
