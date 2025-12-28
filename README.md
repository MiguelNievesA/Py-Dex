<p align="center">
  <img width="20%" align="center" src="https://raw.githubusercontent.com/MiguelNievesA/Py-Dex/master/docs/source/static_icons/logo_app.png" alt="logo">
</p>
<h1>
  Py-Dex - Aplicación de escritorio (PyQt5)
</h1>
<p align="center">
  Una simple aplicación que te permitira explorar el mundo Pokémon. Hecha a partir de PyQt5 en Python.
</p>

<div align="center">

![GPLv2](https://img.shields.io/badge/License-GPLv2-blue%3Fcolor%3D%23FE9090?style=flat&labelColor=red&color=%23FE9090)
![Platform Win32 | Win64](https://img.shields.io/badge/Platform-Win32%20%7C%20Win64-blue?style=flat&labelColor=red&color=%23FE9090)
[![GitHub Release](https://img.shields.io/github/v/release/MiguelNievesA/Py-Dex?include_prereleases&filter=Desktop_Application)](https://github.com/MiguelNievesA/Py-Dex/releases/tag/Desktop_Application)


</div>

<p align="center">
<a href="docs/source/versions_README//README_ENGLISH.md">English</a> | <a href="">Español</a>
</p>

![Interface](https://raw.githubusercontent.com/MiguelNievesA/Py-Dex/master/docs/source/interface.png)

## 📜 Licencia del proyecto (GNU GPL v2)

Este proyecto se distribuye bajo **la licencia Pública General de GNU, versión 2** - [GPL v2](./LICENSE).

Esta te permite utilizar libremente el proyecto para cualquier propósito.

Copyright © 2025 by MiguelNievesA

## Librerías utilizadas para la UI/UX

[![PyQt Fluent Widgets](https://img.shields.io/badge/UI-PyQt--Fluent--Widgets-2C7BE5?style=flat-square&logo=qt&logoColor=white)](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
[![Custom Widgets](https://img.shields.io/badge/UI-Custom--Qt--Widgets-6C757D?style=flat-square&logo=qt&logoColor=white)](https://github.com/KhamisiKibet/QT-PyQt-PySide-Custom-Widgets)

## API utilizada para los datos de los Pokémon

<div>
  <img width="20%" align="center" src="https://raw.githubusercontent.com/MiguelNievesA/Py-Dex/master/docs/source/static_icons/pokeapi_.png" alt="logo">
</div>

<a align="center" href="https://pokeapi.co">Si quieres saber más de esta herramienta dale click aquí.</a>

## 🛠️ Instalación y dependencias de la aplicación

### Requisitos previos

Antes de comenzar, aseguráte de tener instalado en tu sistema:

- **Python 3.9 o superior**

- **pip (gestor de paquetes de Python, normalmente incluido en este.)**

Puedes verificarlo ejecutando en una terminal o consola:
```bash
python --version
pip --version
```

### Descargar el proyecto

#### Opcion 1: Clonar con Git

```bash
git clone "https://github.com/MiguelNievesA/Py-Dex"

cd Py-Dex (<nombre-del-repositorio>)
```

### 📦 Instalar dependencias

Para instalar de manera automática todas las dependencias del proyecto utiliza el archivo **requirements.txt** y ejecuta:

```shell
pip install -r requirements.txt
```

Una vez instalas las dependencias, ejecuta el archivo principal del proyecto:

```shell
python main.py
```

### Errores comunes y soluciones

* `ModuleNotFoundError`
  
  Alguna dependencia no está instalada. Revisa la sección de dependencias.

* `La aplicación no abre la ventana`
  
  Verifica que PyQt5 esté correctamente instalado y que ejecutes el archivo prinicipal.

* `Conflictos de versiones`

  Usa siempre un entorno virtual limpio para utilizar las dependencias y evitar este conflicto de versiones.


## Recomendaciones para reportar problemas (Issues)

Para facilitar la corrección de errores, te pido que, antes de abrir un **issue**, revises cuidadosamente la documentación oficial del proyecto.

Si después de ello confirmas que se trata de un **error real en el proyecto**, por favor proporciona la siguiente información de forma clara y ordenada:

1. **Sistema operativo**
Indica el sistema operativo y su versión (por ejemplo: Windows 11, Ubuntu 22.04, macOS Sonoma).

2. **Versión de la librerías utilizadas para ejecutar el proyecto**
Especifica la versión exacta de la aplicación que estás utilizando y las librerías que instalaste para ejecutarla.

3. **Código mínimo reproducible**
Incluye un ejemplo de código lo más pequeño posible que permita reproducir el problema. Evita compartir proyectos completos si no es necesario.

4. **Pasos para reproducir el error**
Describe, paso a paso, qué acciones deben realizarse para que el problema ocurra.
