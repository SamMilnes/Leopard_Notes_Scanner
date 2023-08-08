<h1 align="center">Leopard Notes Scanner</h1>
![alt text](https://github.com/SamMilnes/Leopard_Notes_Scanner/blob/master/static/WIT_logo.png?raw=true)


# Instructions

Clone this repo and cd into it

```
git clone git@github.com:SamMilnes/Leopard_Notes_Scanner.git
```

### Required Downloads
- [Python3.9](https://www.python.org/downloads/release/python-390/)
- [virtualenv](https://pypi.org/project/virtualenv/)
- [PostgreSql](https://www.postgresql.org/download/)
- [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html)


Change Tesseract OCR Path
```
Go to leopardnotes/views.py and change the line:
pytesseract.pytesseract.tesseract_cmd = 'C://Program Files//Tesseract-OCR//tesseract.exe'
To wherever your path is for the downloaded tesseract.
```


Start a new **Virtualenv**, activate it, install Python module requirements on it

```
python -m venv venv
cd venv/Scripts
activate
pip install -r requirements.txt
```  
Create a **PostgreSQL** database

```
To activate postgresql in your terminal:
Type "C:\Program Files\PostgreSQL\15\bin\psql" -U postgres
It will prompt for a password, it will be the word password.
Then type:
CREATE DATABASE leopardnotesdb;
Then type exit.
-------------------------------------------------------------------------------------------------------
Then create a user with a password, for example:
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres -c "CREATE USER milness WITH PASSWORD 'password'"
-------------------------------------------------------------------------------------------------------
Then go into the database and grant all permissions to the user you created: 
"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres -d leopardnotesdb
GRANT ALL PRIVILEGES ON SCHEMA public TO milness;
```

Create a **.env** file in the root directory with enviroment variables of `APP_SECRET, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT`
APP_SECRET can be anything, for example 12345

```
APP_SECRET=12345
DB_NAME=leopardnotesdb
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
``` 

Apply migrations to the database

```
python manage.py makemigrations
python manage.py migrate 
```
Run the **Django** server 

```
python manage.py runserver
```  

# Technologies Used
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

# Resources / Links
- [Libraries](https://github.com/SamMilnes/Leopard_Notes_Scanner/blob/master/requirements.txt)
- [Testing Code](https://github.com/SamMilnes/Leopard_Notes_Scanner/tree/master/Testing)
- [OCR and Segmentation Implementation](https://github.com/SamMilnes/Leopard_Notes_Scanner/blob/master/leopardnotes/views.py)
- [Diagrams (ERD, Sequence, Navigation)](https://github.com/SamMilnes/Leopard_Notes_Scanner/tree/master/Diagrams)

