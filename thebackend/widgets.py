from django import forms


class PythonEditor(forms.Textarea):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'python-editor'

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/codemirror.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/codemirror.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/xml/xml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/htmlmixed/htmlmixed.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/python/python.js',
            '/static/codemirror/init.js',
        )
