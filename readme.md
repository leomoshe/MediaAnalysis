## GIT
# Requisites
git (\\prfs1\groups\SpsTeam\Tools\Git-2.29.2.3-64-bit.exe, \\mntfs\msdn_pim\Python&Git\)
SourceTree gui, optional (\\prfs1\groups\SpsTeam\Tools\SourceTreeSetup-3.4.12.exe + ndp48-x86-x64-allos-enu.exe)

# git config
$ vi /c/Users/e303610901/.gitconfig
[alias]
        unstage = reset HEAD --
        last = log -1 HEAD
        como = !git status | grep modified | cut -d':' -f2 | xargs git checkout
        admo = !git status | grep modified | cut -d':' -f2 | xargs git add
        adre = !git status | grep renamed | cut -d':' -f2
        rmde = !git status | grep deleted | cut -d':' -f2 | xargs git rm
[user]
        email = leozilber@Police.gov.il
        name = Leo Zylber

# Create local and remote repo (only in order to create a new project)
TALI10-HB77 $ cd ../git_repo/
TALI10-HB77 $ git init --bare
TALI10-HB77 $ cd ../fast/
TALI10-HB77 $ git init
TALI10-HB77 $ git remote add origin /c/dev/git_repo/
...
MNTSP19LEO $ git clone file:////tali10-hb77/git_repo fast

## Development environment
# Requisites
VS code (\\mntfs\msdn_pim\Visual Studio\Visual Studio Code\VSCodeUserSetup-x64-1.73.1.exe, \extensions\, \\mnthaaravs\Tools\Visual Studio Code\Extensions [Python v2021.8.1159798656 ms-python: Python extension for Visual Studio Code])
python (\\prfs1\groups\SpsTeam\Tools\python-3.10.8-amd64.exe, \\mntfs\msdn_pim\Python&Git\). Important: "Add Python to environment variables"

./service/readme.md
$ python -m venv .venv
$ source .venv/Scripts/activate

# Requisites
Docker for Windows (\\mntfs\msdn_pim\Tools\Docker for Windows\)



