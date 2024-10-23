# N-Encrypt
![N-Encrypt WEB](img/img01.png)
![N-Encrypt WEB](img/img02.png)
![N-Encrypt WEB](img/img03.png)
![N-Encrypt WEB](img/img05.png)
![N-Encrypt WEB](img/img04.png)

## Descripción
N-Encrypt  es una aplicación web segura para la gestión de mensajes encriptados, desarrollada con Flask, JavaScript vanilla y TailwindCSS. Permite a los usuarios crear, leer, editar y eliminar mensajes encriptados con caducidad, todo ello sin necesidad de registro.

## Características principales
- Creación de mensajes encriptados con caducidad personalizable
- Lectura de mensajes mediante ID único y clave de encriptación
- Edición y eliminación de mensajes existentes
- Interfaz de usuario intuitiva y responsive
- Soporte para múltiples algoritmos de encriptación (SHA256, SHA384, SHA512)
- Modo oscuro para mayor comodidad visual

## Requisitos del sistema
- Python 3.8+
- Flask
- SQLAlchemy
- Flask-Migrate
- PostgreSQL

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/686f6c61/n-encrypt-web.git
   cd n-encrypt-web
   ```

2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Configurar las variables de entorno:
   Crea un archivo `.env` en la raíz del proyecto y añade las siguientes variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_base_de_datos
   FLASK_SECRET_KEY=tu_clave_secreta
   ```

4. Inicializar la base de datos:
   ```
   flask db upgrade
   ```

5. Ejecutar la aplicación:
   ```
   flask run
   ```

La aplicación estará disponible en `http://localhost:5000`.

## Uso

### Crear un mensaje
1. Accede a la página principal y haz clic en "Crear Mensaje".
2. Escribe el contenido del mensaje, selecciona el algoritmo de encriptación y establece la fecha de caducidad.
3. Opcionalmente, añade una clave personal y/o de terceros para mayor seguridad.
4. Haz clic en "Crear Mensaje Encriptado".
5. Guarda la URL y la clave de encriptación generadas.

### Leer un mensaje
1. Utiliza la URL proporcionada o ve a "Leer Mensaje" en la navegación.
2. Introduce el ID del mensaje, la clave de encriptación y las claves adicionales si se usaron.
3. Haz clic en "Desencriptar Mensaje" para ver el contenido.

### Editar o eliminar un mensaje
1. Accede al mensaje utilizando la URL y la clave de encriptación.
2. Utiliza las opciones "Editar" o "Borrar" según sea necesario.

## Seguridad
- Los mensajes se almacenan encriptados en la base de datos.
- Las claves de encriptación nunca se almacenan en texto plano.
- Los mensajes caducan automáticamente después del período especificado.

## Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de crear un pull request.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.


