# Documentación de Almacenamiento de Archivos - N-Encrypt

## Descripción General
N-Encrypt implementa un sistema seguro de almacenamiento de archivos que permite a los usuarios adjuntar y compartir archivos de forma encriptada junto con sus mensajes. Los archivos se almacenan de manera segura en la base de datos PostgreSQL después de ser encriptados.

## Componentes Principales

### 1. Modelo de Datos (models.py)
```python
class FileAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(64), db.ForeignKey('message.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    encrypted_data = db.Column(db.LargeBinary, nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 2. Configuración de Archivos (routes.py)
```python
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB límite por archivo
```

## Proceso de Almacenamiento

### 1. Validación de Archivos
- Se verifica la extensión del archivo usando `allowed_file(filename)`
- Se comprueba que el tamaño no exceda el límite de 10MB
- Se utiliza `secure_filename()` para sanitizar los nombres de archivo

### 2. Encriptación
Los archivos se encriptan usando el mismo sistema que los mensajes:
1. Se lee el contenido del archivo como bytes
2. Se encripta usando la función `encrypt_message()` con la clave del mensaje
3. Se almacena el resultado en la columna `encrypted_data`

### 3. Almacenamiento en Base de Datos
- Los archivos se almacenan como datos binarios en PostgreSQL
- Se mantiene la metadata del archivo (nombre, tipo, tamaño) por separado
- Se vincula cada archivo al mensaje correspondiente mediante `message_id`

## Proceso de Recuperación

### 1. Verificación de Acceso
- Se verifica la clave de encriptación del mensaje
- Se comprueba que el mensaje no haya expirado

### 2. Desencriptación y Descarga
```python
def download_attachment(message_id, filename):
    # 1. Obtener el archivo
    message = Message.query.get_or_404(message_id)
    attachment = next((a for a in message.attachments if a.filename == filename), None)
    
    # 2. Desencriptar datos
    decrypted_data = decrypt_message(
        attachment.encrypted_data,
        message.encryption_key,
        message.encryption_algorithm,
        is_file=True
    )
    
    # 3. Enviar archivo
    return send_file(
        io.BytesIO(decrypted_data),
        mimetype=attachment.file_type,
        as_attachment=True,
        download_name=attachment.filename
    )
```

## Medidas de Seguridad

### 1. Encriptación
- Los archivos se encriptan antes de almacenarse
- Se usa el mismo algoritmo y clave que el mensaje asociado (SHA256/384/512)
- Los datos nunca se almacenan en texto plano

### 2. Validación
- Verificación de tipos MIME
- Sanitización de nombres de archivo
- Límites de tamaño estrictos

### 3. Control de Acceso
- Se requiere la clave de encriptación para descargar
- Los archivos se eliminan automáticamente con el mensaje
- Control de acceso basado en claves personales/terceros

## Limitaciones y Consideraciones
1. Tamaño máximo por archivo: 10MB
2. Tipos de archivo permitidos: txt, pdf, png, jpg, jpeg, gif, doc, docx
3. Los archivos comparten la fecha de expiración del mensaje
4. No se permite la modificación de archivos después de subidos

## Ejemplos de Uso

### 1. Subir un Archivo
```python
# En el formulario HTML
<input type="file" name="attachments" multiple>

# En el controlador
files = request.files.getlist('attachments')
for file in files:
    if file and allowed_file(file.filename):
        encrypted_data = encrypt_message(file.read(), encryption_key)
        attachment = FileAttachment(
            message_id=message_id,
            filename=secure_filename(file.filename),
            encrypted_data=encrypted_data,
            file_type=file.content_type,
            file_size=len(file.read())
        )
```

### 2. Descargar un Archivo
```python
# En la plantilla HTML
<form action="{{ url_for('download_attachment', message_id=id, filename=file) }}" method="post">
    <input type="hidden" name="encryption_key" value="{{ key }}">
    <button type="submit">Descargar</button>
</form>
```

## Mantenimiento y Escalabilidad

### 1. Limpieza de Archivos
- Los archivos se eliminan automáticamente cuando:
  * El mensaje expira
  * El usuario elimina el mensaje
  * Se alcanza el límite de almacenamiento

### 2. Monitoreo
- Se registran todas las operaciones de archivo
- Se mantienen estadísticas de uso
- Se verifican errores de encriptación/desencriptación

### 3. Optimización
- Los archivos grandes se procesan en chunks
- Se utiliza almacenamiento en búfer para la descarga
- Se implementa compresión cuando es posible

## Recomendaciones para el Desarrollo
1. Mantener actualizadas las bibliotecas de seguridad
2. Realizar pruebas regulares de seguridad
3. Monitorear el uso de almacenamiento
4. Implementar políticas de retención de archivos
5. Mantener copias de seguridad regulares
