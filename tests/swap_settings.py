from .settings import (  # noqa
    SECRET_KEY,
    MIDDLEWARE_CLASSES,
    INSTALLED_APPS,
    DATABASES,
    ROOT_URLCONF,
    MEDIA_ROOT,
)

SWAP = True

INSTALLED_APPS += ("tests.swap_app",)
WQ_REPORT_MODEL = "swap_app.Record"
WQ_SITE_MODEL = "swap_app.Site"
