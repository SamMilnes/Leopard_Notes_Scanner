<h1 align="center">Leopard Notes Scanner</h1>

## Features

- Convert Images To Text
- User Accounts
- Segmentation
- Snipping Tool
- Public Feed
- Messaging
- Note Saving
- Friends / Followers

## Instructions

Clone this repository, cd into it

```
git clone
cd Social-Network
```    


Download PostgreSql
```
https://www.postgresql.org/download/
```

Download Tesseract OCR
```
https://tesseract-ocr.github.io/tessdoc/Installation.html

Go to leopardnotes/views.py and change the line:
pytesseract.pytesseract.tesseract_cmd = 'C://Program Files//Tesseract-OCR//tesseract.exe'
To wherever your path is for the downloaded tesseract.
```


Start a new **Virtualenv**, activate it, install Python module requirements on it

```
python -m venv venv
cd venv/Scripts
activate
pip install -r requirements/base.txt
```  
Create a **PostgreSQL** database

```
To activate postgresql in your terminal:
Type "C:\Program Files\PostgreSQL\15\bin\psql" -U postgres -d
Then type:
CREATE DATABASE leopardnotesdb;
Then create a user with a password, for example:
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres -c "CREATE USER milness WITH PASSWORD 'password'"
Then go into the database and grant all permissions to the user you created: 
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres -d leopardnotesdb
GRANT ALL PRIVILEGES ON SCHEMA public TO milness;
```

Create a **.env** file in the root directory with enviroment variables of `APP_SECRET, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT`

```
APP_SECRET=your_very_very_secure_secret_key
DB_NAME=leopardnotesdb
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
``` 

Apply migrations to the database and run the **Django** server 

```
python manage.py makemigrations
python manage.py migrate 
python manage.py runserver
```  

## Technologies
- Python
- CSS
- HTML
- JavaScript
- Django
- OpenCV
- PostgreSQL
- Tesseract OCR
- Pix2Tex
- Git/Github



