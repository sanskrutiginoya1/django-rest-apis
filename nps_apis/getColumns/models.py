from django.db import models


# in django models we can create tables and store data in the tables

class xmlFile(models.Model):  # table for file upload
    xmlfile = models.FileField()


class File_upload(models.Model):  # table for file upload
    file = models.FileField()
    fileColumn = models.JSONField(max_length=500)


class t_datasource_config(models.Model):  # table for database connection
    # user_id = models.IntegerField()
    db = models.CharField(max_length=100)
    dbname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    port = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    tablename = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class dbField(models.Model):  # table for database fields
    # getcategory = models.JSONField(max_length=500)
    dbfield = models.JSONField(max_length=100)


class getCategory(models.Model):  # table for category values
    getcategory = models.JSONField(max_length=500)
# fileColumn = models.CharField(max_length=100)

