#!/usr/bin/env python3
'''
File: tests.py
Authors: 
    2015-03-17 - C.Shaw <shaw.colin@gmail.com> 
Description: 
    Test suite for angryhos.com, makes use of selenium to drive
    testing procedures.
'''
import os
import shutil
from datetime import datetime
from pytz import utc
import unittest

from app import db, bc
import app.model
from app.model import User, Role

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def recreateDatabase():
    """
    Function to recreate database tables, make a user for testing,
    and create application roles.
    """
    print("Dropping and recreating database tables.")
    db.drop_all()
    db.create_all()
    print("Cleansing user uploads folder.")
    shutil.rmtree('app/static/uploads/1/')
    os.mkdir('app/static/uploads/1')
    os.chmod('app/static/uploads/1', mode=0o777)
    print("Creating application roles and first user.")
    user = User(password=bc.generate_password_hash('12345678', rounds=12),
            user_name='tester1')
    active_role = Role(name="Active", description="Active user.")
    verified_role = Role(name="Verified",
            description="User with a verified email.")
    admin_role = Role(name="Administrator", description="Administrator.")
    db.session.add(admin_role)
    db.session.add(active_role)
    db.session.add(verified_role)
    db.session.flush()
    user.roles.append(admin_role)
    user.roles.append(active_role)
    user.roles.append(verified_role)
    db.session.add(user)
    db.session.commit()

recreateDatabase()

class TestAngryHos(unittest.TestCase):
    """
    Test case for angryhos.com
    """
   
    def setUp(self):
        """
        Resets everything and prepares test driver.
        """
        # Prepares driver for browser automation.
        self.firefox  = webdriver.Firefox()

    def test_logInOut(self):
        """
        Tests for confirming user functionality:
            signing in
            create post without title
            creat post without picture
            creat post with picture
            creat post with multiple pictures
            creat post with too many pictures
            add picture to post
        """

        ff = self.firefox

        # User login.
        ff.get("localhost:8080/index")
        ff.find_element_by_id('login').click()
        input = ff.find_element_by_id('user_name')
        input.send_keys("tester1")
        input = ff.find_element_by_id('password')
        input.send_keys("12345678")
        input.submit()
        success_alert = ff.find_element_by_class_name(
                'alert-success')

        # User logout.
        ff.find_element_by_id('logout').click()
        success_alert = ff.find_element_by_class_name(
                'alert-success')

    def test_postActions(self):
        """
        docstring for test_postActions
        """

        ff = self.firefox

        # User login.
        ff.get("localhost:8080/index")
        ff.find_element_by_id('login').click()
        input = ff.find_element_by_id('user_name')
        input.send_keys("tester1")
        input = ff.find_element_by_id('password')
        input.send_keys("12345678")
        input.submit()
        success_alert = ff.find_element_by_class_name(
                'alert-success')

        # Create post without title.
        ff.find_element_by_id('create-post').click()
        input = ff.find_element_by_id('title')
        input.submit()
        ff.find_element_by_class_name('alert-warning')

        # Create post without picture
        input = ff.find_element_by_id('title')
        input.send_keys('Title 1')
        input = ff.find_element_by_id('subtitle')
        input.send_keys('Subtitle 1')
        input = ff.find_element_by_id('body')
        body = \
                """
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
                do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                Ut enim ad minim veniam, quis nostrud exercitation ullamco 
                laboris nisi ut aliquip ex ea commodo consequat. Duis aute
                irure dolor in reprehenderit in voluptate velit esse cillum
                dolore eu fugiat nulla pariatur. Excepteur sint occaecat
                cupidatat non proident, sunt in culpa qui officia deserunt
                mollit anim id est laborum.
                """
        input.send_keys(body)
        input.submit()
        ff.find_element_by_class_name('alert-success')

        # Create post with one picture.
        ff.find_element_by_id('create-post').click()
        input = ff.find_element_by_id('pics')
        input.send_keys(
                '/home/colin/Pictures/1240565_406439336124583_1778167961_n.jpg')
        input = ff.find_element_by_id('title')
        input.send_keys('Title 2')
        input = ff.find_element_by_id('subtitle')
        input.send_keys('Subtitle 2')
        input = ff.find_element_by_id('body')
        body = \
                """
                Sed ut perspiciatis unde omnis iste natus error sit voluptatem
                accusantium doloremque laudantium, totam rem aperiam, eaque
                ipsa quae ab illo inventore veritatis et quasi architecto 
                beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem
                quia voluptas sit aspernatur aut odit aut fugit, sed quia 
                consequuntur magni dolores eos qui ratione voluptatem sequi 
                nesciunt. Neque porro quisquam est, qui dolorem ipsum quia 
                dolor sit amet, consectetur, adipisci velit, sed quia non 
                numquam eius modi tempora incidunt ut labore et dolore magnam 
                aliquam quaerat voluptatem. Ut enim ad minima veniam, quis 
                nostrum exercitationem ullam corporis suscipit laboriosam, 
                nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum 
                iure reprehenderit qui in ea voluptate velit esse quam nihil 
                molestiae consequatur, vel illum qui dolorem eum fugiat quo 
                voluptas nulla pariatur?
                """
        input.send_keys(body)
        input.submit()
        ff.find_element_by_class_name('alert-success')
        
        # Add second picture to post.
        ff.get('localhost:8080/edit/2')
        input = ff.find_element_by_id('pics')
        input.send_keys('/home/colin/Pictures/2014-12-02-123635.jpg')
        ff.find_element_by_id('submit').submit()
        ff.find_element_by_class_name('alert-success')

        # Add third picture to post and change picture ordering.
        # Picture is a duplicate to test renaming.
        ff.get('localhost:8080/edit/2')
        input = ff.find_element_by_id('pics')
        input.send_keys('/home/colin/Pictures/2014-12-02-123635.jpg')
        ff.find_element_by_class_name('down').click()
        ff.find_element_by_id('submit').submit()
        ff.find_element_by_class_name('alert-success')
        # Add fourth picture to post, rename picture.
        ff.get('localhost:8080/edit/2')
        input = ff.find_element_by_id('pics')
        input.send_keys(
                '/home/colin/Pictures/45e2ea709e55687d60bcb6008efb6081.jpg')
        title = ff.find_element_by_id('pic_forms-2-title')
        title.clear()
        title.send_keys("ticket2")
        ff.find_element_by_id('submit').submit()
        ff.find_element_by_class_name('alert-success')

        # Add fifth picture to post, rename pictures, and change
        # picture ordering, and change cover choice.
        ff.get('localhost:8080/edit/2')
        ff.find_element_by_id('pics').send_keys(
                '/home/colin/Pictures/'
                '811-Get_money_fuck_bitches_smoke_trees.jpg')
        titles = ff.find_elements_by_class_name('title')
        names = ["ticket 1", "twins", "ticket 2", "dino", "wisdom"]
        for title, name in zip(titles, names):
            title.clear()
            title.send_keys(name)
        ups = ff.find_elements_by_class_name('up')
        downs = ff.find_elements_by_class_name('down')
        ups[3].click()
        ups[3].click()
        ups[3].click()
        downs[1].click()
        downs[2].click()
        ups[4].click()
        ff.find_element_by_name('choice').click()
        ff.find_element_by_id('submit').submit()
        ff.find_element_by_class_name('alert-success')

        # Add three more pictures, delete one, rename some,
        # change ordering again, and change cover choice again.
        files = ['dafsdfasf.jpeg', 'images.jpeg',
                'Ger-ma-bethi-ho-bag-to-side-per-rakh-do.jpg']
        names = ['nympho', 'mean girl', 'durrrr']
        for file in files:
            ff.get('localhost:8080/edit/2')
            ff.find_element_by_id('pics').send_keys(
                    '/home/colin/Pictures/' + file)
            ff.find_element_by_id('submit').submit()
            ff.find_element_by_class_name('alert-success')
        ff.get('localhost:8080/edit/2')
        ff.find_element_by_id('pic_forms-4-delete').click()
        titles = ff.find_elements_by_class_name('title')
        for i in range(3):
            titles[len(titles) - 1 - i].clear()
            titles[len(titles) - 1 - i].send_keys(names[i])
        ups = ff.find_elements_by_class_name('up')
        downs = ff.find_elements_by_class_name('down')
        ups[4].click()
        ups[4].click()
        ups[4].click()
        downs[3].click()
        downs[3].click()
        ff.find_element_by_id('pics').send_keys(
                '/home/colin/Pictures/resized_ap_gqhunter.jpg')
        ff.find_elements_by_name('choice')[4].click()
        ff.find_element_by_id('submit').submit()
        ff.find_element_by_class_name('alert-success')

        # Add one picture.
        ff.get('localhost:8080/edit/2')
        ff.find_element_by_id('pics').send_keys(
                '/home/colin/Pictures/windows.png')
        ff.find_element_by_id('submit').submit()
        ff.find_element_by_class_name('alert-warning')

    def tearDown(self):
        """
        Close driver connection and clean up.
        """
        self.firefox.quit()

if __name__ == '__main__':
    unittest.main()
