# 🥾 Take a hike 🥾

### Setting up for local development 🧑‍💻

#### Start virtual environment 🐚
* Use `pipenv shell`

#### Install dependencies and initialize sql database 📋
* Use `pipenv install`
* Use `pipenv run init_sql`
---- This will initialize sql database and create table schema.

#### Run Flask development server 🏃‍➡️
* Use `pipenv run start` 
---- Or run `export FLASK_DEBUG=1 && flask run -h localhost -p 5001` for live reloading
* Find app running at `http://localhost:5001/`

#### If you need to access the sqlite3 database 📊
* Use `pipenv run db` or `sqlite3 hikes.db`
* Verify schema with `.schema`
* `.quit` to exit sqlite3 prompt