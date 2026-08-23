# Trollheim Optimizer

Simulador Monte Carlo para comparar guerreros, mejoras, armas y equipo en
combates cuerpo a cuerpo de Trollheim.

El programa calcula estimaciones estadísticas. No sustituye al reglamento, al
árbitro ni al colega que recuerda una regla distinta cada jueves.

## Descargar y usar la versión portable

La versión portable es la opción más sencilla para Windows: consiste en un
único archivo y no necesita instalación, Python ni compilación.

[Descargar Trollheim Optimizer Portable 4.2.0](https://github.com/Adrian-Antonio-del-Campo-Morales/Trollheim-Optimizer/releases/download/v4.2.0/Trollheim-Optimizer-Portable-4.2.0.exe)

Para utilizarla:

1. Descarga `Trollheim-Optimizer-Portable-4.2.0.exe`.
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
- Vistas por configuración de manos o por resultado óptimo.
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

### Guardar candidatos

En la pestaña **Candidato** puedes escribir un nombre y, opcionalmente,
seleccionar una banda y un tipo de guerrero. Al elegir un perfil, se cargan sus
atributos y solo quedan disponibles las armas, protecciones y categorías de
habilidades válidas que el simulador puede representar.

**Guardar libro…** crea un `.xlsx` legible y reutilizable. Las hojas
`Candidato` y `Enemigos` conservan la ficha principal, todos los rivales
manuales y la configuración de la muestra aleatoria; el resto del libro queda
preparado para añadir resultados. **Cargar libro…** recupera todo ese estado.

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
