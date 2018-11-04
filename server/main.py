import base64
import io
import json
import mimetypes
import pathlib
import typing

from PIL import Image
import PyPDF2
import falcon


HOST = 'localhost'
PORT = 8080


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
        with open('../dist/index.html') as fp:
            resp.body = fp.read()
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


class StaticFiles:
    def __init__(self, base_path: pathlib.Path):
        self.path = base_path

    def on_get(self, req, resp, filename):
        try:
            with (self.path / filename).open() as fp:
                resp.body = fp.read()
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return
        resp.status = falcon.HTTP_200
        resp.content_type = mimetypes.guess_type(filename)[0]


app = falcon.API()
app.add_route('/', CatPDFAPI())
app.add_route('/{filename}', StaticFiles(pathlib.Path('../dist/')))
app.add_route('/_nuxt/{filename}', StaticFiles(pathlib.Path('../dist/_nuxt/')))


if __name__ == '__main__':
    from wsgiref import simple_server

    print('listen on {}:{}...'.format(HOST, PORT))
    simple_server.make_server(HOST, PORT, app).serve_forever()
