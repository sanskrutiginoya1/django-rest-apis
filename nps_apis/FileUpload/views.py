'''# import nlp
import psycopg2
from nltk.corpus import stopwords
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import FileUploadSerializer, SaveFileSerializer
import pandas as pd
import json
from .models import File, DataGet
from django.http.response import JsonResponse
# import tensorflow.keras
from sqlalchemy import create_engine
# from keras.models import load_model
# from keras.preprocessing.text import Tokenizer
# from sklearn.preprocessing import LabelEncoder
# from tensorflow.keras.models import load_model

from nltk import pos_tag
import nltk

nltk.download('stopwords')
import sqlalchemy
from .sentiment import clean, token_stop_pos, getPolarity, getSubjectivity, lemmatize, analysis, keyword_extraction, \
    classes_lexicon, construct_dim_vector, euclidian_distance, construct_sentence_vector, cosine_sim
import dask.dataframe as dd
import numpy as np

# os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

# vocab_size = 6000 # We set a maximum size for the vocabulary


class UploadFileView(generics.CreateAPIView):
  serializer_class = FileUploadSerializer

  def post(self, request, *args, **kwargs):
    try:
      sentiment_model_path = "D:\\NPS_API\\nps_apis\\model\\sentiment_model.h5"
      aspect_model_path = "D:\\NPS_API\\nps_apis\\model\\aspect_model.h5"
      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      file = serializer.validated_data['file']
      test_reviews = pd.read_csv(file, index_col=False)
      test_review_list = test_reviews.stack().tolist()
      #print(test_review_list)
      #reader.to_csv('file_name.csv', encoding='utf-8')
      test_reviews = [review.lower() for review in test_review_list]
      #print(test_reviews)
      reconstructed_sentiment_model = load_model(sentiment_model_path)
      reconstructed_aspect_model = load_model(aspect_model_path)

      # Sentiment preprocessing
      #print("Sentiment")
      tokenizer = Tokenizer()
      label_encoder_2 = LabelEncoder()
      tokenizer.fit_on_texts(test_reviews)
      #print("HOOOOO")

      label_encoder = LabelEncoder()
      tokenizer.fit_on_texts(test_reviews)

      test_sentiment_terms = []
      for review in nlp.pipe(test_reviews):

        if review.is_parsed:
          test_sentiment_terms.append(' '.join([token.lemma_ for token in review if (not token.is_stop and not token.is_punct and (token.pos_ == "ADJ" or token.pos_ == "VERB"))]))
        else:
          test_sentiment_terms.append('')
      #print("HOIIIIIIIIIIIIIiIIII")
      test_sentiment_terms = pd.DataFrame(tokenizer.texts_to_matrix(test_sentiment_terms))
      #print(test_sentiment_terms)
      test_sentiment = label_encoder_2.inverse_transform(reconstructed_sentiment_model.predict_classes(test_sentiment_terms)).astype('int32')
      print(test_sentiment)
      #aspect processing

      print("Aspect term")
      test_aspect_terms = []
      for review in nlp.pipe(test_reviews):
        chunks = [(chunk.root.text) for chunk in review.noun_chunks if chunk.root.pos_ == 'NOUN']
        test_aspect_terms.append(' '.join(chunks))
      test_aspect_terms = pd.DataFrame(tokenizer.texts_to_matrix(test_aspect_terms))
      print(test_aspect_terms)
      print("HOIIIIIIIIIIIIIIIIIIIIIIII")

      #model output
      test_aspect_categories = label_encoder.inverse_transform(reconstructed_aspect_model.predict_classes(test_aspect_terms))
      test_sentiment = label_encoder_2.inverse_transform(reconstructed_sentiment_model.predict_classes(test_sentiment_terms))
      print(test_sentiment)
      print(test_aspect_categories)
      return Response(status=status.HTTP_200_OK)

    except Exception as e:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    #return (predictions)




class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            # print("REQ :",request.POST['name'])
            serializer.is_valid(raise_exception=True)
            business_category = serializer.validated_data['business_category']
            file = serializer.validated_data['file']
            data = serializer.validated_data['data']
            # data = request.POST['data']
            # data = eval(data)
            # data1 = json.load(data)
            print(type(data))

            test_reviews = pd.read_csv(file)
            # print(test_reviews.head)

            test_reviews['cleaned_reviews'] = test_reviews['review'].apply(clean)
            test_reviews['POS tagged'] = test_reviews['cleaned_reviews'].apply(token_stop_pos)
            test_reviews['Lemma'] = test_reviews['POS tagged'].apply(lemmatize)
            test_reviews['keywords'] = test_reviews['review'].apply(keyword_extraction)
            test_reviews['polarity'] = test_reviews['Lemma'].apply(getPolarity)
            test_reviews['analysis'] = test_reviews['polarity'].apply(analysis)
            # print(test_reviews)
            classes, lexicon = classes_lexicon()
            # classes = list(data.keys())
            # lexicon = data
            # print(classes)
            # print(lexicon)
            lexicon_vectors = {}
            for aspect, descriptive_words in lexicon.items():
                lexicon_vectors[aspect] = construct_dim_vector(descriptive_words)

            # print(lexicon_vectors)

            def select_aspect(review):
                vec = construct_sentence_vector(str(review))
                sims = np.array(list(map(lambda lex_v: cosine_sim(vec, lex_v), lexicon_vectors.values())))
                max_cat = np.argmax(sims) if sims.max() > 0.39 else -1
                return max_cat

            predicted_aspects = dd.from_pandas(test_reviews['review'], npartitions=4).apply(select_aspect, meta=(
                'review', 'object')).compute()
            # print(predicted_aspects)
            test_reviews['aspect'] = predicted_aspects
            test_reviews['aspect'] = test_reviews['aspect'].apply(lambda ix: classes[ix])
            # print(test_reviews)
            a = []
            for i in test_reviews['aspect']:

                for key, value in lexicon.items():
                    if i == key:
                        # print("HIIII")
                        a.append(value)
                        # print(value)
            # print(a)
            test_reviews['sub_category'] = a
            test_reviews['sub_category'] = test_reviews['sub_category'].astype(str)
            final_data = pd.DataFrame(test_reviews[['review', 'aspect', 'sub_category', 'analysis']])
            print(final_data.columns)
            df = pd.DataFrame(final_data, columns=['review', 'aspect', 'sub_category', 'analysis'])
            # da_data = ["Great Service  Great Product",   "Vase",  "[leaks, leaky, tacky , too big, did not receive]",  "Positive"]
            # df1 = pd.DataFrame(da_data, columns= ['review', 'aspect', 'sub_category', 'analysis'])

            print(df)
            engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:root9825@122.169.107.192:5432/demodb3')
            print(engine.table_names())
            df.to_sql(name='flower_data1', con=engine, index=False, if_exists='append')

            return Response({'File': 'Successfully uploaded'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'File': 'Not uploaded'}, status=status.HTTP_400_BAD_REQUEST)


class dataget_list(generics.CreateAPIView):
    serializer_class = DataGetSerializer

    # parser_classes = (FileUploadParser,)
    print(serializer_class)

    def post(self, request, *args, **kwargs):

            serializer = self.get_serializer(data=request.data)
            print("REQ :", request.POST.get['id'])
            serializer.is_valid(raise_exception=True)
            id = serializer.validated_data['id']
            print(id)
            return Response({'message': 'No Data Get'}, status=status.HTTP_200_OK)

        data_serializer.is_valid(raise_exception=True)
        #data_serializer.save()
        print(data_serializer.save())
        data1['id'] = request.POST.get('id')
        data1['review'] = request.POST.get('review')
        data1['category'] = request.POST.get('category')
        data1['sub_category'] = request.POST.get('sub_category')
        #serializer = DataGetSerializer(data_serializer, many=True)
        #print(serializer.data)
        return Response({'message': 'No Data Get'}, status=status.HTTP_200_OK)

        if serializer.is_valid():
        datas = serializer.save()
        print(datas)
        data['id'] = datas.id
        data['review'] = datas.review
        data['category'] = datas.category
        data['sub_category'] = datas.sub_category
        return Response({'message': 'No Data Get'}, status=status.HTTP_201_CREATED)
    return Response(data, status=status.HTTP_200_OK)

    if request.method == 'GET':
        data = DataGet.objects.all()
        print(data)
        data_serialzer = DataGetSerializer(data, many=True)
        return JsonResponse(data_serialzer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        data_serialzer = DataGetSerializer(data=data)
        if data_serialzer.is_valid():
            data_serialzer.save()
            return JsonResponse(data_serialzer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(data_serialzer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No Data Get'}, status=status.HTTP_204_NO_CONTENT)
'''