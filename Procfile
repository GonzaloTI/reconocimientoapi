release: apt-get update && apt-get install -y libgl1 libglib2.0-0
web: gunicorn proydjango.wsgi:application --bind 0.0.0.0:$PORT
