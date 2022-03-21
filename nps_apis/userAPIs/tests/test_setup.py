from rest_framework.test import APITestCase # allows you to add test cases to your project
from django.urls import reverse  # reverse relation allows you to reverse the url
from faker import Faker  # faker is a fake data generator

#from userAPIs.models import User


class TestSetUp(APITestCase): # create a class for the test set up

    def setUp(self): # setUp method is used to register the user
        self.register_url = reverse('register') 
        self.login_url = reverse('login') 
        self.fake = Faker()

        self.user_data = {
            'email': self.fake.email(), 
            'username': self.fake.email().split('@')[0],
            'password': self.fake.email(),
        }

        return super().setUp() # Set up method is used to register the user

    def tearDown(self): # tearDown method is used to unregister the user
        return super().tearDown() # tearDown method is used to unregister the user