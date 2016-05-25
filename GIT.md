ClearMap Git Help 
=================


Install
-------

For a plain user to use the toolbox:

 * in terminal execute: 
 
    `cd basedirectory`
 
    `git clone https://github.com/ChristophKirst/ClearMap.git`


For a developer / programmer:

  * create account at github

  * got to [https://github.com/ChristophKirst/ClearMap](https://github.com/ChristophKirst/ClearMap) and press fork button 

  * in terminal execute:
	
	`cd basedirectory`

	`git clone https://github.com/ChristophKirst/ClearMap.git`
	
  * configure remotes (named upstream)
        
	`cd ClearMap`

	`git remote add upstream https://github.com/ChristophKirst/ClearMap.git`

	`git fetch upstream`


Backup
------

To backup your version in case you followed the developer / proogrammer route:

  * in terminal in the ClearMap directory execute:

      `git add -A`

      `git commit -m 'some description of what you did'`

      `git push`


Update
------    

Plain user:

  * in terminal in the iDisco directory execute
     
      `git pull`


Programmer: 

in case you want to update your code from the upstream repository

  * in terminal execute:
 
      `git fetch upstream`
      
      `git merge upstream/master`

  * if mergin fails, some files will be highlighted with <<<<<< >>>>>> entries, fix this manually

  * if you dont care about your own changes and simply want the plain new version:

      `git reset --hard upstream/master`

  * to force it to your fork on github use
       
	  `git push origin/master --force` 


Submitting
----------

In case you have something to contribute to the code:
 
  * follow the steps in the Backup section first

  * got to [https://github.com/ChristophKirst/ClearMap.git](https://github.com/ChristophKirst/ClearMap.git) and click pull request 
  
  * wait for us to accept the request


References
----------

ClearMap home:

  * [https://github.com/ChristophKirst/ClearMap](https://github.com/ChristophKirst/ClearMap)

A good source to get questions answered about github: 

  * [https://help.github.com/](https://help.github.com)
  * [http://git-scm.com/documentation](http://git-scm.com/documentation)

Git home:

  * [http://git-scm.com](http://git-scm.com/)


