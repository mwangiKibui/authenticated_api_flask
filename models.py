from app import db,ma

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    public_id = db.Column(db.String(50),unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

#the Schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','public_id','name','admin')

class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id','text','completes')

user_schema = UserSchema()
users_schema = UserSchema(many=True)
todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True) 