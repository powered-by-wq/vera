set -e
if [ "$LINT" ]; then
    flake8 vera tests
else
    rm -f vera/*/migrations/0*py tests/swap_app/migrations/0*py
    python setup.py test
    rm -f vera/*/migrations/0*py tests/swap_app/migrations/0*py
    DJANGO_SETTINGS_MODULE=tests.swap_settings python setup.py test
fi
