import json
import os
from io import StringIO
import psycopg2
import sqlalchemy
from django.shortcuts import render
from rest_framework.parsers import FileUploadParser

from .serializers import *
from rest_framework.response import Response
from rest_framework import status, generics, mixins, views
import pandas as pd
from django.db import connection
import csv
from .sentiment import *
import dask.dataframe as dd
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from userAPIs.models import User
# User = get_user_model()
from userAPIs.views import LoginAPIView as lv  # user       # loginAPIView is a class to get the user model

engine = sqlalchemy.create_engine('postgresql://postgres:root9825@122.169.107.192:5432/test', pool_pre_ping=True)


# create a connection to the database and return the connection object

def dataClean(df1):  # data cleaning function
    df1['cleaned_reviews'] = df1['review'].apply(clean)  # clean the reviews
    df1['POS tagged'] = df1['cleaned_reviews'].apply(token_stop_pos)  # POS tagging
    df1['Lemma'] = df1['POS tagged'].apply(lemmatize)  # lemmatize the reviews
    df1['polarity'] = df1['Lemma'].apply(getPolarity)  # get the polarity of the reviews
    df1['sentiment'] = df1['polarity'].apply(analysis)  # get the sentiment of the reviews
    return df1  # return the dataframe


def category_keywords(data):
    lexicon = data
    classes = list(lexicon.keys())
    # print("222222222222")
    return classes, lexicon


def sentiment(df1, lexicon, classes, file_idx):
    lexicon_vectors = {}
    for aspect, descriptive_words in lexicon.items():
        lexicon_vectors[aspect] = construct_dim_vector(descriptive_words)

    def select_aspect(review):  # select_aspect is a function to get the sentiment of the reviews
        vec = construct_sentence_vector(str(review))  # vec is a vector to get the sentiment of the reviews
        sims = np.array(list(map(lambda lex_v: cosine_sim(vec, lex_v),
                                 lexicon_vectors.values())))  # sims is a vector of np.array that contains the cosine similarity of the reviews
        max_cat = np.argmax(
            sims) if sims.max() > 0.39 else -1  # max_cat is a vector max value from np.argmax 0.39 is the threshold
        return max_cat

    predicted_aspects = dd.from_pandas(df1['review'], npartitions=4).apply(select_aspect, meta=(
        'review',
        'object')).compute()  # predicted_aspects is dask dataframe that creats new 4 partitions and apply the function to each partition
    df1['category'] = predicted_aspects
    df1['category'] = df1['category'].apply(
        lambda ix: classes[ix])  # df1['category'] is a vector that contains the category of the reviews
    # a = []
    # for i in df1['category']:
    #
    #     for key, value in lexicon.items():
    #         if i == key:
    #             a.append(value)
    #
    # df1['keywords'] = a
    # df1['keywords'] = df1['keywords'].astype(str)
    df1['file_id'] = file_idx
    final_data = pd.DataFrame(df1[['review', 'category', 'polarity', 'sentiment', 'file_id']])
    final_df = pd.DataFrame(final_data, columns=['review', 'category', 'polarity', 'sentiment', 'file_id'])
    print("SENTIMENT ...........................")
    # engine = sqlalchemy.create_engine('postgresql://postgres:root9825@122.169.107.192:5432/demodb3')
    final_df.to_sql(name='final_data', con=engine, index=False, if_exists='replace')
    return final_df


tablename = {}
file_id = ()


class xmlfileview(generics.CreateAPIView):
    serializer_class = xmlfileSerializer
    # parser_classes = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:  #
            payload = jwt.decode(token,
                                 settings.SECRET_KEY)  # payload is a dictionary to decode the token to get the user id
            user = User.objects.get(id=payload['user_id'])  # user is a function to get the user model

            if user.is_verified:
                print(user)
                # serializer = self.get_serializer(data=request.data)
                # serializer.is_valid(raise_exception=True)
                # serializer.save()
                # file = serializer.validated_data['file']
                # print(file)
                file_obj = request.data['file']
                df = pd.read_xml(file_obj)
                print(df)
                return Response({'msg': 'file sent'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class File_uploadview(generics.CreateAPIView):  # File_uploadview is a class to upload the file
    serializer_class = getColumnsSerializer  #

    def post(self, request, *args, **kwargs):  # post is a request method function to upload the file
        token = request.META.get('HTTP_AUTHORIZATION')
        try:  #
            payload = jwt.decode(token,
                                 settings.SECRET_KEY)  # payload is a dictionary to decode the token to get the user id
            user = User.objects.get(id=payload['user_id'])  # user is a function to get the user model

            if user.is_verified:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                # serializer.save()
                user_id = user.id
                file = serializer.validated_data['file']
                fileColumn = serializer.validated_data['fileColumn']
                filename = request.data['filename']
                filetype = request.data['filetype']

                if filetype == 'application/vnd.ms-excel':
                    df = pd.read_csv(file)
                elif filetype == 'application/json':
                    df = pd.read_json(file)
                elif filetype == 'text/plain':
                    df = pd.read_csv(file, delimiter=",")
                elif filetype == 'text/xml':
                    df = pd.read_xml(file)
                else:
                    return Response({'msg': 'enter file with valid format'}, status=status.HTTP_400_BAD_REQUEST)

                cursor = connection.cursor()

                a = []
                for i in fileColumn.values():
                    for col_name, value in df.items():
                        if i == col_name:
                            a.append(value)

                df = pd.DataFrame(a).astype(str)
                df = df.transpose()
                df.columns = fileColumn.keys()

                jsn = []
                for key, value in fileColumn.items():  # for each key and value in the fileColumn dictionary
                    jsn.append(value)  # append the value to the jsn list
                print(jsn)
                jsn = str(jsn)
                try:
                    global file_id
                    cursor.execute("BEGIN")
                    cursor.callproc("f_file", (user_id, filename, filetype, jsn))
                    file_id = cursor.fetchone()
                    cursor.execute("COMMIT")
                    df['file_id'] = file_id[0]
                    df['user_id'] = user_id
                    df.to_sql(name='file_data', con=engine, index=False, if_exists='replace')

                except (
                        Exception,
                        psycopg2.DatabaseError) as error:  # in except is a function to handle the psycopg2 error
                    print(error)
                finally:
                    cursor.close()
                print(file_id[0])

                return Response({'msg': 'review and star are store into database'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class DbConnect(generics.CreateAPIView):  # dbconnect is a class to connect the database
    serializer_class = dbConnectSerializer

    def post(self, request, *args, **kwargs):  # post is a request method function to connect the database
        global tablename
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            payload = jwt.decode(token,
                                 settings.SECRET_KEY)  # payload is a dictionary to decode the token to get the user id
            user = User.objects.get(id=payload['user_id'])  # user is a function to get the user model

            if user.is_verified:  # if user is verified then the user can connect the database

                serializer = self.get_serializer(data=request.data)  # serializer is a function to get the serializer
                serializer.is_valid(
                    raise_exception=True)  # serializer.is_valid(raise_exception=True) is a function to validate the data
                # serializer.save()

                # below code is to get the database details to connect with the user's database
                db = serializer.validated_data['db']
                host = serializer.validated_data['host']
                port = serializer.validated_data['port']
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                dbname = serializer.validated_data['dbname']
                tablename = serializer.validated_data['tablename']
                user_id = user.id
                cursor = connection.cursor()

                # below code is to insert data into the database
                try:
                    cursor.execute("BEGIN ")
                    print(user_id)
                    # below code is to insert the database name, host, port, username, password, database name and table name into the database 
                    cursor.callproc("dbconnectsp1", (db, host, port, username, password, dbname, tablename, user_id))
                    cursor.execute("COMMIT")

                except (
                        Exception,
                        psycopg2.DatabaseError) as error:  # in except is a function to handle the psycopg2 error
                    print(error)
                finally:
                    cursor.close()

                engine = sqlalchemy.create_engine(
                    f"{db}://{username}:{password}@{host}:{port}/{dbname}")  # engine is a function to create the engine

                data = engine.execute(
                    f'''SELECT * FROM "{tablename}"''')  # data is a function to get the data from the database
                print(data)
                outfile = open("table.csv", 'w', encoding="utf-8")
                outcsv = csv.writer(outfile)

                outcsv.writerow(data.keys())
                outcsv.writerows(
                    data.fetchall())  # outcsv.writerows(data.fetchall()) is a function to write the data into the csv file
                outfile.close()

                return Response(data.keys(), status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class getdbFields(generics.CreateAPIView):  # getdbFields is a class to get the database fields
    serializer_class = getdbFieldSerializer  # serializer_class is a function to get the serializer

    def post(self, request, *args, **kwargs):  # post is a request method function to get the database fields
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])

            if user.is_verified:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                dbfield = serializer.validated_data['dbfield']
                # table_name = request.data['table_name']
                print(tablename)
                user_id = user.id
                df = pd.read_csv('table.csv')  # .decode('latin-1').encode("utf-8")
                # print(df)
                a = []

                for i in dbfield.values():
                    for col_name, value in df.items():  # df.items() is a function to get the column name and value
                        if i == col_name:
                            a.append(value)

                df = pd.DataFrame(a)
                df = df.transpose()
                # print(df)
                df.columns = dbfield.keys()
                jsn = []
                for key, value in dbfield.items():  # for key, value in dbfield.items() is a function to get the key and value
                    jsn.append(value)
                print(jsn)
                jsn = str(jsn)
                filetype = 'database'
                cursor = connection.cursor()  # establish the connection
                try:
                    global file_id
                    cursor.execute("BEGIN ")
                    cursor.callproc("f_file", (user_id, tablename, filetype, jsn))
                    file_id = cursor.fetchone()
                    print(type(file_id))
                    cursor.execute("COMMIT")
                    df['file_id'] = file_id[0]
                    df['user_id'] = user_id
                    print(df)
                    df.to_sql(name='file_data', con=engine, index=False, if_exists='replace')

                except (
                        Exception,
                        psycopg2.DatabaseError) as error:  # in except is a function to handle the psycopg2 error
                    print(error)
                finally:  # finally is a function to close the connection
                    cursor.close()
                return Response({'msg': 'DB review and star are store into database'},
                                status=status.HTTP_200_OK)  # Response is a function to send the response

        except jwt.ExpiredSignatureError as identifier:  # in except is a function to handle the jwt error
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)  # S
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class getCategoryValues(generics.CreateAPIView):  # getCategoryValues is a class to get the category values
    serializer_class = getCategorySerializer  # serializer_class is a function to get the serializer

    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')  # meta is a function to get the meta data
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)  # payload is a function to decode the token
            user = User.objects.get(id=payload['user_id'])
            print(file_id[0])
            if user.is_verified:  # if user.is_verified is a function to check the user is verified
                serializer = self.get_serializer(data=request.data)  # serializer is a function to get the serializer
                serializer.is_valid(raise_exception=True)
                user_id = user.id
                getcategory = serializer.validated_data['getcategory']
                classes, lexicon = category_keywords(getcategory)
                # print(type(getcategory))
                df = pd.DataFrame(getcategory.items())
                df.columns = ['cat', 'keyw']
                # print(str(df['keyword']))
                df['keyw'] = df['keyw'].apply(lambda x: ','.join(map(str, x)))
                df = df.assign(orderssplit=df['keyw'].str.split(',')).drop("keyw", axis=1).rename(
                    columns={"orderssplit": "keyw"})
                df = df.explode('keyw')
                df['temp_id'] = df.index
                print(df)
                df.to_sql("temp_data1", con=engine, index=False, if_exists='replace')
                print("data inserted")
                print(user_id)
                cursor = connection.cursor()

                try:
                    cursor.execute("BEGIN")
                    cursor.execute(f"select f_category({user_id})")
                    cursor.execute("COMMIT")

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)

                finally:
                    cursor.close()

                data = engine.execute(f'''SELECT review, star FROM "file_data" where user_id = {user_id} ''')
                a = data.fetchall()
                var = []
                for x in a:
                    var.append(x)

                df1 = pd.DataFrame(var)
                df1.columns = data.keys()
                data = dataClean(df1)
                result = sentiment(data, lexicon, classes, file_id[0])
                print(result)
                # serializer.save()
                return Response(result, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
