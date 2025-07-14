# Repository for the frontend development

# Install

to compile scss to css please do the following:

        npm install -g sass

to automatically compile your scss files run the following in your static
folder:

        sass --watch scss/main.scss:css/main.css

python packages

        sudo apt install python3-bcrypt python3-flask python3-flask-babel 
        python3-flask-login python3-mypy python3-numpy python3-psycopg2
        python3-werkzeug python3-wtforms python3-flask-caching python3-requests

for development

        sudo apt install python3-pytest python3-pytest-cov python3-pytest-flask


to create the database, choose a existing OpenAtlas (https://openatlas.eu) 
postgresql database and run

        cd install
        cat 1_structure.sql 2_data_model.sql | psql -d <DATABASE_NAME> -f -

Or run the script if you have the correct database credentials in "instance/production.py"
    
        python3 /install/install_script.py
