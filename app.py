from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200), nullable=False)
    Name_Neighbor = db.Column(db.String, nullable=False)
    Side_Neighbor = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return('Hexagon %r') % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['Name']
        Neighbor_content = request.form['Name_Neighbor']
        Side_content = request.form['Side_Neighbor']
        side_content = int(Side_content)
        new_hexagon = Todo(
            Name=task_content, Name_Neighbor=Neighbor_content, Side_Neighbor=Side_content)
        if side_content < 4:
            new_hexagon_neighbor = Todo(
                Name=Neighbor_content, Name_Neighbor=task_content, Side_Neighbor=side_content+3)
        if side_content > 3:
            new_hexagon_neighbor = Todo(
                Name=Neighbor_content, Name_Neighbor=task_content, Side_Neighbor=side_content-3)

        try:
            db.session.add(new_hexagon)
            db.session.commit()
            db.session.add(new_hexagon_neighbor)
            db.session.commit()
            return redirect('/')
        except:
            return "there was an error"
    else:
        tasks = Todo.query.order_by(Todo.date_created)
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):

    task_to_delete = Todo.query.get_or_404(id)
    hexagon_to_delete = task_to_delete.Name
    # Checking if Hexagon isn't the only link
    check_hexagon_list = Todo.query.filter_by(Name=hexagon_to_delete).all()
    number_of_neighbors = len(check_hexagon_list)
    # Removing hexagon from Neighbors
    delete_hexagon_neighbor_list = Todo.query.filter_by(
        Name_Neighbor=hexagon_to_delete).all()

    # List to check all neighbors are securely connected
    l = []
    flag = 0
    for i in range(number_of_neighbors):
        l.append(check_hexagon_list[i].Side_Neighbor)
    l.sort()
    if len(l) > 1:
        for i in range(len(l)-1):
            if l[i+1]-l[i] == 1:
                pass
            else:
                flag = 1
                break
    if flag == 0:
        try:
            # deleting neighbors
            for i in range(len(delete_hexagon_neighbor_list)):
                db.session.delete(Todo.query.get(
                    delete_hexagon_neighbor_list[i].id))
                db.session.commit()
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem deleting that task'
    else:
        return 'That hexagon is the only link between two hexagons'


@app.route('/results', methods=['POST', 'GET'])
def results():
    if request.method == "POST":
        name = request.form['Search']
        name_of_hexagon = Todo.query.filter_by(Name=name).all()
        total_neighbors = len(name_of_hexagon)
        name_of_neighbor = []
        side_neighbor_isAttached = []
        for i in range(total_neighbors):
            name_of_neighbor.append(name_of_hexagon[i].Name_Neighbor)
            side_neighbor_isAttached.append(name_of_hexagon[i].Side_Neighbor)
    return render_template("results.html", len=total_neighbors, name_of_neighbor=name_of_neighbor,
                           side_neighbor_isAttached=side_neighbor_isAttached)


if __name__ == "__main__":
    app.run(debug=True)
