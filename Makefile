all: native

urxvt:
	urxvt -e bash -c "python main.py"

native:
	python main.py
