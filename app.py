from datetime import datetime

from flask import Flask, render_template, flash, request

import repo_students

app = Flask(__name__)
app.config["SECRET_KEY"] = "asd"

long_url = []


@app.route("/", methods={"GET", "POST"})
def items_endpoint():
    flash("Database unavailable. Try again later")
    if request.method == "POST":
        item = request.form.get("item")
        item1 = request.form.get("item1")
        if item1 is None:
            link = repo_students.Link(
                url=item, hash_id=short(item), created_at=datetime.utcnow()
            )
        else:
            link = repo_students.Link(
                url=item, hash_id=item1, created_at=datetime.utcnow()
            )
        repo_students.repository.create(link)
    return render_template("home.html")


@app.route("/items", methods={"GET"})
def items1():
    flash("Database unavailable. Try again later")
    links = repo_students.repository.get()
    return render_template("items.html", links=links)


@app.route("/<hash_id>")
def greed(hash_id):
    link1 = repo_students.repository.get(hash_id=hash_id)
    if link1 is not None:
        repo_students.repository.update(hash_id)
    else:
        flash("No such link")
    return render_template("greed.html", link1=link1)


def short(s):
    s = s.replace("/", "")
    p = 31
    m = 1e9 + 9
    hash_value = 0
    p_pow = 1
    for i in range(len(s)):
        hash_value = (hash_value + (ord(s[i]) - ord("a") + 1) * p_pow) % m
        p_pow = (p_pow * p) % m
    return hash_value


if __name__ == "__main__":
    app.run(debug=True)
