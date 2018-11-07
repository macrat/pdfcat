import sys

import main


if __name__ == '__main__':
	order = []
	keys = {}
	files = {}

	i = 1
	while i < len(sys.argv):
		name = sys.argv[i]
		try:
			slice_ = slice(int(sys.argv[i+1]), int(sys.argv[i+1])+1)
		except:
			slice_ = slice(*map(int, sys.argv[i+1].split(':')))

		if name in keys:
			key = keys[name]
		else:
			key = str(i//2)
			keys[name] = key

			with open(name, 'rb') as f:
				files[key] = main.load_pdf(f.read())

		for page in range(*slice_.indices(files[key].getNumPages())):
			order.append([page, key])

		i += 2


	with open('out.pdf', 'wb') as f:
		f.write(main.merge_pdf(order, files).read())
