# Trollheim Optimizer

Simulador Monte Carlo para comparar guerreros, mejoras, armas y equipo en
combates cuerpo a cuerpo de Trollheim.

El programa calcula estimaciones estadísticas. No sustituye al reglamento, al
árbitro ni al colega que recuerda una regla distinta cada jueves.

## Descargar y usar la versión portable

La versión portable es la opción más sencilla para Windows: consiste en un
único archivo y no necesita instalación, Python ni compilación.

[Descargar Trollheim Optimizer Portable 4.1.0](https://github.com/Adrian-Antonio-del-Campo-Morales/Trollheim-Optimizer/releases/download/v4.1.0/Trollheim-Optimizer-Portable-4.1.0.exe)

Para utilizarla:

1. Descarga `Trollheim-Optimizer-Portable-4.1.0.exe`.
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
- Rivales aleatorios ponderados por perfil, dificultad y equipo legal.
- Comparación de mejoras individuales y combinaciones de mejoras.
- Comparación de armas, armaduras, objetos y consumibles.
- Vistas por configuración de manos o por resultado óptimo.
- Número de simulaciones configurable en cada análisis.

El alcance, las limitaciones, las decisiones de modelado y el trabajo pendiente
se mantienen juntos en
[`sources/text/estado-simulador.md`](sources/text/estado-simulador.md).

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

## Desarrollo

El código está organizado de la siguiente manera:

- `src/trollheim_simulator/rules.py`: perfiles, equipo y habilidades.
- `src/trollheim_simulator/enemies.py`: rivales y equipo legal.
- `src/trollheim_simulator/engine.py`: motor de simulación.
- `src/trollheim_simulator/ui.py`: interfaz gráfica.
- `sources/text/`: referencia de reglas y estado de cobertura.
- `tests/`: pruebas automáticas del motor y del catálogo.

Para instalar las herramientas de desarrollo y ejecutar las pruebas:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Generar los ejecutables

`build_Trollheim_ONEFILE.bat` genera la versión portable en
`dist\Trollheim.exe`.

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

Los PDF originales no se distribuyen en el repositorio. `sources/text` contiene
referencias breves de las reglas relevantes para el simulador y un inventario
de la cobertura actual. Los nombres y el material de Trollheim/Mordheim
pertenecen a sus respectivos titulares.

## Licencia

El proyecto todavía no tiene una licencia de código definida. Hasta que se
añada una, su publicación en GitHub no concede permiso automático para copiar,
modificar o redistribuir el código.
