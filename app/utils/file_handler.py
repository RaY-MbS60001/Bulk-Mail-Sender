import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

class FileHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_file(file, directory='uploads'):
        if file and FileHandler.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            upload_path = os.path.join(current_app.root_path, 'static', directory)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            return unique_filename
        return None