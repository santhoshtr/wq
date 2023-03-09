import multiprocessing

bind = "0.0.0.0:9898"
workers = multiprocessing.cpu_count()
accesslog = "/tmp/translate.access.log"
wsgi_app  = "app:app"
