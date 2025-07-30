Quick start
-----------

1. Add ``moni_auth`` to your ``INSTALLED_APPS`` setting like this::

    INSTALLED_APPS = [
        ...,
        "moni_auth",
    ]

2. Include the moni-auth URLconf in your ``urls.py`` like this::

    path("moni-auth/", include("moni_auth.urls")),
    path("admin/login/", CustomAdminLoginView.as_view()), # Import this view from moni_auth.views

3. Include the exception handler into the ``REST_FRAMEWORK`` config::

    REST_FRAMEWORK = {
        ...,
        'EXCEPTION_HANDLER': 'moni_auth.exceptions.custom_exception_handler',
    }

4. Add the following variables to the settings::

    MONI_AUTH = {
        "JWT_SECRET_KEY": env.str("JWT_SECRET_KEY", "DJjZ1sFPZAf1cfA0yqd3ufvLbc7E1r_JYMuu3Rqx5Pk"),
        "JWT_DEBUG": env.bool("JWT_DEBUG", False),
        "JWT_KEY": env.str("JWT_KEY", "jwt_wt"), # -> Main JWT for the service
        "JWT_KEYS": env.list("JWT_KEYS", default=["jwt_wt", "jwt_cs"]), # -> Array of JWTs that will be checked on the BaseJWTPermission to check for pages
        "BO_AUTH_LOGIN_URL": env.str("BO_AUTH_LOGIN_URL", "http://localhost:3000/login"),
        "AUTHENTICATION_SERVICE_URL": env.str("AUTHENTICATION_SERVICE_URL", "http://auth-django-1:8000"),
        "SHARED_SECRET_TOKEN": env.str("SHARED_SECRET_TOKEN", "3bqLVv3TlI_-2x2vEwN5N0Q_6IuX7n5kCnpJhZ8UAGo4xImfD"),
        "PRODUCTS": {}, # -> Import the product constants for the project
    }

