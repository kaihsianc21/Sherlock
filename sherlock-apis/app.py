from flask import Flask, request, url_for
from flask import jsonify

from worker import celery
import celery.states as states

from utils import FormFilter

import json
import traceback
from datetime import datetime


class Resp(object):
    def __init__(self):
        self.status = self.msg = None
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def set_status(self, status):
        self.status = status
        return self
    def set_msg(self, msg):
        self.msg = msg
        return self
    def to_json(self):
        #return json.dumps(self.__dict__) + '\n'
        return jsonify(self.__dict__)


app = Flask(__name__)


models = {
    'inceptionv3': None,
    'mnist': None
}

actions = {
    'transfer': None,
    'label': None,
    'retrain': None
}

parms_filters = {
    'label': FormFilter.label_parms_filter,
    'retrain': FormFilter.retrain_parms_filter,
    'transfer': FormFilter.transfer_parms_filter
}


@app.errorhandler(404)
def page_not_found(e):
    return Resp().set_status(404).set_msg('Page Not Found').to_json()

@app.route('/')
def main():
    return Resp().set_status(200).set_msg('Welcome Sherlock').to_json()


@app.route('/<model>/<action>', methods=['POST'])
def model_action(model, action):
    try:
        # case insensitive for the url
        model, action = model.lower(), action.lower()
        if model not in models:
            raise Exception('error model name: {}'.format(model))
        if action not in actions:
            raise Exception('error action: {}'.format(action))

        parms = parms_filters[action](request)

        print(parms)

        task = celery.send_task('tasks.{}'.format(action), args=[model, action], kwargs=parms)

        msg = {
            'model': model,
            'action': action,
            'task_id': task.id,
            'check_status': url_for('info_task', task_id=task.id)
        }
        return Resp().set_status(200).set_msg(msg).to_json()

    except Exception as e:
        err_msg = {
            'err_msg': str(e),
        }
        return Resp().set_status(400).set_msg(err_msg).to_json()


@app.route('/info/<task_id>')
def info_task(task_id):
    res = celery.AsyncResult(task_id)
    msg = {
        'status': res.state,
        'result': res.result
    }
    return Resp().set_status(200).set_msg(msg).to_json()

@app.route('/cancel/<task_id>')
def cancel_task(task_id):
    celery.control.revoke(task_id, terminate=True)
    res = celery.AsyncResult(task_id)
    msg = {
        'status': res.state,
        'result': res.result
    }
    return Resp().set_status(200).set_msg(msg).to_json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
