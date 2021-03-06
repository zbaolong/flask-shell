# encoding: utf-8
import os
import sys

from flask import Response
from flask import jsonify
from flask import Flask, render_template
from flask_socketio import SocketIO

# 设置默认编码
default_encoding = "utf-8"
if (default_encoding != sys.getdefaultencoding()):
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class MyResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (list, dict)):
            try:
                response = jsonify(response)
            except RuntimeError:
                print('返回的字符串不是有效json')

        return super(Response, cls).force_type(response, environ)


# 设置static_url_path=""则静态资源默认目录为/static/目录
app = Flask(__name__, static_url_path="")
app.response_class = MyResponse

basePath = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.abspath(os.path.dirname(__file__))

socketio = SocketIO(app)


# app.config['SECRET_KEY'] = 'secret!'


def execShell(file):
    result_lines = os.popen('sh ' + file).readlines()
    return result_lines


@app.route('/', methods=['GET'])
def hello_html():
    return app.send_static_file("html/hello.html")


@socketio.on('connect', namespace='shell')
def wsConnect():
    print('>>> websocket connected')


def resultResponse(result_lines):
    decodeList = []
    for line in result_lines:
        row = line.replace("\n", "")
        decodeList.append(row)
        socketio.emit('message', {'data': row})
    return decodeList


@app.route('/<name>', methods=['GET'])
def hello_world(name):
    result_lines = "nothing to"
    file = "/shell/hello.sh"
    if name == "app":
        file = "/root/bin/start-app"
    elif name == "vue":
        file = "/root/bin/start-vue"
    elif name == "oa":
        file = "/root/bin/start-oa"
    elif name == "nginx":
        file = "/root/bin/start-nginx"
    else:
        file = '/shell/hello.sh'
        file = basePath + file
    result_lines = execShell(file)
    return resultResponse(result_lines)


if __name__ == '__main__':
    # app.run('0.0.0.0', 8088)
    socketio.run(app, '0.0.0.0', 8088, debug='true')
    # socketio.run(app)
