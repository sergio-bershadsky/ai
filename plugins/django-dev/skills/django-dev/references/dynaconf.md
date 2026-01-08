# Dynaconf Configuration

Complete setup guide for Django with Dynaconf.

## Installation

```bash
pip install dynaconf[toml]
```

## Initial Setup

Create configuration files:

```
config/
├── __init__.py
├── settings.py           # Django + Dynaconf integration
├── settings.toml         # Default settings
├── settings.local.toml   # Local overrides (gitignored)
└── .secrets.toml         # Secrets (gitignored)
```

## settings.py

Replace Django's settings.py with Dynaconf integration:

```python
"""Django settings with Dynaconf integration."""
import os
from pathlib import Path
from dynaconf import Dynaconf

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Dynaconf configuration
settings = Dynaconf(
    envvar_prefix="DJANGO",
    settings_files=[
        "settings.toml",
        "settings.local.toml",  # Gitignored
        ".secrets.toml",        # Gitignored
    ],
    environments=True,
    env_switcher="DJANGO_ENV",
    root_path=Path(__file__).parent,
)

# Django settings from Dynaconf
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.get("DEBUG", False)
ALLOWED_HOSTS = settings.get("ALLOWED_HOSTS", [])

# Application definition
INSTALLED_APPS = [
    # Django apps
    "unfold",  # Before django.contrib.admin
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "ninja",

    # Local apps
    *settings.get("LOCAL_APPS", []),
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = settings.get("ROOT_URLCONF", "config.urls")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# Database from Dynaconf
DATABASES = {
    "default": {
        "ENGINE": settings.get("DATABASE_ENGINE", "django.db.backends.postgresql"),
        "NAME": settings.DATABASE_NAME,
        "USER": settings.get("DATABASE_USER", ""),
        "PASSWORD": settings.get("DATABASE_PASSWORD", ""),
        "HOST": settings.get("DATABASE_HOST", "localhost"),
        "PORT": settings.get("DATABASE_PORT", "5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = settings.get("LANGUAGE_CODE", "en-us")
TIME_ZONE = settings.get("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = settings.get("STATIC_URL", "/static/")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = settings.get("MEDIA_URL", "/media/")
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = settings.get("AUTH_USER_MODEL", "auth.User")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": settings.get("LOG_LEVEL", "INFO"),
    },
}
```

## settings.toml

Default settings (committed to git):

```toml
[default]
DEBUG = false
ALLOWED_HOSTS = []
LOG_LEVEL = "INFO"

DATABASE_ENGINE = "django.db.backends.postgresql"
DATABASE_NAME = "myproject"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5432"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

LOCAL_APPS = [
    "apps.users",
    "apps.products",
]

ROOT_URLCONF = "config.urls"
AUTH_USER_MODEL = "users.User"

[development]
DEBUG = true
ALLOWED_HOSTS = ["*"]
LOG_LEVEL = "DEBUG"

[staging]
ALLOWED_HOSTS = ["staging.example.com"]
LOG_LEVEL = "INFO"

[production]
ALLOWED_HOSTS = ["example.com", "www.example.com"]
LOG_LEVEL = "WARNING"
```

## .secrets.toml

Secrets (gitignored):

```toml
[default]
SECRET_KEY = "your-super-secret-key-here"

[development]
DATABASE_USER = "devuser"
DATABASE_PASSWORD = "devpassword"

[production]
# Use environment variables: @env DJANGO_DATABASE_PASSWORD
DATABASE_USER = "@env DJANGO_DATABASE_USER"
DATABASE_PASSWORD = "@env DJANGO_DATABASE_PASSWORD"
SECRET_KEY = "@env DJANGO_SECRET_KEY"
```

## .gitignore entries

```gitignore
# Dynaconf
settings.local.toml
.secrets.toml
```

## Environment Variables

Dynaconf reads from environment variables with prefix:

```bash
# Set environment
export DJANGO_ENV=production

# Override any setting
export DJANGO_DEBUG=false
export DJANGO_DATABASE_PASSWORD=mysecret
export DJANGO_SECRET_KEY=production-secret-key

# Lists use JSON format
export DJANGO_ALLOWED_HOSTS='["example.com", "www.example.com"]'
```

## Accessing Settings

In code, import the settings object:

```python
from django.conf import settings

# Access Dynaconf values
debug = settings.DEBUG
db_name = settings.DATABASE_NAME

# With defaults
timeout = settings.get("TIMEOUT", 30)

# Check environment
from config.settings import settings as dynaconf_settings
if dynaconf_settings.current_env == "production":
    # Production-specific code
    pass
```

## Validation

Add validation in settings.py:

```python
# Validate required settings
settings.validators.register(
    Validator("SECRET_KEY", must_exist=True),
    Validator("DATABASE_NAME", must_exist=True),
    Validator("DEBUG", is_type_of=bool),
)

settings.validators.validate()
```

## Docker Integration

In docker-compose.yml:

```yaml
services:
  web:
    environment:
      - DJANGO_ENV=production
      - DJANGO_SECRET_KEY=${SECRET_KEY}
      - DJANGO_DATABASE_HOST=db
      - DJANGO_DATABASE_PASSWORD=${DB_PASSWORD}
```

## Testing Configuration

Create `settings.test.toml`:

```toml
[testing]
DEBUG = false
DATABASE_NAME = "test_myproject"
```

Run tests with:

```bash
DJANGO_ENV=testing pytest
```
