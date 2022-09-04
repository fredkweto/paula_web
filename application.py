from paula import app
from waitress import serve

app_test = True
application = app

if app_test:
    if __name__== '__main__':
        application.run(debug=False)
else:
    if __name__== '__main__':
        serve(application, host="0.0.0.0", port=8080)

