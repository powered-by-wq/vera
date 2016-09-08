from .settings import (  # noqa
    SECRET_KEY,
    MIDDLEWARE_CLASSES,
    INSTALLED_APPS,
    ROOT_URLCONF,
    MEDIA_ROOT,
)

SWAP = True

INSTALLED_APPS += ("tests.swap_app",)
WQ_REPORT_MODEL = "swap_app.Record"
WQ_SITE_MODEL = "swap_app.Site"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'vera_swap_test',
        'USER': 'postgres',
    }
}
