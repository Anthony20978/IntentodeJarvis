# JARVIS FUNCIONAL
## Proposito:
En este proyecto intentaremos hacer un jarvis funcional.
## Versión
v0.1.0
## Estado
En este momento, Jarvis esta en fase 0, no existe codigo y es una fase de organización e inicialización.
## Organización de archivos
<style>
.tree ul {
  list-style: none;
  padding-left: 10px;
}
.tree li {
  position: relative;
  padding: 5px 0 5px 20px;
  border-left: 1px solid #888;
}
.tree li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 16px;
  width: 15px;
  border-top: 1px solid #888;
}
.tree li:last-child {
  border-left: none;
}
.tree li:last-child::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  height: 16px;
  border-left: 1px solid #888;
}
</style>
<div class="tree">
  <ul>JARVIS/<ul>
        <li>src/<ul>
            <li>jarvis/<ul>
            <li>__init__.py</li>
            <li>main.py</li>
            <li>config.py</li>
            <li>brain.py</li>
            <li>memory.py</li>
            <li>capabilities.py</li>
            <li>platform.py</li></ul></li></ul></li>
        <li>tests/<ul>
        <li>__init__.py</li>
        <li>test_core.py</li></ul></li>
        <li>README.md</li>
        <li>.gitignore</li>
        <li>pyproject.toml</li></ul></ul>
</div>

## Descipción de los directorios
- carpeta **src/**:
    contiene el codigo fuente del proyecto.
  - subcarpeta **jarvis/**:
      el nucleo de jarvis y sus capacidades.
    - archivo **config.py**:
        gestiona parametros generales, rutas y configuraciones del asistente.
    - archivo **main.py**: 
      inicia y coordina a Jarvis.
    - archivo **brain.py**:
      procesa instrucciones.
    - archivo **memory.py**:
      guarda y recupera información local.
    - archivo **capabilities.py**:
      administra las funciones que se pueden ejecutar.
    - archivo **platform.py**:
      adapta las funciones a otros entornos.
    - archivo **__init__.py**:
      permite organizar los modulos como paquetes de python.
- carpeta **tests/**:
    contiene pruebas que verifican el funcionamiento de jarvis.
    - archivo **__init__.py**:
      permite organizar los modulos como paquetes de python.
    - archivo **test_core.py**:
      ayuda a comprobar el funcionamiento del nucleo
  
- archivo **README.md**:
contiene la principal informacion para el usuario.
- archivo **.gitignore**:
se asegura de que GitHub no guarde archivos innecesarios.
- archivo **pyprojecy.py**:
contiene información acerca de la configuración del proyecto.
<div style="border-left: 4px solid #c42220; background: #2b1717; padding: 12px; border-radius: 6px;">
El proyecto continua en una fase temprana de desarrollo. Su estructura y funcionalidades cambiarán conforme a su construcción.
</div>