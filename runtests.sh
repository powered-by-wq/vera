set -e
if [ "$LINT" ]; then
    flake8 vera tests --exclude migrations
    flake8 vera/migrations --ignore E501
else
    python setup.py test
    DJANGO_SETTINGS_MODULE=tests.swap_settings python setup.py test
fi
