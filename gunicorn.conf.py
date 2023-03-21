import multiprocessing

bind = "0.0.0.0:9898"
workers = 1
accesslog = "/tmp/translate.access.log"
wsgi_app  = "app:app"
timeout = 600
