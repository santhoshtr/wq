from flask import Flask, abort, render_template, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from store.qa import db, QAStore
from wq import get_questions

import os
import json

DATABASE_NAME="wq.db"
app = Flask(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(
    os.path.join(project_dir, DATABASE_NAME)
)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db.init_app(app)
store = QAStore(db)

def get_languages():
    return ['en', 'es']

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

@app.route('/', methods = ['GET', 'POST'])
def index():
     return render_template("index.html", languages=get_languages())

@app.route('/api/qa/<language>/<title>', methods = ['GET'])
def get_qa(language, title):
    initdb()
    auth_cookie_name = os.environ.get('WQ_AUTH_COOKIE')
    if auth_cookie_name:
        print(request.cookies)
        if not request.cookies.get(auth_cookie_name):
            abort(401, description="API usage not authorized")
    qas = []
    qa_list=store.query_questions(language,title)
    qas = [q[0].to_dict() for q in qa_list]
    if len(qas) == 0:
        predicted_qas=get_questions(language, title)
        if len(predicted_qas) > 0:
            store.insert_qa_list(language,title, predicted_qas)
            qa_list=store.query_questions(language,title)
            qas = [q[0].to_dict() for q in qa_list]

    return jsonify(qas)

def initdb():
    db.create_all()

if __name__ == "__main__":
    f = open('test.json')
    data = json.load(f)
    f.close()
    store = QAStore(db)
    store.insert_qa_list('en', 'Charminar', data)
    # result=store.query_questions('en', 'Charminar')
    # print(result.all())
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)