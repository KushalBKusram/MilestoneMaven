from flask import Flask, render_template

from todoist import Todoist

app = Flask(__name__, static_folder='static')

@app.route('/')
def render_index():
    todoist = Todoist()
    task_objs = todoist.get_tracked_task_objs()
    data = [task_obj.model_dump() for task_obj in task_objs]
    return render_template('index.html', task_objs=data)

if __name__ == '__main__':
    app.run(debug=True)
