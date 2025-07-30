
![Babot](assets/logo.png)



# BABOT

Babot es un framework para crear agentes inteligentes personalizados utilizando Langchaing, integrados con modelos de lenguaje como Llama 2, y diseñados para ejecutarse en infraestructura local o en la nube. 
Ofrece herramientas para inicializar proyectos, crear agentes desde cero, clonar agentes predefinidos desde un repositorio, y ejecutar tareas complejas como búsqueda en internet o análisis de imágenes.




## Caracteristicas

**Fácil Inicialización:** Crea rápidamente un proyecto base con la CLI.

**Agentes Personalizados:** Diseña agentes con prompts y capacidades específicas.

**Integración con Ollama:** Utiliza modelos como Llama 2 para ejecución local.

**Soporte Modular:** Añade agentes o funcionalidades según las necesidades del negocio.

**Escalabilidad:** Perfecto para proyectos pequeños o despliegues empresariales.
## Instalación

**Instala el framework:**

```bash
  pip install babot
  cd my-project
```
  
**Verifica que Babot esté instalado:**

```bash
  babot --version
```

**Inicializar un Proyecto Para comenzar un nuevo proyecto:**

babot init <nombre_proyecto>

```bash
  babot init mi_proyecto
```

Esto generará una estructura base en el directorio mi_proyecto.

**Ejecutar un Agente Existente Dirígete al directorio del proyecto:**

NOTA: es importante que ollama esté corriendo en algún puerto localmente.

```bash
  cd mi_proyecto
  babot run babot
```

Puedes modificar el prompt del babot o cualquier configuracion del agente dentro del directorio **config/babot.yaml**


## Cómo crear Agentes

Puedes crear un agente desde cero con: babot create <nombre_agente>

```bash
babot create agente_ventas
```

Esto generará:

Un archivo Python: **agentes/agente_ventas.py**.
Un archivo de configuración: **config/agente_ventas.yaml**.

Edítalos según tus necesidades y ejecuta el nuevo agente: 

```bash
babot run agente_ventas
```



## Cómo clonar un Agente desde nuestro repositorio

Si deseas usar un agente predefinido de nuestro repositorio, puedes clonarlo: babot clone <nombre_agente>

```bash
babot clone agente_marketing
```

Esto descargará el código del agente y su configuración en tu proyecto.


## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

