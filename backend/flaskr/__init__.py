import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    return jsonify({'categories': [c.format() for c in categories]})
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    page_number = request.args.get('page', 1, type=int)
    offset = (page_number - 1) * 10
    questions = Question.query.offset(offset).limit(10)
    categories = Category.query.all()
    formatted_questions = [q.format() for q in questions]
    if len(formatted_questions) > 0:
      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': Question.query.count(),
        'categories': [c.format() for c in categories]
      })
    else:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)
    if question is None:
      abort(404)
    question.delete()
    return jsonify({
      'success': True,
      'deleted': question_id
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    question = Question(
      question=body.get('question', None),
      answer=body.get('answer', None),
      category=body.get('category', None),
      difficulty=body.get('difficulty', None)
      )
    try:
      question.insert()
      return jsonify({
        'success': True,
        'added': question.id
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/searched_questions', methods=['POST'])
  def search_questions():
    search_term = request.get_json()['searchTerm']
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    if len(questions) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': [q.format() for q in questions],
      'total_questions': len(questions)
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    if len(questions) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': [q.format() for q in questions],
      'total_questions': len(questions)
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quzzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    quiz_category = int(body.get('quiz_category', 0))
    
    if quiz_category > 0:
      available_questions = Question.query.filter(Question.category == quiz_category, Question.id.notin_(previous_questions)).all()
    else:
      available_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
    
    print(available_questions)
    next_question = None
    if len(available_questions) > 0:
      next_question = random.choice(available_questions)
    return jsonify({
      'success': True,
      'question': next_question.format() if next_question is not None else None
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'status': 404,
      'message': 'Resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'status': 422,
      'message': 'Request unprocessable'
    }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'status': 405,
      'message': 'Method not allowed for this endpoint'
    }), 405
  
  return app

    