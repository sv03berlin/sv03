# bootstrap
wget https://github.com/twbs/bootstrap/releases/download/v5.0.2/bootstrap-5.0.2-dist.zip
unzip bootstrap-5.0.2-dist.zip
mv bootstrap-5.0.2-dist bootstrap
mv bootstrap ./clubapp/static/
rm bootstrap-5.0.2-dist.zip

# github ribbon
wget https://raw.githubusercontent.com/simonwhitaker/github-fork-ribbon-css/gh-pages/gh-fork-ribbon.css
mv gh-fork-ribbon.css ./clubapp/static/ext/gh.css

# tomselect
wget https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/js/tom-select.complete.min.js
mv tom-select.complete.min.js ./clubapp/static/ext/tom-select.min.js
wget https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.min.css
mv tom-select.min.css ./clubapp/static/ext/tom-select.min.css
wget https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.min.css.map
mv tom-select.min.css.map ./clubapp/static/ext/tom-select.min.css.map

# calendar
wget https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js
mv index.global.min.js ./clubapp/static/ext/fullcalendar.min.js

# flatpikr
wget https://registry.npmjs.org/flatpickr/-/flatpickr-4.6.13.tgz
mkdir -p temp_flatpickr
tar -xzf flatpickr-4.6.13.tgz -C temp_flatpickr
mkdir -p staticfiles
cp -r temp_flatpickr/package/dist clubapp/static/flatpickr
rm -rf temp_flatpickr
rm flatpickr-4.6.13.tgz
