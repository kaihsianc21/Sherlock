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
        """
        :type status: int
        :rtype: Resp
        """
        self.status = status
        return self

    def set_msg(self, msg):
        """
        :type msg: msg
        :rtype: Resp
        """
        self.msg = msg
        return self

    def to_json(self):
        """
        :rtype: str
        """
        return jsonify(self.__dict__)


app = Flask(__name__)

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


@app.route('/inceptionv3/<action>', methods=['POST'])
def model_action(action):
    """
    :type action: str
    :rtype: Resp
    """

    try:
        if action not in actions:
            raise Exception('error action: {}'.format(action))

        parms = parms_filters[action](request)

        task = celery.send_task('tasks.{}'.format(action), args=[action], kwargs=parms)

        msg = {
            'model': "InceptionV3",
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
    """
    :type task_id: str
    :rtype: Resp
    """

    res = celery.AsyncResult(task_id)
    msg = {
        'status': res.state,
        'result': res.result
    }
    return Resp().set_status(200).set_msg(msg).to_json()

@app.route('/cancel/<task_id>')
def cancel_task(task_id):
    """
    :type task_id: str
    :rtype: Resp
    """

    celery.control.revoke(task_id, terminate=True)
    res = celery.AsyncResult(task_id)
    msg = {
        'status': res.state,
        'result': res.result
    }
    return Resp().set_status(200).set_msg(msg).to_json()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
