# Speer.io-Backend-Assessment

A **stock market tracking system** is created with an aim to complete the Backend assessment by Speer.

## Specifications: 

This project complies with all the requirements of the assessment.

1. Your system should have support for users to login/logout.
1. Users should be able to add balance to their wallet.
1. Users should be able to buy/sell shares (transactions need not be stored)
1. Users should be able to subscribe to an endpoint that should provide live rates.
1. Users should have the ability to see their portfolio

## Configuration and Running:

Steps to create new Django Project and new app inside it:
1. django-admin startproject PROJECT_NAME
2. cd PROJECT_NAME
3. python manage.py startapp APP_NAME
4. Add the APP_NAME in settings.py in list of INSTALLED_APPS
5. Register urls in project level urls.py (default one), as well as in app level urls.py after creating the urls.py in your app.

After cloning the project in your machine, remove db.sqlite3, pycache, and migrations folder as well from all the sub folders of django project.

NOTE: Name of our django project is StockMarket and the name of app inside it is finance.
Once removing above files, run the following commands in your terminal:
1. python manage.py makemigrations finance
2. python manage.py migrate
3. python manage.py runserver

NOTE: You can visit to "/admin" app to see the models i.e. tables in our database and modify the same from the admin panel only which is a Django default app.


## Summary: 

The backend part of the code is well formated, scalable, maintanable, extensible, and is resilient to users silly mistakes with exceptions handling mechanism. We have used Django and Python to create our backend server and business logic on the server-side. The default SQLite3 Database provided by Django is used that handles user's queries efficiently. The code is refactored in order to improve the overall design of the system while preserving its functionality.  

## Development Tools:

* Languages: Python
* Framework: Django
* Tools: Visual Studio Code, Git
