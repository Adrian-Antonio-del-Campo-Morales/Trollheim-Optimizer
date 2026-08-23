# Trollheim Optimizer

Simulador Monte Carlo para comparar guerreros, mejoras, armas y equipo en
combates cuerpo a cuerpo de Trollheim.

El programa calcula estimaciones estadísticas. No sustituye al reglamento, al
árbitro ni al colega que recuerda una regla distinta cada jueves.

## Descargar y usar la versión portable

La versión portable es la opción más sencilla para Windows: consiste en un
único archivo y no necesita instalación, Python ni compilación.

[Descargar Trollheim Optimizer Portable 5.0.1](https://github.com/Adrian-Antonio-del-Campo-Morales/Trollheim-Optimizer/releases/download/v5.0.1/Trollheim-Optimizer-Portable-5.0.1.exe)

Para utilizarla:

1. Descarga `Trollheim-Optimizer-Portable-5.0.1.exe`.
2. Guarda el archivo donde quieras, por ejemplo en el escritorio o en una
   memoria USB.
3. Haz doble clic sobre él para abrir el simulador.

El ejecutable puede moverse o borrarse sin desinstalar nada. Para buscar una
versión más reciente, consulta la página de
[Releases](https://github.com/Adrian-Antonio-del-Campo-Morales/Trollheim-Optimizer/releases/latest).

Windows puede mostrar una advertencia de SmartScreen porque el archivo todavía
no está firmado digitalmente. Comprueba que lo descargaste desde este
repositorio antes de ejecutarlo.

## Funciones principales

- Configuración del candidato y de un rival personalizado.
- Selección libre o filtrada por banda y tipo de guerrero canónico.
- Guardado y carga de candidatos en libros Excel preparados para incorporar resultados.
- Rivales aleatorios ponderados por perfil, dificultad y equipo legal.
- Comparación de mejoras individuales y combinaciones de mejoras.
- Comparación de armas, armaduras, objetos y consumibles.
- Resultados óptimos de configuraciones de armas con coste e Índice MOTTA.
- Número de simulaciones configurable en cada análisis.

El alcance, las decisiones de modelado y el trabajo pendiente se mantienen en
[`PROJECT_STATUS.md`](PROJECT_STATUS.md).

## Ejecutar desde el código fuente

Necesitas Python 3.10 o posterior. Desde la carpeta del proyecto:

```powershell
python -m pip install -r requirements.txt
python Trollheim_Simulator.py
```

También puedes instalar el proyecto en modo editable:

```powershell
python -m pip install -e .
trollheim
```

### Guardar y cargar libros de simulación

En la pestaña **Candidato** puedes escribir un nombre y, opcionalmente,
seleccionar una banda y un tipo de guerrero. Al elegir un perfil, se cargan sus
atributos y solo quedan disponibles las armas, protecciones y categorías de
habilidades válidas que el simulador puede representar.

**Guardar** crea un `.xlsx` legible y reutilizable. Las hojas `Candidato` y
`Enemigos` conservan la ficha principal, todos los rivales manuales y la
configuración de la muestra aleatoria. Cada análisis calculado se guarda en su
propia hoja. **Cargar** recupera todo ese estado y los resultados. **Cargar
Candidato** y **Cargar Enemigos** permiten reemplazar solamente esa parte del
libro; la segunda opción activa automáticamente el rival configurable.

### Índice MOTTA

La pestaña **Configuraciones de Armas** calcula la eficiencia económica de cada
configuración mediante:

```text
                      O_m × mejora
Índice MOTTA = ──────────────────────────────
                     √(coste² + 0,01²)
O_m = 507,4
```

`mejora` es la diferencia en puntos porcentuales de victoria respecto al equipo
actual exacto del candidato. `coste` es el gasto pendiente para adquirir la
configuración: no incluye las piezas que el candidato ya lleva y descuenta la
daga normal gratuita con la que empieza todo guerrero.

El término `0,01` regulariza el denominador sin separar el coste cero mediante
un caso especial. Una mejora gratuita obtiene así un valor positivo muy alto;
un empeoramiento gratuito obtiene el mismo comportamiento con signo negativo;
y una mejora nula produce un índice cero. Para costes habituales, el resultado
es prácticamente igual a `507,4 × mejora / coste`.

## Versión congelada por equipo

La versión **5.0.1** es la última versión estable del modelo «por equipo»: cada
análisis compara por separado arma con mano libre, arma con escudo, dos armas y
arma a dos manos. Queda identificada por la etiqueta Git `v5.0.1` antes de los
cambios funcionales mayores de las versiones siguientes.

## Desarrollo

El código está organizado de la siguiente manera:

- `src/trollheim_simulator/rules.py`: perfiles, equipo y habilidades.
- `src/trollheim_simulator/enemies.py`: rivales y equipo legal.
- `src/trollheim_simulator/engine.py`: motor de simulación.
- `src/trollheim_simulator/ui.py`: interfaz gráfica.
- `sources/knowledge/`: reglas, bandas, perfiles y catálogos canónicos.
- `PROJECT_STATUS.md`: alcance, decisiones de modelado y trabajo pendiente.
- `tests/`: pruebas automáticas del motor y del catálogo.

Para instalar las herramientas de desarrollo y ejecutar las pruebas:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

El motor dispone de un kernel Cython para los combates que no usan reglas
especiales. Es opcional al ejecutar el código fuente: si no está compilado, el
programa utiliza automáticamente el motor NumPy. Para compilarlo en Windows se
necesitan Visual C++ Build Tools y el Windows SDK:

```powershell
.\build_NATIVE_KERNEL.bat
python tools\benchmark_native_kernel.py -n 500000
```

## Generar los ejecutables

`build_Trollheim_ONEFILE.bat` genera la versión portable en
`dist\Trollheim.exe`. El propio script compila e incluye el kernel nativo; el
usuario final sigue recibiendo un solo archivo y no necesita instalar nada.

`build_Trollheim_INSTALLER.bat` genera el ejecutable y un instalador tradicional
de Windows. Para compilar el instalador también hace falta
[Inno Setup](https://jrsoftware.org/isdl.php):

```powershell
winget install --id JRSoftware.InnoSetup.7 -e -s winget -i
.\build_Trollheim_INSTALLER.bat
```

El instalador resultante se guarda en `dist\installer`. Los binarios generados
están excluidos de Git y deben publicarse como archivos de GitHub Releases.

## Manuales y cobertura

Los PDF originales no se distribuyen en el repositorio. La documentación
estructurada de `sources/knowledge` permite consultar y validar las reglas sin
depender de ellos durante el desarrollo normal. Los nombres y el material de
Trollheim/Mordheim pertenecen a sus respectivos titulares.

## Licencia

El proyecto todavía no tiene una licencia de código definida. Hasta que se
añada una, su publicación en GitHub no concede permiso automático para copiar,
modificar o redistribuir el código.
