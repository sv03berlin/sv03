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
mv tom-select.complete.min.js ./clubapp/static/ext/

wget https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/js/tom-select.complete.min.js.map
mv tom-select.complete.min.js.map ./clubapp/static/ext/

wget https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.min.css
mv tom-select.min.css ./clubapp/static/ext/

wget https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.min.css.map
mv tom-select.min.css.map ./clubapp/static/ext/

# calendar
wget https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js
mv index.global.min.js ./clubapp/static/ext/fullcalendar.min.js

# datepicker
wget https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.9.0/moment-with-locales.min.js
mv moment-with-locales.min.js ./clubapp/static/ext/

wget https://cdn.jsdelivr.net/npm/eonasdan-bootstrap-datetimepicker@4.17.49/build/js/bootstrap-datetimepicker.min.js
mv bootstrap-datetimepicker.min.js ./clubapp/static/ext/

wget https://cdn.jsdelivr.net/npm/eonasdan-bootstrap-datetimepicker@4.17.49/build/css/bootstrap-datetimepicker.min.css
mv bootstrap-datetimepicker.min.css ./clubapp/static/ext/

wget https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css
mv bootstrap-icons.css ./clubapp/static/ext/
wget https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/fonts/bootstrap-icons.woff
mv bootstrap-icons.woff ./clubapp/static/ext/fonts/
wget https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/fonts/bootstrap-icons.woff2
mv bootstrap-icons.woff2 ./clubapp/static/ext/fonts/

wget https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js
mv jquery.min.js ./clubapp/static/ext/
