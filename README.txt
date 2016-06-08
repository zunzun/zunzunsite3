You will need to install scipy, matplotlib, django, beautifulsoup and
reportlab to run this software.  On Debian and Ubuntu, you can run:

apt-get install python-scipy python-matplotlib
apt-get install python-django python-beautifulsoup
apt-get install python-reportlab python-reportlab-accel


then install the pyeq3 fitting code with these commands:

apt-get install python-pip
pip install pyeq3


You can now cd to the project's top-level directory and
run the django development server with the command:

python manage.py runserver

and open the url http://127.0.0.1:8000/ in a browser. Cool!


NOTES: the code uses Unix-style process forking, and this
is not available on the  Windows operating system.

My tests show that while both mod_wsgi and gunicorn work fine
for Django production servers, the uwsgi process model would not
allow os.fork() calls to work as required for this software.
