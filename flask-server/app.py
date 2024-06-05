from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

# Initialisation de l'application Flask
app = Flask(__name__)
cors = CORS(app, origins=["*"])

# Configuration de l'URI de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# Initialisation de l'extension SQLAlchemy
db = SQLAlchemy(app)

# Définition du modèle Todo
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # Date de création par défaut à la date et heure actuelles
    completed = db.Column(db.Boolean, default=False)  # Champ pour marquer une tâche comme complétée ou non
    
    def __repr__(self):
        return '<Task %r>' % self.id

# Créez les tables si elles n'existent pas déjà
with app.app_context():
    db.create_all()

# Route pour ajouter et récupérer des tâches
@app.route('/api/tasks', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'message': 'Content is required'}), 400

        task_content = data['content']
        new_task = Todo(content=task_content)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'id': new_task.id, 'message': 'Task added successfully'}), 201
        except Exception as e:
            return jsonify({'message': 'There was an issue adding your task', 'error': str(e)}), 500
    else:
        try:
            tasks = Todo.query.order_by(Todo.date_created).all()
            return jsonify([{'id': task.id, 'content': task.content, 'completed': task.completed, 'date_created': task.date_created.isoformat()} for task in tasks])
        except Exception as e:
            return jsonify({'message': 'There was an issue fetching the tasks', 'error': str(e)}), 500


# Route pour supprimer une tâche
@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200  # Retourner un message de succès avec un code 200
    except Exception as e:
        return jsonify({'message': 'There was a problem deleting that task', 'error': str(e)}), 500  # Retourner un message d'erreur avec le détail de l'exception et un code 500

@app.route('/api/completed/<int:id>', methods=['PUT'])
def complete(id):
    task = Todo.query.get_or_404(id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404  # Retourner un message d'erreur avec un code 404 si la tâche n'est pas trouvée

    task.completed = not task.completed
    try:
        db.session.commit()
        return jsonify({'message': 'Task completed/uncompleted successfully'}), 200  # Retourner un message de sélection avec un code 200
    except Exception as e:
        return jsonify({'message': 'There was an issue completing/uncompleting your task', 'error': str(e)}), 500  # Retourner un message d'erreur avec le détail de l'exception et un code 500
# Route pour mettre à jour une tâche
@app.route('/api/update/<int:id>', methods=['PUT'])
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    if not todo:
        return jsonify({'message': 'Todo not found'}), 404  # Retourner un message d'erreur avec un code 404 si la tâche n'est pas trouvée

    todo.content = request.json['content']
    try:
        db.session.commit()
        return jsonify({'message': 'Todo updated successfully'}), 200  # Retourner un message de succès avec un code 200
    except Exception as e:
        return jsonify({'message': 'There was an issue updating your task', 'error': str(e)}), 500  # Retourner un message d'erreur avec le détail de l'exception et un code 500

# Point d'entrée de l'application
if __name__ == '__main__':
    app.run(debug=True)
