from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///subtrackr.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(10), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    subs = Subscription.query.all()
    total_monthly = sum(s.cost if s.frequency == "monthly" else s.cost / 12 for s in subs)
    total_yearly = total_monthly * 12
    return render_template("index.html", subs=subs, total_monthly=total_monthly, total_yearly=total_yearly)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        cost = float(request.form["cost"])
        frequency = request.form["frequency"]
        new_sub = Subscription(name=name, cost=cost, frequency=frequency)
        db.session.add(new_sub)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    sub = Subscription.query.get_or_404(id)
    if request.method == "POST":
        sub.name = request.form["name"]
        sub.cost = float(request.form["cost"])
        sub.frequency = request.form["frequency"]
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", sub=sub)

@app.route("/delete/<int:id>")
def delete(id):
    sub = Subscription.query.get(id)
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/export")
def export():
    subs = Subscription.query.all()
    output = []
    for s in subs:
        output.append([s.name, s.cost, s.frequency])
    csv_data = "Name,Cost,Frequency\n" + "\n".join([",".join(map(str, row)) for row in output])
    return Response(csv_data, mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=subscriptions.csv"})

if __name__ == "__main__":
    app.run(debug=True)
