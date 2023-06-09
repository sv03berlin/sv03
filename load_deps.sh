# bootstrap
wget https://github.com/twbs/bootstrap/releases/download/v5.0.2/bootstrap-5.0.2-dist.zip
unzip bootstrap-5.0.2-dist.zip
mv bootstrap-5.0.2-dist bootstrap
mv bootstrap /code/clubapp/static/
rm bootstrap-5.0.2-dist.zip

# github ribbon
wget https://raw.githubusercontent.com/simonwhitaker/github-fork-ribbon-css/gh-pages/gh-fork-ribbon.css
mv gh-fork-ribbon.css /code/clubapp/static/gh.css