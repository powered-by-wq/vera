set -e
if [ "$LINT" ]; then
    flake8 vera tests
else
    rm -f vera/*/migrations/0*py tests/swap_app/migrations/0*py

    python -c "import tests"
    celery worker -A tests &
    python setup.py test

    killall celery
    rm -f vera/*/migrations/0*py tests/swap_app/migrations/0*py

    export DJANGO_SETTINGS_MODULE=tests.swap_settings
    python -c "import tests"
    celery worker -A tests &
    python setup.py test
fi
