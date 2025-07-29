# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",
#     "numpy",
#     "pandas",
#     "pillow",  
#     "PIL",
#     "duckdb",
#     "urllib3",     
#     "mdformat",
# ]
# ///

import os
import requests
from datetime import datetime
from itertools import combinations
import base64
import numpy as np
import subprocess
import json 
import sqlite3
import shutil
import duckdb
from PIL import Image
import pandas as pd
import urllib.request
import threading
import re
import asyncio

api_key = os.getenv("OPENAI_API_KEY")

def formatfile(inputfilepath,outputfilepath): 
    if not os.path.exists(inputfilepath):
        return 'no_i', None

    try:
        npx_path = shutil.which("npx")
        formatted_output = subprocess.check_output(
            [npx_path, "-y", "prettier@3.4.2", inputfilepath,],text=True,encoding="utf-8" 
        )
        with open(outputfilepath, "w",encoding='utf-8') as f:
            f.write(formatted_output)
        return 'Sucess', outputfilepath

    except subprocess.CalledProcessError as e:
        return 'no_task', outputfilepath

    
def logs(inputfilepath,outputfilepath,count):
    if not os.path.exists(inputfilepath):
        return 'no_i' ,None

    folder = inputfilepath
    try:
        files = os.listdir(folder)
        fileTime = []
        for file in files:
            totalp = os.path.join(folder, file)
            time = os.path.getmtime(totalp)
            fileTime.append((file, time))
        sorted_files = sorted(fileTime, key=lambda x: x[1], reverse=True)
    except:
        return 'no_task', outputfilepath
    try:
        for i in range(0,count):
            x = inputfilepath+'/'+sorted_files[i][0]
            with open(outputfilepath, 'a') as file:
                file.write(str(x))
        return 'Success',outputfilepath
    except:
        return 'no_task', outputfilepath
    
def photo(inputfilepath,datax,outputfilepath):
    if not os.path.exists(inputfilepath):
        return 'no_i', None

    try:
        with open(inputfilepath, 'rb') as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "please find the" + datax + " present in the image and tell just that with no other text"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "detail": "high",
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }]}]}
        
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"}

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        datav=response_json["choices"][0]["message"]["content"]
        datav = datav.replace(" ", "")
        with open(outputfilepath, 'w') as file:
                file.write(datav)
        return 'Success',outputfilepath
    except:
        return 'no_task', outputfilepath
      

def similar(inputfilepath,outputfilepath):
    if not os.path.exists(inputfilepath):
        return 'no_i', None

    try:
        with open(inputfilepath, 'r',encoding='utf-8') as file:
            content = file.read()
        content = content.split("\n")
        url = "https://api.openai.com/v1/embeddings"
        response = requests.post(
            url,
            headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"},
            json={
                "input": content,
                "model": "text-embedding-3-small",
                "encoding_format": "float"
            }
        )
        data = response.json()
        embeddings = [item["embedding"] for item in data["data"]]

        def cossim(vec1, vec2):
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        pair = None
        highest = -1
        for (i, j) in combinations(range(len(content)), 2):
            sim = cossim(embeddings[i], embeddings[j])
            if sim > highest:
                highest = sim
                pair = (i, j)
        with open(outputfilepath, 'a') as file:
                file.write(content[pair[0]])
                file.write('\n')
                file.write(content[pair[1]])
        return 'Success' , outputfilepath
    except:
        return 'no_task', outputfilepath
    

def fetchapi(url,outputfilepath):
    try:
        x=requests.get(url).json()
        with open(outputfilepath, 'w') as file:
            file.write(str(x))
        return 'Success', outputfilepath
    except:
        return 'no_task', outputfilepath
    
    

def dbSqlDuck(query,inputfilepath,outputfilepath):
    if not os.path.exists(inputfilepath):
        return 'no_i' ,None
    dbpath=inputfilepath
    try:
        ext = os.path.splitext(dbpath)[1]
        if ext =='.duckdb':
            conn = duckdb.connect(dbpath)
            ans = conn.execute(query).fetchall()
            conn.close()
        else:
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            ans = result[0] 
            conn.close()
        with open(outputfilepath, 'w') as file:
            file.write(str(ans))
        return 'Success', outputfilepath
    except:
        return 'no_task', outputfilepath

def compressimage(inputfilepath,outputfilepath):
    if not os.path.exists(inputfilepath):
        return 'no_i' ,None

    try:
        fp=inputfilepath
        op=outputfilepath
        image = Image.open(fp)
        format = image.format 
        if format in ["JPEG", "JPG"] and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        if format == "WEBP":
            image.save(op, format=format, lossless=True) 
        else:
            image.save(op, format=format, optimize=True)

        return 'Success', outputfilepath
    except:
        return 'no_task', outputfilepath

def markedownHtml(inputfilepath,outputfilepath):
    if not os.path.exists(inputfilepath):
        return 'no_i', None

    try:
        with open(inputfilepath, 'r',encoding='utf-8') as file:
            content = file.read() 
        data = {
        "model": "gpt-4o-mini",  
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Convert the given markedown in the content into html and provide only the html with no extra text as response,  where the content is : " + content }
        ]}

        header = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=header, json=data)
        result = response.json()
        x= result['choices'][0]['message']['content']
        with open(outputfilepath, 'w',encoding='utf-8') as file:
                file.write(x)
        return 'Success', outputfilepath
    except:
        return 'no_task', outputfilepath

def filterCSV(filtersdict,inputfilepath,outputfilepath):
    if not os.path.exists(inputfilepath):
        return 'no_i' ,None

    try:
        df = pd.read_csv(inputfilepath)
        filters=dict(filtersdict)
        for key, value in filters.items():
            if key in df.columns:
                df = df[df[key].astype(str) == value]
        result = df.to_dict(orient="records")

        with open(outputfilepath, 'w',encoding='utf-8') as file:
            file.write(json.dumps(result))
        return 'Success', outputfilepath
    except:
        return 'no_task', outputfilepath


FUNCTIONS = [
    {
        "name": "formatfile",
        "description": "Get the file path for prettier formatting",
        "parameters": {
            "type": "object",
            "properties": {
                "inputfilepath": {"type": "string", "description": "input file path"},
                "outputfilepath": {"type": "string", "description": "output file path"}
            },
            "required": ["inputfilepath","outputfilepath"],
        },
    },
    {
        "name": "logs",
        "description": "tp find the most recent log files.",
        "parameters": {
            "type": "object",
            "properties": {
                "inputfilepath": {"type": "string", "description": "folderpath from where the log files are read"},
                "outputfilepath": {"type": "string", "description": "filepath where the output to be written"},
                "count" : {"type": "integer", "description": "number of log files"}
            },
            "required": ["fpath", "outputfilepath","count"],
        },
    },
    {
        "name": "photo",
        "description": "Extracting data from image.",
        "parameters": {
            "type": "object",
            "properties": {
                "inputfilepath": {"type": "string", "description": "Filepath from where image is read"},
                "outputfilepath": {"type": "string", "description": "filepath where result is to be stored "},
                "datax": {"type": "string", "description": "The data that needs to be extracted from the image"},
            },
            "required": ["inputfilepath", "outputfilepath", "datax"],
        },
    },
    {
        "name": "similar",
        "description": "Finding similar content from a file .",
        "parameters": {
            "type": "object",
            "properties": {
                "inputfilepath": {"type": "string", "description": "Filepath for similar content is read"},
                "outputfilepath": {"type": "string", "description": "filepath where result is to be strored "},
            },
            "required": ["inputfilepath", "outputfilepath"],
        },
    },
    {
        "name": "fetchapi",
        "description": "to fetch data from an api",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "the api url"},
                "outputfilepath": {"type": "string", "description": "the output file path where the result would be stored"},
                    
                },
            "required": ["url","outputfilepath"]
        },
    },
    {
        "name": "dbSqlDuck",
        "description": "Execute a query on a sql or duck database.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "the query to execute"},
                "inputfilepath": {"type": "string", "description": "Filepath of database file"},
                "outputfilepath": {"type": "string", "description": "filepath where result is to be strored "},
            },
            "required": ["query","inputfilepath","outputfilepath"],
        },
    },
    {
        "name": "compressimage",
        "description": "To compress an imagefile or imageurl and save as an compressed image output ",
        "parameters": {
            "type": "object",
            "properties": {
                "inputfilepath": {"type": "string", "description": "input file path for the image"},
                "outputfilepath": {"type": "string", "description": "filepath of the compressed image "},
            },
            "required": ["inputfilepath","outputfilepath"],
        },
    },
    {
        "name": "markedownHtml",
        "description": "To convert marked down to Html.",
        "parameters": {
            "type": "object",
            "properties": {
                "inputfilepath": {"type": "string", "description": "Filepath of marked down file"},
                "outputfilepath": {"type": "string", "description": "filepath where html result is to be strored "},
            },
            "required": ["inputfilepath", "outputfilepath"],
        },
    },
    {
        "name": "filterCSV",
        "description": "to filter a csv file with filter values given",
        "parameters": {
            "type": "object",
            "properties": {
                "filtersdict": {"type": "object", "description": "Filters as a dictionary of keys being filter name and values as  value pair"},
                "inputfilepath": {"type": "string", "description": "Filepath of csv file"},
                "outputfilepath": {"type": "string", "description": "filepath where result is to be strored "},
            },
            "required": [ "filtersdict","inputfilepath","outputpath"],
        },
    },
]


def run_task(task: str): 
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an assistant that can call functions.You first check if there is any input filepath or url mentioned if not you donot call any function and just say no input file given, and similarly if no output file path is mentioned then also you donot call any function and just say no output file path given. And if you find both input as well as output file paths ,You donot ask for any content nor you yourself provide any content you just call suitable functions from the functions set given.If you cannot find a matching function please say not found and call no function."},
            {"role": "user", "content": task},
        ],
        "functions": FUNCTIONS,
        "function_call": "auto",
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
    result = response.json()
    if "choices" in result and result["choices"]:
        function_call = result["choices"][0]["message"].get("function_call")
        if function_call:
            name = function_call.get("name")
            arguments = function_call.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)  
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format for arguments")
            funv= {
                "name": name,
                "arguments": arguments
            }
        else :
            return result["choices"][0]["message"]["content"] , None
    file_keys = {"inputfile", "inputfilepath", "inputpath", "dbpath", "filepath", "fpath","url"}
    result, outputpath = globals()[funv["name"]](**funv["arguments"])
    
    if result =='no_i':
        return ' the input file path is not valid one.', None
    elif result == 'no_task':
        return 'The task you said cannot be performed on the file path or url mentioned.', None
    else:
        return result,outputpath
    
print(run_task(" Please format the file C:/Users/suneh/okay.html and save it into C:/Users/suneh/okay.html"))
    