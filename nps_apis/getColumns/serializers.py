from rest_framework import serializers  # searlizes are used to convert python objects to JSON and vice versa
from .models import *  # import all models from the models.py file
from userAPIs.models import User  # IMPORTANT: import the User model from userAPIs.models


class xmlfileSerializer(serializers.ModelSerializer):
    xmlfile = serializers.FileField()

    class Meta:  # meta is used to define the model and fields to be serialized inside the class
        model = xmlFile  # define the model to be serialized
        fields = "__all__"  # all fields are serialized


class getColumnsSerializer(serializers.ModelSerializer):  # create a class for serializing the data
    file = serializers.FileField()  # create a file field
    fileColumn = serializers.JSONField()  # create a JSON field

    class Meta:  # meta is used to define the model and fields to be serialized inside the class
        model = File_upload  # define the model to be serialized
        fields = "__all__"  # all fields are serialized


class dbConnectSerializer(serializers.ModelSerializer):  # dbConnectSerializer class

    class Meta:  # meta is used to define the model and fields to be serialized inside the class
        model = t_datasource_config  # define the model to be serialized
        fields = '__all__'  # all fields are serialized


class getdbFieldSerializer(serializers.ModelSerializer):  # getdbFieldSerializer class
    dbfield = serializers.JSONField()  # create a JSON field to store the db field

    class Meta:  # meta is used to define the model and fields to be serialized inside the class
        model = dbField  # define the model to be serialized
        fields = '__all__'  # all fields are serialized


class getCategorySerializer(serializers.ModelSerializer):  # getCategorySerializer class
    getcategory = serializers.JSONField()  # define a JSON field to store the category values

    class Meta:  # meta is used to define the model and fields to be serialized inside the class
        model = getCategory  # define the model to be serialized
        fields = '__all__'  # all fields are serialized
