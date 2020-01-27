from django.conf import settings
from django.http.multipartparser import MultiPartParser as DjangoMultiPartParser
from rest_framework.parsers import BaseParser
from rest_framework.exceptions import ParseError


class MyMultiPartParser(BaseParser):

    media_type = 'multipart/form-data'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a multipart encoded form,
        and returns a DataAndFiles object.

        `.data` will be a `QueryDict` containing all the form parameters.
        `.files` will be a `QueryDict` containing all the form files.
        """

        try:
            parser_context = parser_context or {}
            request = parser_context['request']
            encoding = parser_context['encoding'] or settings.DEFAULT_CHARSET
            meta = request.META.copy()
            meta['CONTENT_TYPE'] = media_type
            upload_handlers = request.upload_handlers
            stream = request._request.__dict__['_stream'].__dict__['stream']
            parser = DjangoMultiPartParser(meta, stream, upload_handlers, encoding)
            data, files = parser.parse()
            if 'json' not in data:
                raise ParseError('Multipart form parse error: json missing!')
            try:
                data = json.loads(data['json'].replace('null', 'None'))
            except ValueError:
                raise ParseError('Malformed Json')
            return DataAndFiles(data, files)
        except Exception as e:
            raise ParseError(f'Multipart form parse error: {str(e)}')

