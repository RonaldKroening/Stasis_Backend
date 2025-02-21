from .AIFunctions import find_similar
import bcrypt
import boto3
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from datetime import datetime, timedelta
import json
from .models import Stock, User
import numpy as np
import os
import pandas as pd
import random
import yfinance as yf
from .YahooWrapper import YahooWrapper


Y = YahooWrapper("")

def get_file_from_s3(file_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        response = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name
        )

        file_content = response['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        return JsonResponse(json_content, safe=False)

    except s3_client.exceptions.NoSuchKey:
        return JsonResponse({'error': 'File not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'File is not valid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
    


def refresh(tckr):
    Y.update(tckr)
    data = Y.data()
    chart = Y.chart()
    financial_statements = Y.financial_statements()
    similar = find_similar(tckr)
    return {
        "data" : data,
        "chart" : chart,
        "similar" : similar,
        "finacial_statements" : financial_statements
    }
    


def adjust(ret):
    new_ret = {
        "name":ret["NAME"],
        "ticker" : ret["TCKR"],
        "description" : ret["description"],
        "industry" : ret["industry"],
        "sector" : ret["sector"],
    }
    
    for key,value in ret.marketItems.items():
        new_ret[key] = value
        
    new_ret["similar"] = ret["similar"]
    
    return new_ret

def validate(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    requestType = request.GET.get('status')
    
    if(requestType == "login"):
        user = User.objects.get(username=username)
        if(not user):
            return JsonResponse({
                "status" : False,
                "message" : "Username not found",
            })
        elif(user.valid(username,password) == False):
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
    
    elif(requestType == "signIn"):
        user = User.objects.get(username=username)
        if(not user):
            encoded_password = password
            User.objects.create(username=username,password=encoded_password)
            return JsonResponse({
                "status" : True,
                "message" : "Signup Successful.",
            })
            
def find_all(request):
    stocks = Stock.objects.values_list('ticker', 'name')
    ret = list(stocks)
    return JsonResponse({'cache':ret},safe=False)

    
def get_data(request):
    tckr = request.GET.get('ticker')
    stock = Stock.objects.get(ticker=tckr)
    ret = {}
    changed = False
    if(stock):
        if(stock.needsRefresh()):
            ret = refresh(tckr)
            changed = True
        else:
            ret = stock.data()
            ret["similar"] = stock.get_similar(tckr)
            ret["chart"] = get_file_from_s3(tckr+"_Chart.json")
            ret["financial_statemets"] = get_file_from_s3(tckr+"_FS.json")
            
    else:
        ret = refresh(tckr)
        ret['similar'] = find_similar(tckr)
        changed = True
    
    if(changed):
        new_ret = adjust(ret)
        if(not stock):
            stock = Stock.objects.create(**new_ret)
        for key,value in new_ret.items():
            stock.updateItem(key,value)
        
        

    return JsonResponse(ret)