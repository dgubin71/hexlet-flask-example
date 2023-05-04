start:
	poetry run flask --app example --debug run

start-gunicorn:
	poetry run gunicorn --workers=4 --bind=127.0.0.1:5000 example:app

