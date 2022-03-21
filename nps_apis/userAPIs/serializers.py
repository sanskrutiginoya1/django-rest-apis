from rest_framework import serializers  # import the serializers module for serializing the data
from .models import User, Address  # import the User and Address model from the models.py file
from django.contrib import auth  # import the auth model for authentication and authorization
from rest_framework.exceptions import AuthenticationFailed  # import the AuthenticationFailed exception
from rest_framework_simplejwt.tokens import RefreshToken, TokenError  # TokenError is used to handle the token error
from django.contrib.auth.tokens import \
    PasswordResetTokenGenerator  # PasswordResetTokenGenerator is used to generate the password reset token
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
# smart_str and force_str are used to convert the data to string format
# smart_bytes and DjangoUnicodeDecodeError are used to handle the error
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


# urlsafe_base64_decode and urlsafe_base64_encode are used to decode and encode the data


# this are schemas with complete validation for database for the users model

# Register Serializer
class AddressSerializer(serializers.ModelSerializer):  # create a class for the serializer
    # city = serializers.PrimaryKeyRelatedField( read_only=True) 
    class Meta:  # create a class for the meta
        model = Address
        fields = ['city', 'state', 'country']


# Register Serializer that is used to register the user
class RegisterSerializer(serializers.ModelSerializer):
    # user_data = AddressSerializer(many=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'password', 'company', 'mobileno']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):  # validate the data
        name = attrs.get('name', '')
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        # confirmpassword = attrs.get('confirmpassword', '')
        company = attrs.get('company', '')
        city = attrs.get('city', '')
        state = attrs.get('state', '')
        country = attrs.get('country', '')
        mobileno = attrs.get('mobileno', '')

        if not username.isalnum():  # check if the username is alphanumeric
            raise serializers.ValidationError('The username should only contain alphanumeric characters')

        return attrs  # return the validated data

    def create(self, validated_data):  # create the user
        return User.objects.create(**validated_data)  # call the create method and vallidate function of the User model


class EmailVerificationSerializer(serializers.ModelSerializer):  # EmailVerificationSerializer class
    token = serializers.CharField(min_length=555)

    class Meta:
        model = User
        field = ['token']


class LoginSerializer(serializers.ModelSerializer):  # LoginSerializer class
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'password', 'tokens']


class ResetPasswordEmailRequestSerializer(serializers.Serializer):  # ResetPasswordEmailRequestSerializer class
    email = serializers.EmailField(min_length=2)

    # redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):  # SetNewPasswordSerializer class
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)  #
    confirm_password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        # fields = ['password', 'token']
        fields = ['password', 'confirm_password', 'token', 'uidb64']

    def validate(self, attrs):  # validate the data
        if attrs.get('password') != attrs.get('confirm_password'):
            res = serializers.ValidationError({'message': 'Those passwords does not match'})
            res.status_code = 200
            raise res
        try:  # try to decode the data
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))  # decode the uidb64 and convert it to string format
            user = User.objects.get(id=id)
            if password != confirm_password:
                raise AuthenticationFailed("Password Does not match", 401)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):  # LogoutSerializer class
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')
