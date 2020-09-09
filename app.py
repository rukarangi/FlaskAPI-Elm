from flask import Flask, jsonify, make_response, abort, request, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import *

#from testJson import tasks
import database as db

#App setup
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

app = Flask(__name__)


#Auth setup
users = {
	"luke": generate_password_hash("stephen")
}

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
	if username in users and check_password_hash(users.get(username), password):
		return username

@auth.error_handler
def unauthorized():
	return make_response(jsonify({"error": "Unauthorized Access"}), 403)


#Routes
@app.route("/")
def hello_world():
	return "Hello World!"

#GET responses
@app.route("/todo/api/v1/tasks", methods=["GET"])
@auth.login_required
def get_tasks():
	db.db.connect()
	tasks = [make_public(task) for task in db.Task.select()]
	db.db.close()

	return jsonify({"tasks": tasks})

@app.route("/todo/api/v1/tasks/<int:task_id>", methods=["GET"])
@auth.login_required
def get_task(task_id):
	#task = [task for task in tasks if task["id"] == task_id]
	
	db.db.connect()
	try:
		task = db.get_task(task_id)
	except:
		abort(404)
	db.db.close()

	return jsonify({"task": make_public(task)})

#POST responses
@app.route("/todo/api/v1/tasks", methods=["POST"])
@auth.login_required
def create_task():
	if not request.json or not "title" in request.json:
		abort(400)

	db.db.connect()
	taskIds = [task.i for task in db.Task.select()]
	newId = (taskIds[-1] + 1) if len(taskIds) > 0 else 1

	task = {
		"i": newId,
		"title": request.json["title"]
	}
	
	db.add_task(task["i"], task["title"])
	db.db.close()

	return jsonify({"task": make_public(task)}), 201

#PUT responses
@app.route("/todo/api/v1/tasks/<int:task_id>", methods=["PUT"])
@auth.login_required
def update_task(task_id):
	if not request.json:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)

	task = {
		"i": str(task_id),
		"done": request.json["done"]
	}
	try:
		response = db.update_task(task, task_id)
	except:
		abort(404)

	return jsonify(make_public(response))

#DELETE responses
@app.route("/todo/api/v1/tasks/<int:task_id>", methods=["DELETE"])
@auth.login_required
def delete_task(task_id):
	db.db.connect()
	#print(task_id)
	try:
		task = db.Task.get(db.Task.i == task_id)
	except:
		abort(404)

	db.delete_task(task)

	db.db.close()
	return jsonify({"result": True})

#Error handling
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({"error": "Not Found"}), 404)

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({"error": "Bad Request"}), 400)

@app.errorhandler(503)
def server_error(error):
	return make_response(jsonify({"error": "Server Error"}), 503)

#Create URIs
def make_public(taskM, task=None):
	if not task:
		response = db.task_to_json(taskM)
	else:
		response = task

	response["i"] = url_for("get_task", task_id=response["i"], _external=True)
	return response


#App called
if __name__ == "__main__":
	db.initialise()
	app.run(debug=DEBUG, host=HOST, port=PORT)