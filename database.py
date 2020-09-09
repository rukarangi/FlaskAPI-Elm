from peewee import *
import datetime as dt

#Database
db = SqliteDatabase("tasks.db")


#Models
class Task(Model):
	i = IntegerField()
	title = TextField()
	createdAt = DateTimeField(default=dt.datetime.now)
	done = BooleanField(default=False)

	class Meta:
		database = db


#Methods
def add_task(i, title):
	task = Task.create(i=i, title=title)
	task.save()
	return 1

def get_task(i):
	taskM = Task.get(Task.i == i)
	return task_to_json(taskM)

def task_to_json(taskM):
	task = {
		"i": taskM.i,
		"title": taskM.title,
		"createdAt": taskM.createdAt,
		"done": taskM.done
	}
	return task

def update_task(task, i):
	taskM = Task.get(Task.i == i)
	taskM.i = task["i"]
	taskM.done = task["done"]
	taskM.save()
	return taskM

def delete_task(taskM):
	i = taskM.i
	taskM.delete_instance()

	need_updating = Task.select().where(Task.i >= i)
	for task in need_updating:
		task.i -= 1
		task.save()

	return 1


#Initialise
def initialise():
	db.connect()
	db.create_tables([Task], safe=True)
	db.close()