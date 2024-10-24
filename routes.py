import os
from flask import render_template, request, redirect, url_for, flash, abort, jsonify, send_file
from app import app, db
from models import Message, MessageVersion, FileAttachment
from utils import generate_encryption_key, encrypt_message, decrypt_message, generate_unique_id
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import io
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit/<message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.expires_at and message.expires_at < datetime.utcnow():
        db.session.delete(message)
        db.session.commit()
        abort(404)
    
    if request.method == 'POST':
        encryption_key = request.form.get('encryption_key')
        personal_key = request.form.get('personal_key')
        new_content = request.form.get('content')
        
        # Validate keys
        if not encryption_key or encryption_key != message.encryption_key:
            flash('Clave de encriptación inválida', 'error')
            return redirect(url_for('edit_message', message_id=message_id))
            
        if not personal_key or personal_key != message.personal_key:
            flash('Clave personal inválida. Solo el creador puede editar el mensaje.', 'error')
            return redirect(url_for('edit_message', message_id=message_id))
            
        if not new_content or new_content.strip() == '':
            flash('El contenido del mensaje no puede estar vacío', 'error')
            return redirect(url_for('edit_message', message_id=message_id))
        
        try:
            # Encrypt new content
            encrypted_content = encrypt_message(new_content, encryption_key, message.encryption_algorithm).decode()
            
            # Update message content and create new version
            message.content = encrypted_content
            message.versions.append(MessageVersion(content=encrypted_content))
            
            db.session.commit()
            flash('Mensaje actualizado exitosamente', 'success')
            return redirect(url_for('view_message', message_id=message_id))
            
        except Exception as e:
            logger.error(f"Error updating message: {str(e)}")
            flash('Error al actualizar el mensaje', 'error')
            return redirect(url_for('edit_message', message_id=message_id))
    
    # For GET request, decrypt the message if keys are provided in URL
    encryption_key = request.args.get('encryption_key')
    personal_key = request.args.get('personal_key')
    
    if encryption_key and personal_key:
        if encryption_key != message.encryption_key:
            flash('Clave de encriptación inválida', 'error')
            return redirect(url_for('view_message', message_id=message_id))
            
        if personal_key != message.personal_key:
            flash('Clave personal inválida. Solo el creador puede editar el mensaje.', 'error')
            return redirect(url_for('view_message', message_id=message_id))
            
        try:
            decrypted_content = decrypt_message(message.content, encryption_key, message.encryption_algorithm)
            return render_template('edit_message.html', 
                                message_id=message_id,
                                message=decrypted_content)
        except Exception as e:
            logger.error(f"Error decrypting message: {str(e)}")
            flash('Error al desencriptar el mensaje', 'error')
            return redirect(url_for('view_message', message_id=message_id))
    
    return render_template('edit_message.html', message_id=message_id)

@app.route('/create', methods=['GET', 'POST'])
def create_message():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        content = data.get('content')
        encryption_algorithm = data.get('encryption_algorithm', 'SHA256')
        personal_key = data.get('personal_key')

        if not personal_key:
            if request.is_json:
                return jsonify({'error': 'La clave personal es obligatoria'}), 400
            flash('La clave personal es obligatoria', 'error')
            return redirect(url_for('create_message'))

        # Initialize expiration values
        expiration_days = int(data.get('expiration_days', 0) or 0)
        expiration_hours = int(data.get('expiration_hours', 0) or 0)
        expiration_minutes = int(data.get('expiration_minutes', 0) or 0)

        if expiration_days == 0 and expiration_hours == 0 and expiration_minutes == 0:
            expiration_days = 7  # Default to 7 days if no expiration is set

        encryption_key = generate_encryption_key()
        encrypted_content = encrypt_message(content, encryption_key, encryption_algorithm).decode()

        message_id = generate_unique_id()
        new_message = Message(
            id=message_id,
            content=encrypted_content,
            encryption_key=encryption_key,
            personal_key=personal_key,
            third_party_key=data.get('third_party_key'),
            expiration_days=expiration_days,
            expiration_hours=expiration_hours,
            expiration_minutes=expiration_minutes,
            encryption_algorithm=encryption_algorithm
        )

        # Handle file uploads
        if not request.is_json and request.files:
            files = request.files.getlist('attachments')
            logger.debug(f"Processing {len(files)} files")
            
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    try:
                        file_data = file.read()
                        if len(file_data) > MAX_FILE_SIZE:
                            flash(f'El archivo {file.filename} excede el tamaño máximo permitido de 10MB', 'error')
                            continue

                        filename = secure_filename(file.filename)
                        logger.debug(f"Encrypting file {filename} of size {len(file_data)} bytes")
                        
                        encrypted_file_data = encrypt_message(file_data, encryption_key, encryption_algorithm)
                        logger.debug(f"File encrypted successfully, size: {len(encrypted_file_data)} bytes")
                        
                        attachment = FileAttachment(
                            message_id=message_id,
                            filename=filename,
                            encrypted_data=encrypted_file_data,
                            file_type=file.content_type or 'application/octet-stream',
                            file_size=len(file_data)
                        )
                        new_message.attachments.append(attachment)
                        logger.debug(f"File attachment added: {filename}")
                    except Exception as e:
                        logger.error(f"Error processing file {file.filename}: {str(e)}")
                        flash(f'Error al procesar el archivo {file.filename}: {str(e)}', 'error')
                        continue

        db.session.add(new_message)
        db.session.commit()
        logger.info(f"Message {message_id} created successfully with {len(new_message.attachments)} attachments")

        url = url_for('view_message', message_id=message_id, _external=True)
        
        if request.is_json:
            return jsonify({
                'message_url': url,
                'encryption_key': encryption_key
            })
        return render_template('create_message.html', message_url=url, encryption_key=encryption_key)

    return render_template('create_message.html')

@app.route('/read', methods=['GET', 'POST'])
def read_message():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        message_id = data.get('message_id')
        encryption_key = data.get('encryption_key')
        user_key = data.get('user_key')
        
        if request.is_json:
            return jsonify({
                'redirect': url_for('view_message', message_id=message_id, encryption_key=encryption_key, user_key=user_key)
            })
        return redirect(url_for('view_message', message_id=message_id, encryption_key=encryption_key, user_key=user_key))
    
    return render_template('read_message.html')

@app.route('/view/<message_id>', methods=['GET', 'POST'])
def view_message(message_id):
    message = Message.query.get_or_404(message_id)

    if message.expires_at and message.expires_at < datetime.utcnow():
        db.session.delete(message)
        db.session.commit()
        abort(404)

    if request.method == 'POST' or request.args.get('encryption_key'):
        data = request.get_json() if request.is_json else request.form
        encryption_key = data.get('encryption_key') or request.args.get('encryption_key')
        user_key = data.get('user_key') or request.args.get('user_key')

        # Validate both keys are provided
        if not encryption_key or not user_key:
            if request.is_json:
                return jsonify({'error': 'Se requieren ambas claves: encriptación y personal/terceros'}), 400
            flash('Se requieren ambas claves: encriptación y personal/terceros', 'error')
            return redirect(url_for('read_message'))

        # Validate encryption key
        if encryption_key != message.encryption_key:
            if request.is_json:
                return jsonify({'error': 'Clave de encriptación inválida'}), 400
            flash('Clave de encriptación inválida', 'error')
            return redirect(url_for('read_message'))

        # Validate user key matches either personal or third party key
        if user_key != message.personal_key and user_key != message.third_party_key:
            if request.is_json:
                return jsonify({'error': 'Clave personal o de terceros inválida'}), 400
            flash('Clave personal o de terceros inválida', 'error')
            return redirect(url_for('read_message'))

        decrypted_content = decrypt_message(message.content, message.encryption_key, message.encryption_algorithm)
        attachments = [{
            'filename': attachment.filename,
            'size': attachment.file_size,
            'type': attachment.file_type
        } for attachment in message.attachments]
        
        if request.is_json:
            return jsonify({
                'message': decrypted_content,
                'encryption_algorithm': message.encryption_algorithm,
                'attachments': attachments
            })
        return render_template('view_message.html', 
                           message=decrypted_content, 
                           message_id=message_id, 
                           encryption_key=encryption_key,
                           user_key=user_key,
                           is_owner=user_key == message.personal_key,
                           encryption_algorithm=message.encryption_algorithm,
                           attachments=attachments)

    # If no keys provided, redirect to read message page
    return redirect(url_for('read_message'))

@app.route('/download/<message_id>/<filename>', methods=['POST'])
def download_attachment(message_id, filename):
    message = Message.query.get_or_404(message_id)
    attachment = next((a for a in message.attachments if a.filename == filename), None)
    if not attachment:
        abort(404)
    
    encryption_key = request.form.get('encryption_key')
    if not encryption_key or encryption_key != message.encryption_key:
        flash('Clave de encriptación inválida', 'error')
        return redirect(url_for('view_message', message_id=message_id))
    
    try:
        if not isinstance(attachment.encrypted_data, bytes):
            logger.error(f"Encrypted data is not bytes: {type(attachment.encrypted_data)}")
            raise ValueError("Los datos encriptados no están en el formato correcto")

        logger.info(f"Decrypting file: {filename}, size: {len(attachment.encrypted_data)} bytes")
        
        decrypted_data = decrypt_message(
            attachment.encrypted_data,
            message.encryption_key,
            message.encryption_algorithm,
            is_file=True
        )
        
        if not isinstance(decrypted_data, bytes):
            logger.error(f"Decrypted data is not bytes: {type(decrypted_data)}")
            raise ValueError("Error en la desencriptación: los datos no están en el formato correcto")
        
        logger.info(f"File decrypted successfully, size: {len(decrypted_data)} bytes")
        
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype=attachment.file_type,
            as_attachment=True,
            download_name=attachment.filename
        )
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        flash(f'Error al descargar el archivo: {str(ve)}', 'error')
        return redirect(url_for('view_message', message_id=message_id))
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        flash(f'Error al descargar el archivo: problema de desencriptación', 'error')
        return redirect(url_for('view_message', message_id=message_id))

@app.route('/delete/<message_id>', methods=['GET', 'POST'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        provided_key = data.get('encryption_key')
        personal_key = data.get('personal_key')
        message_id_confirmation = data.get('message_id_confirmation')

        if not provided_key or not personal_key:
            if request.is_json:
                return jsonify({'error': 'Se requieren tanto la clave de encriptación como la clave personal'}), 400
            flash('Se requieren tanto la clave de encriptación como la clave personal', 'error')
            return redirect(url_for('delete_message', message_id=message_id))

        if provided_key != message.encryption_key:
            if request.is_json:
                return jsonify({'error': 'Clave de encriptación inválida'}), 400
            flash('Clave de encriptación inválida', 'error')
            return redirect(url_for('delete_message', message_id=message_id))

        if personal_key != message.personal_key:
            if request.is_json:
                return jsonify({'error': 'Clave personal inválida'}), 400
            flash('Clave personal inválida', 'error')
            return redirect(url_for('delete_message', message_id=message_id))

        if message_id_confirmation != message_id:
            if request.is_json:
                return jsonify({'error': 'El ID del mensaje proporcionado no coincide'}), 400
            flash('El ID del mensaje proporcionado no coincide', 'error')
            return redirect(url_for('delete_message', message_id=message_id))

        confirmation = data.get('confirmation')
        if confirmation != 'BORRAR':
            if request.is_json:
                return jsonify({'error': 'Por favor, escriba BORRAR para confirmar la eliminación del mensaje'}), 400
            flash('Por favor, escriba BORRAR para confirmar la eliminación del mensaje', 'error')
            return render_template('delete_message.html', message_id=message_id)

        db.session.delete(message)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Mensaje eliminado exitosamente'})
        flash('Mensaje eliminado exitosamente', 'success')
        return redirect(url_for('index'))

    return render_template('delete_message.html', message_id=message_id)

@app.errorhandler(404)
def page_not_found(e):
    if request.is_json:
        return jsonify({'error': 'Página no encontrada'}), 404
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    if request.is_json:
        return jsonify({'error': 'Acceso prohibido'}), 403
    return render_template('403.html'), 403
