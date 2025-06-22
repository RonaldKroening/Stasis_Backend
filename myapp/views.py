import bcrypt
import boto3
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from datetime import datetime, timedelta
import json
from .models import Stock
import numpy as np
import os
import pandas as pd
import random
import uuid
import yfinance as yf
from .YahooWrapper import YahooWrapper
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

User = get_user_model()

def validate(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    requestType = request.GET.get('status')
    
    if(requestType == "login"):
        user = User.objects.get(username=username)
        print(f" stored: {user.password} of length {len(user.password)} and entered: {password} of length {len(password)}")
        
        if(not user):
            return JsonResponse({
                "status" : False,
                "message" : "Username not found",
            })
            
        
        elif(user.check_password(password) == False):
            return JsonResponse({
                "status" : False,
                "message" : "Invalid Login Credentials",
            })
        else:
            return JsonResponse({
                "status" : True,
                "message" : "Valid Login",
                "watchList" : user.get_watchlist()
            },safe=False)
    
    elif(requestType == "signup"):
        try:
            print("check all")
            user = User.objects.get(username=username)
            print("found: ",user)
            return JsonResponse({
                "status" : False,
                "message" : "User already exists.",
            })
        except:
            user = User.objects.create(username=username)
            print("making")
            user.set_password(password)
            user.save()
            return JsonResponse({
                "status" : True,
                "message" : "Signup Successful.",
            })
            
    elif(requestType == "delete"):
        print(f"deleting user: {username}")
        user = User.objects.get(username=username)
        print("found: ",user)
        user.delete()
        return JsonResponse({
            "status" : True,
            "message" : "User deleted.",
        })
        
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

Y = YahooWrapper("")


import json
import math

def replace_nan_and_empty(data):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_nan_and_empty(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = replace_nan_and_empty(item)
    elif isinstance(data, float) and math.isnan(data):
        return -1
    elif data == "" or data is None:
        return -1
    return data

def get_file_from_s3(file_name):
    try:
        with open(f"to_s3_bucket/{file_name}", 'r', encoding='utf-8') as file:
            content = file.read()
            json_data = json.loads(content)
            
            cleaned_json_data = replace_nan_and_empty(json_data)
            
            cleaned_json_str = json.dumps(cleaned_json_data, ensure_ascii=False)
            cleaned_json_data = json.loads(cleaned_json_str)
            
            return cleaned_json_data
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


    
def usr_watch(request):
    username = request.GET.get('username')
    wl = request.GET.get('watchlist')
    watchlist = wl.split("@")
    print("here in user watchlist with name: ",username)
    
    user = User.objects.get(username=username)
    print("user for username"+username+": ",user)
    if(user):
        current_watchlist = user.get_watchlist()
        for item in watchlist:
            if(item not in current_watchlist):
                user.add_to_watchlist(item)
        for item in current_watchlist:
            if(item not in watchlist):
                user.remove_from_watchlist(item)
        return JsonResponse({'message': f'Watchlist updated successfully',"watchlist": user.get_watchlist()})
    
    else:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    


def upload_json_to_s3(file_name, json_data):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(json_data),
            ContentType='application/json'
        )

        return JsonResponse({'message': f'File {file_name} uploaded successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

def raw_number(string_input):
    if(string_input == "N/A"):
        return 0
    cleaned_number = str(string_input).replace("$", "").replace(",", "").replace("%", "")
    return float(cleaned_number)

def temp_write_to_json(data, name):
    filename = f"{name}.json"
    
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)  
        print(f"Data successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to the file named: {filename}: {e}")

def refresh(tckr):
    Y.update(tckr)
    data = Y.data(tckr)
    chart = Y.chart(tckr)
    financial_statements = Y.financial_statements(tckr)
    temp_write_to_json(chart,"to_s3_bucket/data/"+tckr+"_Chart")
    temp_write_to_json(financial_statements,"to_s3_bucket/data/"+tckr+"_FS")
    similar = find_similar(tckr,data)
    data["chart"] = chart
    data["similarassets"] = similar
    data["financial_statements"] = financial_statements
    return data


def adjust(ret, similar):
    new_ret = {
        "name":ret["name"],
        "ticker" : ret["ticker"],
        "description" : ret["description"],
        "industry" : ret["industry"],
        "sector" : ret["sector"],
    }
    
    for key,value in ret['marketItems'].items():
        new_ret[key] = raw_number(value)
        
    new_ret["similarassets"] = similar
    
    return new_ret

            
def find_all(request):
    stocks = Stock.objects.values_list('ticker', 'name')
    ret = list(stocks)
    return JsonResponse({'cache':ret},safe=False)

def find_similar(ticker, opt_data={},n=6):
    try:
        target_stock = Stock.objects.get(ticker=ticker)
        
        target_description = target_stock.description
        target_sector = target_stock.sector
        target_industry = target_stock.industry
    except:
        print(f"Stock {ticker} not found in database")
        target_description = opt_data["description"]
        target_sector = opt_data["sector"]
        target_industry = opt_data["industry"]
        
    stocks = Stock.objects.all()
    descriptions = [stock.description for stock in stocks]
    sectors = [stock.sector for stock in stocks]
    industries = [stock.industry for stock in stocks]

    vectorizer = TfidfVectorizer(stop_words='english')
    description_vectors = vectorizer.fit_transform(descriptions)
    target_description_vector = vectorizer.transform([target_description])

    description_similarities = cosine_similarity(target_description_vector, description_vectors).flatten()

    final_scores = []

    for i in range(len(stocks)):
        score = description_similarities[i]  
        score_mult = 1
        if sectors[i] == target_sector:
            score_mult += 1
        if industries[i] == target_industry:
            score_mult += 1
        score = score * score_mult
        final_scores.append(score)

    final_scores = list(set(final_scores))
    
    top_indices = sorted(range(len(final_scores)), key=lambda i: final_scores[i], reverse=True)[1:n+1]

    similar_stocks = [stocks[i].ticker for i in top_indices]

    similar_stocks.pop(0)
    if(len(similar_stocks) > n):
        similar_stocks = similar_stocks[:n]
        
    return similar_stocks

def get_stock_from_db(tckr):
    try:
        stock = Stock.objects.get(ticker=tckr)
        return stock
    except Stock.DoesNotExist:
        return None

def string_to_num(s):

    if not isinstance(s, str):
        return s
    
    
    s = s.strip()
    
    
    if not s:
        return -1
    
    
    if s == "N/A":
        return -1
    
    
    if s.endswith("%"):
        try:
            return float(s[:-1].replace(",", "")) / 100
        except ValueError:
            return -1
    
    
    s_cleaned = s.replace(",", "")
    try:
        if "." in s_cleaned:
            return float(s_cleaned)
        else:
            return int(s_cleaned)
    except ValueError:
        return -1
def update_stock(r, tckr):
    ret = r
    if("chart" in ret):
        del ret["chart"]
    if("financial_statements" in ret):
        del ret["financial_statements"]
    if("marketItems" in ret):
        r = ret["marketItems"]
        del ret["marketItems"]
        for k in r:
            ret[k] = string_to_num(r[k])
    stock, created = Stock.objects.get_or_create(ticker=tckr, defaults=ret)
    if not created:
        for key, value in ret.items():
            if(key not in ["chart","financial_statements"]):
                setattr(stock, key, value)
        stock.save()  
        print("Updated existing stock for ticker: " + tckr) 
    else:
        for key, value in ret.items():
            if(key not in ["chart","financial_statements"]):
                setattr(stock, key, value)
        stock.save()  
        print("Created stock for ticker: " + tckr) 
        return stock
        
        


def get_data(request):
    tckr = request.GET.get('ticker')
    changed = False

    stock = get_stock_from_db(tckr)
    
    if stock == None:
        ret = refresh(tckr)
        stock = update_stock(ret,tckr)
    
    print("Stock obj: ",stock)
    if stock.needsRefresh():
        ret = refresh(tckr)  
        update_stock(ret, tckr)
    
    ret = stock.data()
    ret["chart"] = get_file_from_s3("data/" + tckr + "_Chart.json")
    
    ret["financial_statements"] = {
        "statements": get_file_from_s3("data/" + tckr + "_FS.json"),
        "descriptions": get_file_from_s3("descriptions.json")
    }
    
    
    
    if(ret['similar']==""):
        ret['similar'] = find_similar(tckr)
        print("nothing similar!")
        
    print("sim: ",ret['similar'])
    

    inf = {
        
    }
    for key in ret:
        inf[key] = type(ret[key])
        
    print("Values Returning:\n",inf)
    return JsonResponse(ret)
