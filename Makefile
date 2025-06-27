.PHONY: clean build

# Очистка старых артефактов сборки
clean:
	rm -rf build dist *.egg-info src/*.egg-info

# Сборка wheel и source distribution
build: clean
	python setup.py sdist bdist_wheel
