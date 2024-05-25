from flask import Flask, render_template, request
 
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/image_search", methods=["GET", "POST"])
def image_search():
    if request.method == "GET":
        return render_template("image_search.html")

@app.route("/advanced_search", methods=["GET", "POST"])
def advanced_search():
    if request.method == "GET":
        return render_template("advanced_search.html")

if __name__ == '__main__':
    app.run(debug=True)
