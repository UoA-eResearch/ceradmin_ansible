lint:
	python3 -m venv ./venv; \
	. ./venv/bin/activate && \
	pip3 install -r requirements-dev.txt && \
	python3 -m flake8 . && \
	python3 -m yamllint -c .yamllint ./awx && \
	deactivate; \
	tflint --chdir=infrastructure/ -f compact

update_packages_dev:
	python3 -m venv ./venv; \
	. ./venv/bin/activate && \
	pip3 install -r requirements-dev.txt && \
	pur -r requirements-dev.txt && \
	deactivate;
