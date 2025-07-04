manage.py check --deploy

1. secret key
2. debug
3. database
    pip install dj-database-url
    pip install psycopg2-binary
    import dj_database_url
    dj_database_url.config(conn_max_age=500)
4. serving static files
    static root
    pip install whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',(2nd position)
5. HTTP Server
    pip install gunicorn
6. export requirements

7. For Heroku
    procfile
        web: gunicorn projectName.wsgi --log-file -
8. Create Heroku app and Add Allowed hosts

9.deployement issue installing heroku cli -

You're probably using an old version or the deprecated package 'heroku-cli'. The new one is just called 'heroku' Uninstall that by

npm uninstall -g heroku-cli

Then install the new package

npm i -g heroku

And now all your works will go perfectly.Just try heroku login and any other heroku command.

Credit: https://github.com/heroku/cli/issues/855#issuecomment-394758388