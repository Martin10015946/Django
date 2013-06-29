
Production
==========

Applications to support Production at Unto This Last.  

## Current Apps

* Board Vision: visual interface for the machining files of the week
* Manual: record and edit inline help app
* Production: mother app: settings, urls, shared models, static files and templates. 
* Progress Report: interactive weekly production schedule
* Scripts: automated tasks
* Tools: record machining tools calibration and use
* UTL Timer: assembly timer

## Future

* TODO Machine Historty: interface to the CNC maching log (XML) 
* TODO Supplies: visual interface to the supplies management process and forms 
* TODO Transfer: offset Z and send to machine folder

## Install 

On our server:

`cd /c/django/production`  
`git pull`  
`httpd.exe -k restart`  

## Dependencies

* django_extensions

### Board vision

* cairo 1.8.10 (installed on windows via GTK+ >= 2.8)
* wxPython 2.8.12.1
* PIL 1.1.7
