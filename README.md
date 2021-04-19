# MyGamesList
A web-based games recommender system
<div>
  <img src="https://github.com/shaklain125/MyGamesList/blob/master/screenshots/home.png?raw=true" style="width: 100%;height: 800px;object-fit: cover;object-position: top;"/>
  <br>
</div>

### Open settings.py inside gamesproject folder and set PRODUCTION to False if it is not set

## WINDOWS

### Install python 3.6 if windows doesn't have it (python 3.7 may or may not work)

**FOR WINDOWS 32 BIT**
https://www.python.org/ftp/python/3.6.8/python-3.6.8.exe

**FOR WINDOWS 64 BIT**
https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe

---


**Add python 3.6 to environment path if it is not in the environment (check in cmd, by typing python or python3.6 to check the version)**

**Open command prompt in project root directory (directory where manage.py is located)**

### Install pip from site if python doesn't have it
http://pip.readthedocs.io/en/stable/installing/#do-i-need-to-install-pip

### Install virtualenv
```pip install virtualenv```

### Remove directory environment if exists
```rd /s /q environment_windows```

```python -m virtualenv  environment_windows --python=python && environment_windows\scripts\activate.bat && pip install -r requirements.txt```



## LINUX

### Install python 3.6 on linux
```cd /opt```
```sudo wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz```
```sudo tar -xvf Python-3.6.9.tgz && cd Python-3.6.8 && sudo ./configure && sudo make && sudo make install```

### NOTE
**IF YOU GET THIS ERROR THEN RUN THE FOLLOWING**
....: UserWarning: Could not import the lzma module. Your installed Python is incomplete....

```sudo apt-get install liblzma-dev && cd /opt/Python-3.6.9 && sudo ./configure && sudo make && sudo make install```
```source ./environment/bin/activate```

### Install pip from site if python doesn't have it
http://pip.readthedocs.io/en/stable/installing/#do-i-need-to-install-pip

### Install virtualenv
```pip install virtualenv --user```

### Remove directory environment if exists
```rm -r environment_linux```


```python3 -m virtualenv  environment_linux --python=python3.6 && source ./environment_linux/bin/activate && pip install -r requirements.txt```


--------------------------------------------------------------------------------------------------------------

### Run App
```python manage.py runserver 0.0.0.0:8080```

### Go to
http://127.0.0.1:8080/



-------------------------------------------------------
## IMPORTANT WHEN DEPLOYING:
Both environments are needed for deployment
linux environment is needed to manage backend and cron jobs 
windows environment is needed to run apache
