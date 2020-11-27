# Script to output JV payments/orders Excel

# Descripción

Este escript es utilizado para dejar los cierres semanales de la tienda 'Juan Valdez' Chile.
Este cierres pasa por un preprocesamiento y luego es dejado en un FTP definido por su proveedor de servicios Falabella.

# Instalación y Mantención

## 1. Versiones Utilizadas

* Python 3.8

## 2. Requerimientos
* Servidor con Python >= 3.8

## 3. Instalación

Se debe buscar el directorio raíz, donde se hosteara el proyecto, ejemplo:

	cd /var/www/

Una vez ahí, se debe clonar el repositorio perteneciente al proyecto, este proyecto está bajo el software de control de versiones llamado git y hospedado en github, para clonar el repositorio se debe ejecutar el siguiente comando, 

	git clone https://github.com/getjusto...

> Este comando te pedirá autenticación, deberás autenticarte con tu usuario y clave.

Una vez autenticado comenzara la clonación del repositorio. Este repositorio contiene el proyecto, sin las librerías externas de Python utilizadas, por ende, se debe a proceder a instalarlas:

Cuando esté el repositorio clonado, se deberá ingresar a él, estará ubicado el directorio `cierre-jv` que se acabó de crear al ejecutar el comando anterior.

	cd cierre-jv

Una vez dentro del directorio, se deberá copiar el archivo .env.example a .env y editar las variables de configuraciones iniciales dentro de .env:

	cp .env.example .env
	
En el .env solo deberás modificar las siguientes variables de entorno:

* API_KEY

Luego, hacer la instalación de las librerías de Python necesarias a través del siguiente comando:

	pipenv install

Con esto ya estaría el proyecto listo para ser utilizado en producción.

## 4. Desarrollo y Mantención

Dirigete a donde tienes hospedado el proyecto, ejemplo:

	cd /var/www/cierre-jv

Una vez dentro, deberás ejecutar el comando para actualizar el repositorio

	git pull 

Instalar pipenv, para generar un entorno virtual de trabajo de Python

    pip3 install pipenv

Una vez tengamos pipenv instalado, procedemos a instalar los paquetes requeridos definidos en Pipfile

    pipenv install

Activar virtualenv en el proyecto:

    pipenv shell

## 5. Ejecutar el programa

Para ejecutar pruebas se debe ejecutar el siguiente comando:

    python src/main.py 

## 6. Configurar jobs

TODO...

## 7. Soporte

Si a pesar de todo resulta algún error y no lo puedes solucionar, contacta a:

* Sebastián Iturra <sebastian.iturra@getjusto.com>
* Joaquin Gumuccio <...>
