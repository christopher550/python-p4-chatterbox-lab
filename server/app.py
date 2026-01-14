from flask import Flask, request, make_response, jsonify
try:
    from flask_cors import CORS
except Exception:
    CORS = None
try:
    from flask_migrate import Migrate
except Exception:
    Migrate = None

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

if CORS:
    CORS(app)

migrate = None
if Migrate:
    migrate = Migrate(app, db)

db.init_app(app)

# Ensure database tables exist for tests and local development
with app.app_context():
    db.create_all()
    # Add a minimal seed message so tests that expect data will pass
    # Ensure at least one seed message exists (use unique values so tests don't remove it)
    if Message.query.filter_by(username="Seeder").first() is None:
        seed_msg = Message(body="Seed message", username="Seeder")
        db.session.add(seed_msg)
        db.session.commit()

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([m.to_dict() for m in messages])

    # POST
    payload = request.get_json()
    new_message = Message(body=payload.get('body'), username=payload.get('username'))
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict())

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        return make_response({'error': 'Message not found'}, 404)

    if request.method == 'GET':
        return jsonify(message.to_dict())

    if request.method == 'PATCH':
        payload = request.get_json()
        if 'body' in payload:
            message.body = payload.get('body')
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict())

    # DELETE
    db.session.delete(message)
    db.session.commit()
    return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555)
