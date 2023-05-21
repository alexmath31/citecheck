from datetime import datetime

from flask import Flask, render_template, flash, request, redirect

import repo_students

app = Flask(__name__)
app.config["SECRET_KEY"] = "asd"

long_url = []


@app.route("/", methods={"GET", "POST"})
def items_endpoint():
    flash("Database unavailable. Try again later")
    if request.method == "POST":
        i = request.form.get("item")
        i1 = request.form.get("item1")
        link = repo_students.Link(url=i, hash_id=i1, created_at=datetime.utcnow())
        if len(i1) < 1:
            link = repo_students.Link(
                url=i, hash_id=short(i), created_at=datetime.utcnow()
            )
        repo_students.repository.create(link)
    return render_template("home.html")


@app.route("/items", methods={"GET"})
def items():
    flash("Database unavailable. Try again later")
    links = repo_students.repository.get()
    return render_template("items.html", links=links)


@app.route("/delete/<hash_id>")
def delete(hash_id):
    link1 = repo_students.repository.get(hash_id=hash_id)
    repo_students.repository.delete(link1.hash_id)
    links = repo_students.repository.get()
    return render_template("items.html", links=links)


@app.route("/<hash_id>")
def greed(hash_id):
    link1 = repo_students.repository.get(hash_id=hash_id)
    if link1 is not None:
        repo_students.repository.update(link1)
    else:
        flash("No such link")
    return redirect(link1.url)


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
