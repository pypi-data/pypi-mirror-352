
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import requests
import json
import math


# business logic part

def f_sales(content):
    t0 = content.replace(',', '')
    if float(t0) == 0:
        sales = 0
    else:
        t1 = math.log10(float(t0))
        t2 = 0.0006306609893727 * t1 * t1 * t1 * t1 - 0.0165317434787462 * t1 * t1 * t1 + 0.17887299931035 * t1 * t1 + 0.912385809982912 * t1 - 1.76367539420814
        sales = round(math.pow(10, t2), 2)
    return str(sales)


def f_uv(content):
    t0 = content.replace(',', '')
    if float(t0) == 0:
        uvs = 0
    else:
        t1 = math.log10(float(t0))
        t2 = 0.0006306609893727 * t1 * t1 * t1 * t1 - 0.0165317434787462 * t1 * t1 * t1 + 0.17887299931035 * t1 * t1 + 0.912385809982912 * t1 - 1.76367539420814
        uvs = int(round(math.pow(10, t2)))
    return str(uvs)


def f_addcart(content):
    t0 = content.replace(',', '')
    if float(t0) == 0:
        uvs = 0
    else:
        t1 = math.log10(float(t0))
        t2 = 0.0006306609893727 * t1 * t1 * t1 * t1 - 0.0165317434787462 * t1 * t1 * t1 + 0.17887299931035 * t1 * t1 + 0.912385809982912 * t1 - 1.76367539420814
        addcart_num = int(round(math.pow(10, t2)))
    return str(addcart_num)


def f_collect(content):
    t0 = content.replace(',', '')
    if float(t0) == 0:
        uvs = 0
    else:
        t1 = math.log10(float(t0))
        t2 = 0.0006306609893727 * t1 * t1 * t1 * t1 - 0.0165317434787462 * t1 * t1 * t1 + 0.17887299931035 * t1 * t1 + 0.912385809982912 * t1 - 1.76367539420814
        collect_num = int(round(math.pow(10, t2)))
    return str(collect_num)


def f_payusers(content):
    t0 = content.replace(',', '')
    print("这里", t0)
    if float(t0) == 0:
        uvs = 0
    else:
        t1 = math.log10(float(t0))
        t2 = 0.0006306609893727 * t1 * t1 * t1 * t1 - 0.0165317434787462 * t1 * t1 * t1 + 0.17887299931035 * t1 * t1 + 0.912385809982912 * t1 - 1.76367539420814
        payusers = int(round(math.pow(10, t2)))
    return str(payusers)


def f_payrate(content):
    t0 = content.replace(',', '')
    if float(t0) == 0:
        payrate = 0
    else:
        t1 = math.log10(float(t0))
        t2 = -0.03915332961878450000 * t1 * t1 * t1 * t1 + 0.33116922702621600000 * t1 * t1 * t1 - 1.05080245375226000000 * t1 * t1 + 3.47844680691085000000 * t1 - 2.73100485725722000000
        t3 = math.pow(10, t2) / 100000
        payrate = t3
    return str(payrate)


# flask part

app = Flask(__name__)  # create a Flask instance


@app.route("/")
def index():
    return "Hello,BI!"


# <string:content>定义输入的内容的类型及变量名，注意":"左右不能有空格，
@app.route("/tradeindex/<string:content>")
def tradeindex(content):
    try:
        sales = f_sales(content)

        dict_data = {"code": 200, "data_result": {"input": content, "result_data": sales}}
    except:
        dict_data = {"code": 500}

    return dict_data


@app.route("/uvindex/<string:content>")
def uvindex(content):
    try:
        uv = f_uv(content)
        dict_data = {"code": 200, "data_result": {"input": content, "result_data": uv}}
    except:
        dict_data = {"code": 500}

    return dict_data


@app.route("/addcart/<string:content>")
def addcart(content):
    try:
        addcart_num = f_addcart(content)
        dict_data = {"code": 200, "data_result": {"input": content, "result_data": addcart_num}}
    except:
        dict_data = {"code": 500}

    return dict_data


@app.route("/collectindex/<string:content>")
def collect(content):
    try:
        collect_number = f_collect(content)
        dict_data = {"code": 200, "data_result": {"input": content, "result_data": collect_number}}
    except:
        dict_data = {"code": 500}

    return dict_data


@app.route("/payrate/<string:content>")
def payrate(content):
    try:
        payrate = f_payrate(content)
        dict_data = {"code": 200, "data_result": {"input": content, "result_data": payrate}}
    except:
        dict_data = {"code": 500}
    return dict_data


@app.route("/payusers/<string:content>")
def payusers(content):
    content = content.replace(',', '')
    float_content = float(content)

    if float_content == 0:
        dict_data = {"code": 200, 'data_result': {"input": float_content, "result_data": '0'}}
    else:
        try:
            payusers = f_payusers(content)
            dict_data = {"code": 200, "data_result": {"input": content, "result_data": payusers}}
        except:

            dict_data = {"code": 500}

    return dict_data


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, threaded=True)
