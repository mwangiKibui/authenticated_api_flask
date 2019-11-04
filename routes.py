from app import app,db
from flask import request,jsonify,make_response
from werkzeug.security import generate_password_hash,check_password_hash
import uuid
from models import User,Todo,user_schema,users_schema
from jwt import encode,decode
import datetime
from functools import wraps

#am keeping it simple for now later after the tutorial we can add more

# decorator for validating the token

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({
                'message':'Token is missing'
            }),401  
        try:
            data = decode(token,app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({
                'message':'Token is invalid'
            }),401
        return f(current_user,*args,**kwargs)
    return decorated

@app.route('/users',methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that operation'})        
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify(result)

@app.route('/user/<public_id>',methods=['GET'])
@token_required
def get_one_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that operation'})
    user  = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({
            'message' : 'no such user exists'
        })
    
    return user_schema.jsonify(user)

@app.route('/user',methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that operation'})
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'],method='sha256')
    new_user = User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        'message':'A new user has been created'
    })

@app.route('/user/<public_id>',methods=['PUT'])
@token_required
def promote_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that operation'})
    user  = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({
            'message' : 'no such user exists'
        })
    user.admin = True
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/user/<public_id>',methods=['DELETE'])
@token_required
def delete_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that operation'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({
            'message': 'no such user exists'
        })
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'message':'The user has been removed successfully'
    })

@app.route('/login',methods=['POST'])
def login():
    auth  = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify',401,{'www-Authenticate':'Basic realm="Login required"'})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'www-Authenticate': 'Basic realm="Login required"'})
    if check_password_hash(user.password,auth.password):
        token = encode({'public_id':user.public_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'])
        
        return jsonify({
            'token' : token.decode('UTF-8')
        })
    return make_response('Could not verify', 401, {'www-Authenticate': 'Basic realm="Login required"'})

@app.route('/todo',methods=['GET'])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id)
    output = []
    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        output.append(todo_data)
    return jsonify({
        'todos':output
    })

@app.route('/todo/<todo_id>',methods=['GET'])
@token_required
def get_one_todo(current_user,todo_id):
    todo = Todo.query.filter_by(id=todo_id,user_id=current_user.id).first()
    if not todo:
        return jsonify({
            'message':'Sorry no todo found'
        })
    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete
    return jsonify(todo_data)

@app.route('/todo',methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()
    new_todo = Todo(text=data['text'],complete=False,user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({
        'message':'The todo has successfully been added'
    })

@app.route('/todo/<todo_id>',methods=['PUT'])
@token_required
def complete_todo(current_user,todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify({
            'message': 'Sorry no todo found'
        })
    todo.complete = True
    db.session.commit()
    return jsonify({
        'message':'Todo item has been completed'
    })

@app.route('/todo/<todo_id>',methods=['DELETE'])
@token_required
def delete_todo(current_user,todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    if not todo:
        return jsonify({
            'message': 'Sorry no todo found'
        })
    db.session.delete(todo)
    db.session.commit()
    return jsonify({
        'message':'Todo has been deleted'
    })
