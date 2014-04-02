## weghalen sensitive data (config.py remote_config.py local_config.py)

git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch config.py remote_config.py local_config.py' --prune-empty --tag-name-filter cat -- --all
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --aggressive --prune=now

# initial add opensource repo
git remote add opensource git@github.com:viaict/viaduct.git
git push -f opensource master

# on every push to master branch on server
git push opensource master

# for all pull requests
- merge on the opensource repo
on server: 
git pull opensource master
