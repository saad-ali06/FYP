from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone, timedelta
from model_utilies import model, tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
# from bson import ObjectId

bcrypt = Bcrypt()
port = 85
client = MongoClient("mongodb+srv://saad:709bCCR8JCblXyk4@cluster0.kvghemk.mongodb.net/")
db = client.Flask_DataBase
user_table = db.user_table

def pre_process(ds):
    corpus = []
    for i in range(len(ds)):
        if isinstance(ds[i], str):
            review = re.sub('[^a-zA-Z]', ' ', ds[i])
            review = review.split(' ')
            review = [word for word in review if word != '']
            corpus.append(review)
    return corpus


def sentiment_predict(sentence):
    sentence = [sentence]
    max_len = 279
    sentence=pre_process(sentence)
    sentence = tokenizer.texts_to_sequences(sentence)
    sentence=pad_sequences(sentence, maxlen=max_len, padding='post', truncating='post')
    output=model.predict(sentence)
    threshold = 0.5
    prediction = 'Negative' if output > threshold else 'Positive'
    return prediction, output[0,0]
# prediction, output = sentiment_predict(sentence)
# print("Sentiment for this tweet is:",prediction,'with score:',output)

# Checks if user_name exists in db and return True/False
def check_user(user_name):
    user_name = user_name.lower()
    result = user_table.find_one({"user_name":user_name})
    return bool(result)

# Checks if email exists in db and return True/False   
def check_email(email):
    result = user_table.find_one({"email":email})
    return bool(result)

# This function uses Above two functions for validation and 
# returns user_data(dict: containing user info ) else False
def registration_checker(user_name,email,password):
    if check_user(user_name) or check_email(email):
        return None
    
    user_data = {
                'user_name': user_name,
                'email': email,
                'password': bcrypt.generate_password_hash(password).decode('utf-8'),
                'c_time': datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                'posts': []
            }
    db.user_table.insert_one(user_data)
    return user_data
       
# Checks if password match in db and return True/False       
def check_password_email(email,password):
    result = user_table.find_one({"email":email})
    if result :
        if bcrypt.check_password_hash(result['password'],password): 
            user_data = {
                'user_name': result['user_name'],
                'email': result['email'],
                'password': result['password'],
                'c_time': result['c_time'],
                }
            return user_data
        else:
            return None
                
def add_post_to_db(title,content,email,user_name):
    prediction, score = sentiment_predict(content)
    new_post = {'title':title,
                'content':content,
                'prediction':prediction,
                'prediction_score':f'{score*100:.2f}',
                'user_email': email,
                'author':user_name,
                'date':datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                }
    collection = db[email]
    return bool(collection.insert_one(new_post))
        
def get_post_db(email):
    collection = db[email]
    posts = collection.find({})
    return posts
           
def delete_post_from_db(index, email):
    collection = db[email]
    posts = collection.find({}).limit(1).skip(index)
    for i,post in enumerate(posts, start=0):
        global p 
        p = post
        if i == index:
            break
    post = p  
    collection.delete_one({'_id':post['_id']})
    
def edit_post_form_db(index, new_title, new_content, email):
    print('--------------------------------------------------------')
    print(index,type(index))
    collection = db[email]
    posts = collection.find({}).limit(1).skip(index)
    def new_post(prediction, score):
        
            # new values for post
            new_value = {
                "$set": {"title": new_title if new_title else post['title'],
                        "content":new_content if new_content else post['content'],
                        'prediction':prediction,
                        'prediction_score':f'{score*100:.2f}',
                        "date":datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") },
                "$currentDate": {"lastModified": True}
            }
            return new_value
    for post in posts:
        if new_content:
            prediction, score = sentiment_predict(new_content)
            new_value = new_post(prediction, score)
            
        else:
            new_value = new_post(post['prediction'], post['prediction_score'])
    collection.update_one({'_id':post['_id']},new_value)
    



        
    
    
    
            


# user_name = "Saad"        
# result = check_user(user_name)  
# # result = user_table.find_one({"_id":result[1]})  
# print (result)