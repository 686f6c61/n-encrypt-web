# N-Encrypt

![Imagen 01](img/img01.png)
![Imagen 02](img/img02.png)
![Imagen 03](img/img03.png)
![Imagen 04](img/img04.png)
![Imagen 05](img/img05.png)



## Descripción
N-Encrypt es una aplicación web segura para la gestión de mensajes encriptados, desarrollada con Flask, JavaScript vanilla y TailwindCSS. Permite a los usuarios crear, leer, editar y eliminar mensajes encriptados con caducidad, todo ello sin necesidad de registro.

## Características principales
- **Creación de mensajes encriptados**: Posibilidad de establecer una caducidad personalizable.
- **Lectura de mensajes**: Acceso mediante ID único y clave de encriptación.
- **Edición y eliminación**: Modificación y borrado de mensajes existentes.
- **Interfaz intuitiva**: Diseño responsive y fácil de usar.
- **Soporte para múltiples algoritmos de encriptación**: Incluye SHA256, SHA384 y SHA512.
- **Modo oscuro**: Mejora la comodidad visual en entornos oscuros.
- **Archivos adjuntos encriptados**: Permite adjuntar archivos de manera segura.
- **Sistema CAPTCHA**: Previene el spam y asegura interacciones genuinas.

## Almacenamiento y Seguridad de Datos

### Base de Datos
- **Sistema**: PostgreSQL.
- **Estructura**:
  - Mensajes encriptados con claves únicas.
  - Gestión de versiones de mensajes.
  - Almacenamiento seguro de archivos adjuntos.
  - Campos de metadatos para control de caducidad.
- **Características**:
  - Índices optimizados para búsqueda rápida.
  - Relaciones con integridad referencial.
  - Eliminación en cascada de datos relacionados.
  - Pool de conexiones con reciclado automático.

### Entropía y Seguridad
- **Generación de claves**:
  - Uso de `secrets` para la creación de IDs únicos.
  - Implementación de Fernet para encriptación simétrica.
  - Salt único por mensaje para la derivación de claves.
- **Algoritmos de hash soportados**:
  - **SHA256** (predeterminado): Un equilibrio entre seguridad y rendimiento.
  - **SHA384**: Mayor seguridad para datos sensibles.
  - **SHA512**: Máxima seguridad disponible.
- **Características de seguridad**:
  - Claves nunca almacenadas en texto plano.
  - Verificación de integridad de datos.
  - Protección contra ataques de fuerza bruta.
  - Sistema de doble clave (encriptación + personal/terceros).

## Requisitos del sistema
- **Python**: 3.8+
- **Frameworks y librerías**:
  - Flask
  - SQLAlchemy
  - Flask-Migrate
  - Cryptography
- **Base de datos**: PostgreSQL

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/686f6c61/n-encrypt-web.git
   cd n-encrypt


## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/n-encrypt.git
   cd n-encrypt
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
4. Adjunta archivos si es necesario (máximo 10MB por archivo).
5. Completa el CAPTCHA y haz clic en "Crear Mensaje Encriptado".
6. Guarda la URL y la clave de encriptación generadas.

### Leer un mensaje
1. Utiliza la URL proporcionada o ve a "Leer Mensaje" en la navegación.
2. Introduce el ID del mensaje, la clave de encriptación y las claves adicionales si se usaron.
3. Haz clic en "Desencriptar Mensaje" para ver el contenido.

### Editar o eliminar un mensaje
1. Accede al mensaje utilizando la URL y la clave de encriptación.
2. Utiliza las opciones "Editar" o "Borrar" según sea necesario.
3. Para borrar, deberás confirmar escribiendo "BORRAR" y proporcionar todas las claves.

## Seguridad
- Los mensajes se almacenan encriptados en la base de datos
- Las claves de encriptación nunca se almacenan en texto plano
- Los mensajes caducan automáticamente después del período especificado
- Sistema de doble clave para mayor seguridad
- Verificación CAPTCHA para prevenir spam
- Límites de tamaño en archivos adjuntos

## Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de crear un pull request.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

© 2024 N-Encrypt
