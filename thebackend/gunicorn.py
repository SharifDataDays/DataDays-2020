bind = 'unix:/www/datadays/datadays2021/DataDays-2020/gunicorn.sock'
workers = 3
proc_name = 'datadays2021 gunicorn'

preload=True
timeout = 600
keep_alive = 10

user = 'root'
group = 'root'
loglevel = 'debug'

errorlog = '/log/datadays/gunicorn_error.log'

raw_env = [
        'DJANGO_SETTINGS_MODULE=thebackend.settings.production',

        'DB_NAME=dd2021db',
        'DB_USER=dd2021user',
        'DB_PASSWORD=13781378Kh@',
        'DB_HOST=localhost',
        'DB_PORT=5432',

        'EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_USE_TLS=True',
        'EMAIL_USE_SSL=False',
        'EMAIL_HOST=smtp.gmail.com',
        'EMAIL_HOST_USER=sharif.datadays.3@gmail.com',
        'EMAIL_HOST_PASSWORD=datadays_branding',
        'EMAIL_PORT=587',

        'LOG_ROOT=/log/datadays/',
]

