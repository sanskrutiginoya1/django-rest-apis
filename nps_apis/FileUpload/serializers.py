from rest_framework import serializers
'''from .models import File, DataGet


class FileUploadSerializer(serializers.Serializer):
    business_category = serializers.CharField()
    file = serializers.FileField()
    data = serializers.DictField()
    #category = serializers.CharField()
    #sub_category = serializers.CharField()
    # print(file)


class SaveFileSerializer(serializers.Serializer):
    class Meta:
        model = File
        fields = "__all__"'''


'''class DataGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataGet
        fields = ('id', 'review', 'category', 'sub_category')
    id = serializers.CharField(max_length=100)
    review = serializers.CharField(max_length=300)
    category = serializers.CharField(max_length=200)
    sub_category = serializers.CharField(max_length=200)'''
