import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)

    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Headers', 'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        return jsonify({
            'success': True,
            'categories':{category.id: category.type for category in categories}
            })
    
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        # categories
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]
        
        if (len(current_questions) == 0):
            abort(404)
        
        return jsonify(
            {
                'success':True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'current_category': 'All',
                'categories': formatted_categories
            }
        )
    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if (question is None):
            abort(404)

        question.delete()
        return jsonify(
            {
                "success": True,
                "deleted": question_id,
            }
        )
                
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        if (new_question is None) or (new_answer is None)or (new_category is None) or (new_difficulty is None):
            abort(422)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()
            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                }
            )

        except:
            abort(422)

    @app.route('/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)
        
        try:
            questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
            
            formatted_questions = [question.format() for question in questions]
            
            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions.all())
            })
        except:
            abort(422)
            
    

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == str(category_id)).all()
        formatted_questions = [question.format() for question in questions]
        
        if len(formatted_questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions':len(questions),
                'category':category_id
                 })
       
        

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz():
        body = request.get_json()
        quiz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        
        if ((quiz_category is None) or (previous_questions is None)):
            abort(404)
        if (quiz_category['id']):
            questions = Question.query.filter(Question.category==str(quiz_category['id'])).filter(Question.id.notin_((previous_questions))).all()
        else:
            questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
        
        if len(questions) > 0:
            current_questions = [question.format() for question in questions]
            
            return jsonify({
                "success": True,
                "questions": current_questions
                })
        else:
            return jsonify({
                "success": True,
                "questions": None
                 })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422
        
    return app
