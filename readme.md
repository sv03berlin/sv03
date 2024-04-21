# Clubapp
This is a platform to manage some this for your local sailing sportsclub.

### VsCode
1. Docker and Remote Containers extensions required
2. open git root
3. green double boomerang thing in the left bottom => Reopen in Container
4. Rebuild close etc. => green double boomerang thing

```bash
./load_deps.sh
pip install -r requirements-dev.txt
./manage.py collectstatic
./manage.py migrate
./manage.py run
```

model.py changes
```bash
./manage.py makemigrations
./manage.py migrate
```

## Accounts
superuser : superuser

``docker exec -it clubapp python3 /code/clubapp/manage.py migrate``
``docker exec -it clubapp python3 /code/clubapp/manage.py createsuperuser``

## test data and fixtures

`manage.py dumpdata --natural-foreign --natural-primary --indent 4 -o test_data.json`
