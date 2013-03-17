import os

for current, directories, files in os.walk(os.getcwd()):
	for file in files:
		path = os.path.join(current, file)

		if os.path.splitext(path)[1] == '.pyc':
			os.remove(path)

