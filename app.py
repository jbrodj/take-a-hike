from flask import Flask, redirect, render_template, request
from content import formContent

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
  # Source: CS50
  """Ensure responses aren't cached"""
  response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
  response.headers["Expires"] = 0
  response.headers["Pragma"] = "no-cache"
  return response

@app.route('/')
def hello():
  print(formContent.keys())
  for field in formContent:
    print(formContent[field]["name"])
  return render_template("index.html")

@app.route('/new-hike')
def newHike():
  if request.method == "POST":
    print('post')
    return redirect('/')
  else:
    return render_template("new-hike.html", formContent=formContent)