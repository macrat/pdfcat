import os
import io
import json
import typing
import base64

from PIL import Image
import PyPDF2
import falcon



def image_to_pdf(image: typing.BinaryIO) -> typing.BinaryIO:
	f = io.BytesIO()
	Image.open(image).save(f, 'PDF')
	f.seek(0)
	return f


def merge_pdf(pages: typing.List[typing.Tuple[int, str]], files: typing.Mapping[str, PyPDF2.PdfFileReader]) -> typing.BinaryIO:
	pdf = PyPDF2.PdfFileWriter()

	for page, key in pages:
		pdf.addPage(files[key].getPage(page))

	result = io.BytesIO()
	pdf.write(result)
	result.seek(0)
	return result


def load_pdf(data: bytes) -> PyPDF2.PdfFileReader:
	return PyPDF2.PdfFileReader(io.BytesIO(data))


class CatPDFAPI:
	def on_get(self, req, resp):
		resp.body = 'index'
		resp.status_code = falcon.HTTP_200
		resp.content_type = 'text/html'

	def on_post(self, req, resp):
		data = json.loads(req.bounded_stream.read().decode('utf-8'))
		resp.stream = merge_pdf(
			[(x['page'], x['key']) for x in data['pages']],
			{k: load_pdf(base64.b64decode(v)) for k, v in data['files'].items()},
		)
		resp.status_code = falcon.HTTP_200
		resp.content_type = 'application/pdf'


app = falcon.API()
app.add_route('/', CatPDFAPI())


if __name__ == '__main__':
	from wsgiref import simple_server

	simple_server.make_server('localhost', 8080, app).serve_forever()
