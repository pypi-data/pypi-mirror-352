# wagtail-2fa-v6

A fork of [`wagtail-2fa`](https://github.com/LabD/wagtail-2fa) updated for **Wagtail 6+** and **Django 5.2+**.Provides Time-based One-Time Password (TOTP) two-factor authentication in the Wagtail admin.

Use apps like **Authy**, **Google Authenticator**, or **1Password** to secure your Wagtail login.

📖 [Django OTP Documentation](https://django-otp-official.readthedocs.io)

* * *

## Installation

    pip install wagtail-2fa-v6

Then add the following to your `INSTALLED_APPS` in `settings.py`:

    INSTALLED_APPS = [
        # ...
        'wagtail_2fa',
        'django_otp',
        'django_otp.plugins.otp_totp',
        # ...
    ]

Next, add the middleware **after** `AuthenticationMiddleware`:

    MIDDLEWARE = [
        # ... other middleware
        # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    
        'wagtail_2fa.middleware.VerifyUserMiddleware',
    
        # 'wagtail.core.middleware.SiteMiddleware',
        # ... other middleware
    ]

Run migrations:

    python manage.py migrate

* * *

## Settings

Set the following in your Django `settings.py` file:

* `WAGTAIL_2FA_REQUIRED` (default `False`):Force 2FA login for all staff, superusers, and users with access to the Wagtail admin.
  
* `WAGTAIL_2FA_OTP_TOTP_NAME` (default `False`):Issuer name for authenticator app. Defaults to `WAGTAIL_SITE_NAME` if set.(Sets `OTP_TOTP_ISSUER` under the hood.)
  

* * *

## Making 2FA Optional

To make 2FA **optional** (enabled per group), replace the middleware in your settings:

    MIDDLEWARE = [
        # ...
        # 'wagtail_2fa.middleware.VerifyUserMiddleware',
        'wagtail_2fa.middleware.VerifyUserPermissionsMiddleware',
        # ...
    ]

* This adds a checkbox to group permissions to enable or disable 2FA.
* **Superusers** are always required to use 2FA.

* * *

## Sandbox

To run a sandbox environment:

1. Create a virtual environment with Python 3.8
2. Activate it
3. Run:

    make sandbox

Access the admin at: [http://localhost:8000/admin/](http://localhost:8000/admin/)

Login credentials:

* **E-mail:** `superuser@example.com`
* **Password:** `testing`