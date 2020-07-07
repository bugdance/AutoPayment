# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""The receiver is use for receive the data."""
# # # Import current path.
import sys

sys.path.append('..')
# # # 基础包。
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from datetime import datetime
import time
import logging
# # # 程序包。
from booster.basic_parser import BasicParser
from booster.date_formatter import DateFormatter
# # # app实例。
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# # # 数据库。
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1:3306/produce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# # # 日志格式化。
app.logger = logging.getLogger("flask")
app.logger.setLevel(level=logging.INFO)
app.formatter = logging.Formatter('[%(asctime)s]%(message)s')
app.handler = logging.FileHandler("flask.log")
# app.handler = logging.StreamHandler()
app.handler.setFormatter(app.formatter)
app.logger.addHandler(app.handler)
# # # 声明赋值。
BP = BasicParser()
DF = DateFormatter()
BP.logger = app.logger
DF.logger = app.logger


class ProduceMM(db.Model):
    """MM造值表,abck
    """
    __tablename__ = "produce_mm"
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)
    produce_value = db.Column(db.Text)
    
    def __init__(self, create_time, update_time, produce_value):
        self.create_time = create_time
        self.update_time = update_time
        self.produce_value = produce_value


class ProduceVY(db.Model):
    """VY造值表,abck
    """
    __tablename__ = "produce_vy"
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)
    produce_value = db.Column(db.Text)
    
    def __init__(self, create_time, update_time, produce_value):
        self.create_time = create_time
        self.update_time = update_time
        self.produce_value = produce_value


class ProduceWN(db.Model):
    """WN造值表,header
    """
    __tablename__ = "produce_wn"
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer)
    produce_value = db.Column(db.Text)
    
    def __init__(self, create_time, produce_value):
        self.create_time = create_time
        self.produce_value = produce_value


def delete_mm():
    """mm删除abck
    :return: None
    """
    try:
        now = int(time.time())
        ProduceMM.query.filter(ProduceMM.create_time < now - 3600*24*7).delete()
        db.session.commit()
    except Exception as ex:
        app.logger.info(f"mm删除数据库错误{ex}")
    else:
        pass
    db.session.close()


def delete_wn():
    """wn删除header
    :return: None
    """
    try:
        now = int(time.time())
        ProduceWN.query.filter(ProduceWN.create_time < now - 3600*24*2).delete()
        db.session.commit()
    except Exception as ex:
        app.logger.info(f"wn删除数据库错误{ex}")
    else:
        pass
    db.session.close()
    

def delete_vy():
    """vy删除abck
    :return: None
    """
    try:
        now = int(time.time())
        ProduceVY.query.filter(ProduceVY.create_time < now - 3600*24*7).delete()
        db.session.commit()
    except Exception as ex:
        app.logger.info(f"vy删除数据库错误{ex}")
    else:
        pass
    db.session.close()


scheduler = APScheduler()
scheduler.init_app(app=app)
scheduler.add_job(func=delete_mm, id='delete_mm', trigger='cron', hour=0, minute=0, next_run_time=datetime.now())
scheduler.add_job(func=delete_wn, id='delete_wn', trigger='interval', hours=20, next_run_time=datetime.now())
# scheduler.add_job(func=delete_vy, id='delete_vy', trigger='cron', hour=0, minute=0, next_run_time=datetime.now())
scheduler.start()



# # # 链接地址,例http://x.x.x.x:33334/produce/mm/
@app.route('/produce/mm/', methods=['POST'])
def server_mm():
    """
    Returns:

    """
    get_dict = BP.parse_to_eval(request.get_data())
    if not get_dict:
        return jsonify({"value": ""})
    
    try:
        status = get_dict.get("mm")
        if status != "abck":
            return jsonify({"value": ""})
        
        now = int(time.time())
        sql = f"select id, produce_value from produce_mm where update_time < {now - 60*10} order by rand() limit 1;"
        result = db.session.execute(sql)
        result = list(result)
        if result:
            number = result[0][0]
            value = result[0][1]
            ProduceMM.query.filter(ProduceMM.id == number).update({'update_time': now + 60*3})
            db.session.commit()
            db.session.close()
            return jsonify({"value": value})
        else:
            db.session.close()
            return jsonify({"value": ""})
    except Exception as ex:
        app.logger.info(f"从数据库取mm刷值失败{ex}")
        return jsonify({"value": ""})


# # # 链接地址,例http://x.x.x.x:33334/produce/wn/
@app.route('/produce/wn/', methods=['POST'])
def server_wn():
    """
    Returns:

    """
    get_dict = BP.parse_to_eval(request.get_data())
    if not get_dict:
        return jsonify({"value": ""})
    
    try:
        status = get_dict.get("wn")
        if status != "header":
            return jsonify({"value": ""})
        
        now = int(time.time())
        sql = f"select produce_value from produce_wn where {now - 3600*24*2} < create_time < {now} " \
              f"order by rand() limit 1;"
        result = db.session.execute(sql)
        result = list(result)
        if result:
            value = result[0][0]
            db.session.close()
            return jsonify({"value": value})
        else:
            db.session.close()
            return jsonify({"value": ""})
    except Exception as ex:
        app.logger.info(f"从数据库取wn刷值失败{ex}")
        return jsonify({"value": ""})


# # # 链接地址,例http://x.x.x.x:33334/produce/vy/
@app.route('/produce/vy/', methods=['POST'])
def server_vy() -> dict:
    """

    Returns:
        dict
    """
    get_dict = BP.parse_to_eval(request.get_data())
    if not get_dict:
        return jsonify({"value": ""})

    try:
        status = get_dict.get("vy")
        if status != "abck":
            return jsonify({"value": ""})

        now = int(time.time())
        sql = f"select id, produce_value from produce_vy where update_time < {now - 60*10} order by rand() limit 1;"
        result = db.session.execute(sql)
        result = list(result)
        if result:
            number = result[0][0]
            value = result[0][1]
            ProduceVY.query.filter(ProduceVY.id == number).update({'update_time': now + 60*3})
            db.session.commit()
            db.session.close()
            return jsonify({"value": value})
        else:
            db.session.close()
            return jsonify({"value": ""})
    except Exception as ex:
        app.logger.info(f"从数据库取vy刷值失败{ex}")
        return jsonify({"value": ""})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=33334, threaded=True)
