.. start-no-pypi

.. image:: https://img.shields.io/pypi/v/wagtail-2fa-v6.svg
   :alt: PyPI version
   :target: https://pypi.org/project/wagtail-2fa-v6/

.. image:: https://img.shields.io/github/license/ravigupta-art/wagtail-2fa-v6.svg
   :alt: License
   :target: https://github.com/ravigupta-art/wagtail-2fa-v6/blob/main/LICENSE

.. end-no-pypi

===========
wagtail-2fa-v6
===========

A fork of `wagtail-2fa <https://github.com/LabD/wagtail-2fa>`_ updated for Wagtail 6+ and Django 5.2+.  
Provides Time-based One-Time Password (TOTP) two-factor authentication in the Wagtail admin. This
allows you to use various apps like Authy, Google Authenticator, or
1Password.


.. _django-otp: https://django-otp-official.readthedocs.io


Installation
============

.. code-block:: shell

   pip install wagtail-2fa-v6


Then add the following lines to the ``INSTALLED_APPS`` list in your Django
settings:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'wagtail_2fa',
        'django_otp',
        'django_otp.plugins.otp_totp',
        # ...
    ]

Next add the required middleware to the ``MIDDLEWARE``. It should come
after the AuthenticationMiddleware:

.. code-block:: python

    MIDDLEWARE = [
        # .. other middleware
        # 'django.contrib.auth.middleware.AuthenticationMiddleware',

        'wagtail_2fa.middleware.VerifyUserMiddleware',

        # 'wagtail.core.middleware.SiteMiddleware',
        # .. other middleware
    ]

Migrate your database:

.. code-block:: shell

   python manage.py migrate



Settings
========

The following settings are available (Set via your Django settings):

- ``WAGTAIL_2FA_REQUIRED`` (default ``False``): When set to True all
  staff, superuser and other users with access to the Wagtail Admin site
  are forced to login using two factor authentication.
- ``WAGTAIL_2FA_OTP_TOTP_NAME`` (default: ``False``): The issuer name to
  identify which site is which in your authenticator app. If not set and
  ``WAGTAIL_SITE_NAME`` is defined it uses this. sets ``OTP_TOTP_ISSUER``
  under the hood.


Making 2FA optional
===================

With the default ``VerifyUserMiddleware`` middleware, 2FA is enabled for every user.
To make 2FA optional, use the ``VerifyUserPermissionsMiddleware`` middleware instead.

To do so, use the ``VerifyUserPermissionsMiddleware`` middleware instead of the ``VerifyUserMiddleware`` in your Django settings:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        # 'wagtail_2fa.middleware.VerifyUserMiddleware',
        'wagtail_2fa.middleware.VerifyUserPermissionsMiddleware',
        # ...
    ]

When this middleware is used, a checkbox is added to the group permissions
and 2FA can be enabled or disabled per group.

2FA is always enabled for superusers, regardless of the middleware used.


Sandbox
=======

First create a new virtualenv with Python 3.8 and activate it. Then run
the following commands:

.. code-block:: shell

   make sandbox


You can then visit http://localhost:8000/admin/ and login with the following
credentials:

- E-mail: ``superuser@example.com``
- Password: ``testing``
