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
        self.database_path ="postgres://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)
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

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    
    def delete_question(self):
        newQuestion = Question(question='what is your name', answer='Tong Guan',difficulty=1 , category=6)
        newQuestion.insert()

        res = self.client().delete(f'/questions/{newQuestion.id}')
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == newQuestion.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], {newQuestion.id})
        self.assertEqual(question, None)
    
                        
    def test_404_question_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
    
    def test_create_question(self):
        newQuestion = {
            'id': 35,
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1}
        res = self.client().post('/questions', json=newQuestion)
        data = json.loads(res.data)
        
        question = Question.query.filter_by(id=data['created']).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(question)
    
    def test_create_question_error(self):
        questions_before = Question.query.all()
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        questions_after = Question.query.all()
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(questions_after) == len(questions_before))

 
    def test_search_question(self):
        res = self.client().post('/search', json={'searchTerm':'What'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']>0, True)
        self.assertIsNotNone(data['questions'])                        
    
    def test_search_question_without_result(self):
        res = self.client().post('/search', json={'searchTerm':'abcdefghi'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']==0, True)
        self.assertIsNotNone(data['questions'])   
    
    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']>0, True)
        self.assertEqual(data['category'], 2)
    
    def test_404_get_question_by_invalid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
    
    def test_get_random_quiz(self):
        new_quiz = {'quiz_category': {'type': 'Entertainment', 'id': 5},'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_get_random_quiz_error(self):
        new_quiz = {}
        res = self.client().post('/quizees', json=new_quiz)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
        
        
        
        
        
        
    
        
        
        
        
        

        


        

        

        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()