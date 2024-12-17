*Note: is recommended to use Git Bash.*  

> [!NOTE]  
You can copy the project by doing  
$ git clone file:////tali10-hb77/git_repo  
And update yourself with the latest changes by doing  
$ git pull

# Overview
The project is made up of the manage unit, and 2 other units; process_media which extracts subtitles from the media, and process_srt, which converts the srt file to tsrt

# How to install Service
`This activity must be done within the folder service, and within the process media and process srt subfolders.`  
**Create a Virtual Environment**  
$ python -m venv .venv
$ python3 -m venv .venv
**Activate the Virtual Environment**  
$ source .venv/Scripts/activate
$ source .venv/bin/activate
**Install the Necessary Packages**  
$ pip install -r requirements.txt --no-index -f ./wheels/ --upgrade
$ pip install -r requirements_ubuntu.txt --no-index -f ./wheels_ubuntu/ --upgrade 
**The Virtual Environment can be deactived**  
$ deactivate  

# Configurations  
Each application (service, process_media, porcess_srt) has its configuration file  

<u>Common properties</u>  
 *host:* The value of variable host controls what address the development server listens to. By default, the value of host is set to 127.0.0.1 or localhost. you can make the server publicly available by setting the host to 0.0.0.0.  
*port:* The port on which each application listens.  
*output:* The folder where the results are saved.

**process_media/app.json**
>{  
&nbsp;&nbsp;&nbsp;&nbsp;"host": "0.0.0.0",  
&nbsp;&nbsp;&nbsp;&nbsp;"port": "5002",   
&nbsp;&nbsp;&nbsp;&nbsp;"output": "//tali10-hb77/data",  
&nbsp;&nbsp;&nbsp;&nbsp;"tmp": "//tali10-hb77/data/tmp"  
}  

*tmp:* Folder for intermediate internal processes.  

**process_srt/app.json**
>{  
&nbsp;&nbsp;&nbsp;&nbsp;"host": "0.0.0.0",  
&nbsp;&nbsp;&nbsp;&nbsp;"port": "5001",   
&nbsp;&nbsp;&nbsp;&nbsp;"domain": "http://mntdaniel:8501",  
&nbsp;&nbsp;&nbsp;&nbsp;"output": "//tali10-hb77/data"  
}

*domain:* [DANIEL???].  

**app.json**
>{  
&nbsp;&nbsp;&nbsp;&nbsp;"host": "0.0.0.0",  
&nbsp;&nbsp;&nbsp;&nbsp;"port": "5000",   
&nbsp;&nbsp;&nbsp;&nbsp;"dependencies": [  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{"id": "process_media", "port": "5002"},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{"id": "process_srta", "port": "5001"}  
&nbsp;&nbsp;&nbsp;&nbsp;]  
}

*dependencies:* Ports on which each of the sub-applications is executed.  

# How to run the Service  
There is the option to run the service as a web application(1), or the option to run each unit(process_srt, process_media) itself as a web application(2) or as an application(3).  

**As web applications**
```sequence
                 ------
Post ---------> | 5001 |  (2) process_srt
                 ------
                   ^
                  /
                 /
          ------
Post --> | 5000 |  (1) service
          ------
                \
                 \
                  V
                 ------
Post ---------> | 5002 |  (2) process_media
                 ------

```

## (1) As web application
<u>server</u>  
$ ./.venv/Scripts/python.exe app.py  
<u>client</u>  
$ curl -X POST --data-binary "@./data/shabtay.wav" "http://127.0.0.1:5000/process_media?fullpath=./data/shabtay.wav" --header "Content-Type: 'audio/wav'"  
$ ./.venv/Scripts/python.exe post.py --path ./data/shabtay.wav --type m
$ curl -X POST -d "@./data/shabtay.srt" "http://127.0.0.1:5000/process_srt" --header "Content-Type: 'text/plain; charset=utf-8'  
$ ./.venv/Scripts/python.exe post.py --path ./data/shabtay.srt --type s

## (2) process_media as web application 
<u>server</u>  
$ ./process_media/.venv/Scripts/python.exe app.py  
<u>client</u>  
$ curl -X POST --data-binary "@./data/shabtay.wav" "http://127.0.0.1:5002/process_media?fullpath=./data/shabtay.wav" --header "Content-Type: 'audio/wav'"  
$ ./.venv/Scripts/python.exe post.py --path ./data/shabtay.wav --type m

## (2) process_srt as web application 
<u>server</u>  
$ ./process_srt/.venv/Scripts/python.exe app.py  
<u>client</u>  
$ curl -X POST -d "@./data/shabtay.srt" "http://127.0.0.1:5001/process_srt" --header "Content-Type: 'text/plain; charset=utf-8'  
$ ./.venv/Scripts/python.exe post.py --path ./data/shabtay.srt --type s

## (3) process_media as application  
$ ./.venv/Scripts/python.exe app.py --path ../data/shabtay.wav  

## (3) process_srt as application  
$ ./.venv/Scripts/python.exe app.py --path ../data/shabtay.srt


python app.py --path ../data/282641_2022/


