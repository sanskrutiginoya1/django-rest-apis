import psycopg2  # PostgreSQL database adapter
from django.utils import timezone  # timezone
from rest_framework import generics, permissions, status
# generics is used to create the list and the detail views
# permissions is used to create the permissions for the views
# status is used to create the status codes for the views

from rest_framework.decorators import permission_classes  # decorators is used to create the decorators for the views
from rest_framework.permissions import IsAuthenticated  # isauthenticated is used to create the permission for the views
from rest_framework.response import Response  # response is used to create the response for the views
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, SetNewPasswordSerializer, \
    ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LogoutSerializer
# import the serializers


from django.contrib.auth import login, authenticate  # authenticate is used to authenticate the user
from rest_framework import status, views  # status is used to create the status codes for the views
from django.contrib.auth.models import User  # User is used to create the user
from rest_framework_simplejwt.tokens import RefreshToken  # refresh token is used to generate a new token for the user
from .models import User  # User is used to create the user
from .utils import Util  # Util is used to create the Util class
from django.contrib.sites.shortcuts import get_current_site  # get_current_site is used to get the current site
from django.urls import reverse  # reverse is used to reverse the url
import jwt  # jwt is used to create the jwt token for the user authentication
from django.conf import settings  # settings is used to create the settings
from rest_framework.exceptions import AuthenticationFailed  # import the AuthenticationFailed exception
from drf_yasg.utils import swagger_auto_schema  # swagger_auto_schema is used to create the swagger_auto_schema
from drf_yasg import openapi  # openapi is used to create the openapi
from .renderers import UserRenderer  # UserRenderer is used to create the UserRenderer class
from django.utils.encoding import smart_str, force_str, smart_bytes, \
    DjangoUnicodeDecodeError  # smart_str and force_str are used to convert the data to string format
from django.contrib.auth.tokens import \
    PasswordResetTokenGenerator  # PasswordResetTokenGenerator is used to generate the password reset token
from django.utils.http import urlsafe_base64_encode, \
    urlsafe_base64_decode  # urlsafe_base64_decode and urlsafe_base64_encode are used to decode and encode the data
from django.contrib.sites.shortcuts import get_current_site  # get_current_site is used to get the current site
from django.db import connection  #


# Register API


class RegisterView(generics.GenericAPIView):

    def post(self, request):  # post is used to create the post method for the RegisterView class
        print(request.data)
        user = request.data

        is_verified = User._meta.get_field(
            'is_verified').get_default()  # is_verified is used to create the is_verified field
        is_active = User._meta.get_field('is_active').get_default()
        is_superuser = User._meta.get_field('is_superuser').get_default()
        created_at = timezone.now()
        updated_at = timezone.now()
        last_login = User._meta.get_field('last_login').get_default()
        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        company_name = request.POST.get('company_name')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        mobileno = request.POST.get('mobileno')
        domain_name = request.POST.get('domain_name')
        role_name = request.POST.get('role_name')
        role_mapping = request.POST.get('role_mapping')

        if User.objects.filter(email=email).exists():
            # if the email is already exist then return the response with the message and status code 400 bad request 
            return Response({'message': 'Email is already exist'}, status=status.HTTP_400_BAD_REQUEST)

        cursor = connection.cursor()
        try:  # try is used to create the try block
            cursor.execute("BEGIN ")  # initalize the cursor to connect to the database
            cursor.callproc("usersp", (f_name, l_name, email, is_verified, is_active, created_at, updated_at, password,
                                       company_name, mobileno, is_superuser, last_login, country, city, state,
                                       domain_name, role_name, role_mapping))

            cursor.execute("COMMIT")

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cursor.close()

        user = User.objects.get(email=request.data['email'])  # get the user object from the email
        token = RefreshToken.for_user(user).access_token  # get the token from the user object
        current_site = get_current_site(request).domain
        relativelink = reverse('email-verify')
        absurl = 'http://' + current_site + relativelink + "?token=" + str(
            token)  # get the current site and the relative link
        email_body = 'Hi ' + user.f_name + \
                     ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': email, 'email_subject': 'Verify you Email'}
        # create the dictionary data with the email body and the email subject

        Util.send_email(data)  # send the email

        # print("user is created")
        return Response(request.data, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):  # VerifyEmail is used to create the VerifyEmail class
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description',
                                           type=openapi.TYPE_STRING)

    def get(self, request):  # create the get method for the VerifyEmail class
        print(request.data)
        token = request.data['token']
        print(token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            print(user)
            print(user.is_verified)
            if not user.is_verified:
                user.is_verified = True
                user.is_active = True
                user.save()
                return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
            else:
                return Response({'email': 'email is already activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):  # create the post method for the LoginAPIView class
        user = User()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.get_or_create(email=email)[0]
        user.set_password(password)
        user.save()

        def get_tokens(email):
            user = User.objects.get(email=email)

            return {
                'refresh': user.tokens()['refresh'],
                'access': user.tokens()['access']
            }

        token = get_tokens(email)
        print(token)
        if user is not None:
            login(request, user)
            print(user)

        return Response({'tokens': token}, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):  # create the RequestPasswordResetEmail class
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', '')
        if User.objects.filter(email=email).exists():  # check if the user exists
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse('password-reset-complete', kwargs={'uidb64': uidb64, 'token': token})

            absurl = 'http://' + 'localhost:4200' + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                         absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your password'}
            Util.send_email(data)
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)

        else:  # if the user does not exist
            return Response({'message': 'Please enter the registered email'}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(generics.GenericAPIView):  # create the SetNewPasswordAPIView class
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(id=id)
            print(user)
            return Response({'success': True, 'message': 'Credentials valid', 'uidb64': uidb64, 'token': token},
                            status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid, please request a new one'},
                            status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):  # create the post method for the SetNewPasswordAPIView class

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):  # create the LogoutAPIView class
    serializer_class = LogoutSerializer

    permission_classes = (permissions.AllowAny,)  # create the permission_classes class for the LogoutAPIView class

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


class userProfileData(views.APIView):  # create the userProfileData class
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description',
                                           type=openapi.TYPE_STRING)

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')  # get the token from the header
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)  # decode the token
            user = User.objects.get(id=payload['user_id'])  # get the user from the token
            print(user)
            if user.is_verified:
                status_code = status.HTTP_200_OK

                # create response to send back to the user
                response = {
                    'success': 'true',
                    'status code': status_code,
                    'message': 'User profile fetched successfully',
                    'data': [{
                        'id': user.id,
                        'Name': user.f_name,
                        'Lastname': user.l_name,
                        'email': user.email,
                    }]
                }
                print(response)
                return Response(response, status_code)  # return the response
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
