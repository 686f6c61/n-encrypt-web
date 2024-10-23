from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from app import app, db
from models import Message, MessageVersion
from utils import generate_encryption_key, encrypt_message, decrypt_message, generate_unique_id
from datetime import datetime, timedelta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_message():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        content = data.get('content')
        encryption_algorithm = data.get('encryption_algorithm', 'SHA256')
        expiration_days = int(data.get('expiration_days', 7))

        encryption_key = generate_encryption_key()
        encrypted_content = encrypt_message(content, encryption_key, encryption_algorithm)

        message_id = generate_unique_id()
        new_message = Message(
            id=message_id,
            content=encrypted_content,
            encryption_key=encryption_key,
            expiration_days=expiration_days,
            encryption_algorithm=encryption_algorithm
        )

        db.session.add(new_message)
        db.session.commit()

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

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        encryption_key = data.get('encryption_key')
        user_key = data.get('user_key')
    else:
        encryption_key = request.args.get('encryption_key')
        user_key = request.args.get('user_key')
    
    if encryption_key:
        if encryption_key == message.encryption_key:
            decrypted_content = decrypt_message(message.content, message.encryption_key, message.encryption_algorithm)
            if request.is_json:
                return jsonify({
                    'message': decrypted_content,
                    'encryption_algorithm': message.encryption_algorithm
                })
            return render_template('view_message.html', message=decrypted_content, message_id=message_id, encryption_key=encryption_key, encryption_algorithm=message.encryption_algorithm)
        else:
            if request.is_json:
                return jsonify({'error': 'Clave de encriptación inválida'}), 400
            flash('Clave de encriptación inválida', 'error')

    return render_template('view_message.html', message_id=message_id)

@app.route('/edit/<message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        encryption_key = data.get('encryption_key')

        if not encryption_key:
            if request.is_json:
                return jsonify({'error': 'Se requiere la clave de encriptación para editar el mensaje'}), 400
            flash('Se requiere la clave de encriptación para editar el mensaje', 'error')
            return redirect(url_for('view_message', message_id=message_id))

        if encryption_key != message.encryption_key:
            if request.is_json:
                return jsonify({'error': 'Clave de encriptación inválida'}), 400
            flash('Clave de encriptación inválida', 'error')
            return redirect(url_for('view_message', message_id=message_id))

        new_content = data.get('content')
        if not new_content:
            if request.is_json:
                return jsonify({'error': 'El contenido del mensaje no puede estar vacío'}), 400
            flash('El contenido del mensaje no puede estar vacío', 'error')
            return redirect(url_for('edit_message', message_id=message_id))

        encrypted_content = encrypt_message(new_content, message.encryption_key, message.encryption_algorithm)
        message.update_content(encrypted_content)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Mensaje actualizado exitosamente'})
        flash('Mensaje actualizado exitosamente', 'success')
        return redirect(url_for('view_message', message_id=message_id))

    decrypted_content = decrypt_message(message.content, message.encryption_key, message.encryption_algorithm)
    return render_template('edit_message.html', message_id=message_id, message=decrypted_content)

@app.route('/delete/<message_id>', methods=['GET', 'POST'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        provided_key = data.get('encryption_key')

        if not provided_key:
            if request.is_json:
                return jsonify({'error': 'Se requiere la clave de encriptación para borrar el mensaje'}), 400
            flash('Se requiere la clave de encriptación para borrar el mensaje', 'error')
            return redirect(url_for('view_message', message_id=message_id))

        if provided_key != message.encryption_key:
            if request.is_json:
                return jsonify({'error': 'Clave de encriptación inválida'}), 400
            flash('Clave de encriptación inválida', 'error')
            return redirect(url_for('view_message', message_id=message_id))

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