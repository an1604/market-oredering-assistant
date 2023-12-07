import re
import threading
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By

from app import create_app, db, fake
from app.Models.Role import Role
from app.Models.User import User


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start Chrome
        try:
            cls.client = webdriver.Chrome()
        except:
            pass

            # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")
            db.create_all()
            Role.insert_roles()
            fake.users(10)
            fake.posts(10)

            # add an administrator user
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='john@example.com',
                         username='john', password='cat',
                         role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            # TODO: FIX THE SERVER RUN PROBLEM ON THE OTHER THREAD
            cls.server_thread = threading.Thread(
                target=cls.app.run, kwargs={'debug': 'false',
                                            'use_reloader': False,
                                            'use_debugger': False})
            cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the Flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            cls.destroy_db()

            # remove application context
            cls.app_context.pop()

    @staticmethod
    def destroy_db():
        db.drop_all()
        db.session.remove()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.navigate_to_home_page()
        self.navigate_to_login_page()
        self.login()

        # navigate to the user's profile page
        self.client.find_element_by_link_text('Profile').click()
        self.assertIn('<h1>john</h1>', self.client.page_source)

    def navigate_to_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\\s+Stranger!', self.client.page_source))

    def navigate_to_login_page(self):
        self.client.find_element_by_link_text('Log In').click()
        self.assertIn('<h1>Login</h1>', self.client.page_source)

    def login(self):
        self.client.find_element(By.NAME, 'email').send_keys('john@example.com')
        self.client.find_element(By.NAME, 'password').send_keys('cat')
        self.client.find_element(By.NAME, 'submit').click()
        self.assertTrue(re.search('Hello\\s+john!', self.client.page_source))
