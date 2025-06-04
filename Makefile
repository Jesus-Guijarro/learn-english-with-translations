env:
	python -m venv lewtvenv

python-lib:
	python -m pip install --upgrade pip \
	&& pip install -r requirements.txt

create-db:
	cd database \
	&& python create_database.py

run:
	source lewtvenv/bin/activate && \
	python run.py & \
	sleep 3 && \
	xdg-open http://127.0.0.1:5000/


