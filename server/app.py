from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, User, Article

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

### Routes ###

class ClearSession(Resource):
    def get(self):
        session.clear()
        return {}, 204

class Login(Resource):
    def post(self):
        username = request.json.get("username")
        user = User.query.filter_by(username=username).first()

        if user:
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {}, 401

class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {}, 204

class MemberOnlyArticles(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        articles = Article.query.filter_by(is_member_only=True).all()
        return [article.to_dict() for article in articles], 200

class MemberOnlyArticleByID(Resource):
    def get(self, id):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        article = Article.query.filter_by(id=id).first()
        if not article:
            return {"error": "Article not found"}, 404

        return article.to_dict(), 200

### Resource Routes ###

api.add_resource(ClearSession, '/clear')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(MemberOnlyArticles, '/members_only_articles')
api.add_resource(MemberOnlyArticleByID, '/members_only_articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
