20up
========

20up is a program for the backup of a Spanish social network. This program downloads all of the photos, comments, and friends' information of a specific user.

If you have any problems, questions or improvements, please visit the Contact section of [20up web page](http://bmenendez.github.io/20up)

#### Executable file

You can generate your own executable for Windows and check the MD5SUM if you want. It is as easy as:

* Follow the instructions in the [official FAQ of 20up](http://bmenendez.github.io/20up/#Windows-dificil)
* Install [pyinstaller](http://www.pyinstaller.org/)
* Open cmd, go to your 20up folder and execute:

    pyinstaller --onefile 20up.py
    
* Go to 'dists' folder and execute:

    FCIV -md5 20up.exe
    
This way, you should have an MD5SUM calculated for your executable file. Now you are able to check this number with the one written in [the official 20up MD5SUM file](https://github.com/bmenendez/20up/blob/master/windows/MD5SUM).

#### Dockerized support

#### Build

```
export PROJECT_DIR=$HOME/Projects/20up
git clone https://github.com/bmenendez/20up.git $PROJECT_DIR
cd $PROJECT_DIR
docker build -t bmenendez/20up .
```

#### Run

```
export PROJECT_DIR=$HOME/Projects/20up
cd $PROJECT_DIR
mkdir download
docker run -it -v $PWD/download:/volume bmenendez/20up
```

#### Use

After following the instructions, you will find the downloaded assets in "$PROJECT_DIR/download" :)
