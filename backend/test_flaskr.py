import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
      response = self.client().get('/questions')
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertGreater(len(data['questions']), 0)
      self.assertGreater(data['total_questions'], 0)
      self.assertGreater(len(data['categories']), 0)

    def test_negative_get_questions_page_not_found(self):
      response = self.client().get('/questions?page=666')
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource not found')

    def test_get_categories(self):
      response = self.client().get('/categories')
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertGreater(len(data['categories']), 0)

    def test_get_questions_by_category(self):
      response = self.client().get('/categories/4/questions')
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertEqual(data['questions'][0]['category'], 4)
      self.assertGreater(data['total_questions'], 0)

    def test_negative_get_questions_by_not_existing_category(self):
      response = self.client().get('/categories/69/questions')
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource not found')

    def test_search_questions(self):
      response = self.client().post('/searched_questions', json={'searchTerm': 'title'})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertTrue('title' in data['questions'][0]['question'].lower())

    def test_negative_search_questions_no_search_term(self):
      response = self.client().post('/searched_questions', json={})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 400)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Bad request')
    
    def test_negative_search_questions_get_method(self):
      response = self.client().get('/searched_questions', json={'searchTerm': 'title'})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 405)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Method not allowed for this endpoint')

    def test_add_question(self):
      response = self.client().post('/questions', json={'question': 'New question', 'answer': 'New answer', 'category':1, 'difficulty':1})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertTrue(data['added'])

    def test_negative_add_question_incomplete_params(self):
      response = self.client().post('/questions', json={'question': '', 'category':1, 'difficulty':1})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 400)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Bad request')

    def test_negative_add_question_method_not_allowed(self):
      response = self.client().post('/questions/1', json={'question': 'New question', 'answer': 'New answer', 'category':1, 'difficulty':1})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 405)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Method not allowed for this endpoint')

    def test_delete_question(self):
      response = self.client().post('/questions', json={'question': 'New question', 'answer': 'New answer', 'category':1, 'difficulty':1})
      data = json.loads(response.data)
      id_to_delete = data['added']
      
      response = self.client().delete(f'/questions/{id_to_delete}')
      data = json.loads(response.data)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(data['deleted'], id_to_delete)

    def test_negative_delete_question_not_existing_question(self):
      response = self.client().delete(f'/questions/322')
      data = json.loads(response.data)
      self.assertEqual(response.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'Resource not found')

    def test_get_quizzes(self):
      previous_questions = [9, 12, 23]
      quiz_category = 4
      response = self.client().post('/quizzes', json={'previous_questions': previous_questions, 'quiz_category': quiz_category})
      data = json.loads(response.data)

      self.assertEqual(response.status_code, 200)
      self.assertEqual(data['question']['category'], quiz_category)
      self.assertTrue(data['question']['id'] not in previous_questions)


    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()