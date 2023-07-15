import logging
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, select
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()


class ARTICLES(db.Model, SerializerMixin):
    # id | language | title | qa_id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(10))
    title = db.Column(db.String(2000))


class QA(db.Model, SerializerMixin):
    # id | question | answer | article_id | timestamp
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(2000))
    answer = db.Column(db.String(10000))
    article_id = db.Column(db.Integer, ForeignKey("articles.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class QAStore:
    def __init__(self, db):
        self.db = db

    def insert_qa_list(self, language, title, qa_list):
        existing_records = self.query_questions(language, title)
        if len(existing_records.all()):
            return
        article = ARTICLES(
            language=language,
            title=title,
        )
        self.db.session.add(article)
        self.db.session.commit()
        logging.info(f"[Add] {language} - {title}")
        qa_obj_list = [
            QA(question=item["question"], answer=item["answer"], article_id=article.id)
            for item in qa_list
        ]
        self.db.session.add_all(qa_obj_list)
        self.db.session.commit()

    def query_questions(self, language, title):
        db_search_results = self.db.session.execute(
            select(QA)
            .join(ARTICLES)
            .where(ARTICLES.language == language, ARTICLES.title == title)
        )
        return db_search_results
