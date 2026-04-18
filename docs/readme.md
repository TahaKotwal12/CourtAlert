Terminal 1 — Worker:


cd backend
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
Terminal 2 — Beat (scheduler):


cd backend
celery -A app.workers.celery_app beat --loglevel=info
--pool=solo is also needed on Windows because the default prefork pool uses fork() which doesn't exist on Windows.