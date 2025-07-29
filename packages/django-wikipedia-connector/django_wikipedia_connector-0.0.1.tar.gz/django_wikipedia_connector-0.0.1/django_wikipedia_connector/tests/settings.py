########################################################################################################################
#                                                                                                                      #
#                                      Django settings to be used during testing                                       #
#                                                                                                                      #
########################################################################################################################

SECRET_KEY = "super-secret-key"  # nosec

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_musicbrainz_connector",
    "django_wikipedia_connector",
]

DATABASES = {
    # SQLite option. SQLite is adequate for most functionality. Does not support `distinct` though:
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "TEST": {
            "NAME": "test-db",
        },
    },
}

ROOT_URLCONF = "django_wikipedia_connector.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

USE_TZ = True
