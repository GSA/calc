## Authentication and authorization

CALC uses cloud.gov's [User Account and Authentication (UAA)](https://cloud.gov/docs/apps/leveraging-authentication/) server to authenticate users. Django's typical username/password authentication is not used.

When a user logs in via UAA, their email address is looked up in Django's user database; if a matching email is found, the user is logged in. If not found, the user is *not* logged in, and will be shown an error message.

### Permission groups

CALC uses permission groups (also known as "roles") for easily managing various lower-level permissions of authorized users. In addition, some users should be given [**staff** status](https://docs.djangoproject.com/en/1.11/ref/contrib/auth/#django.contrib.auth.models.User.is_staff), which allows them to log in to CALC's Django admin interface.

Authorization is set up as follows:

* **Non-staff users** in the **Contract Officers** group can upload individual price lists for approval.
* **Staff users** in the **Data Administrators** group can
  * create and edit users and assign them to groups,
  * review submitted price lists and approve/reject/retire them,
  * bulk upload data exports (only Region 10 data for now).
* **Staff users** in the **Technical Support Specialists** group can view attempted price list submissions that any users have made.
* **Superusers** can do anything, but only infrastructure/operational engineers should be given this capability.

Running `docker-compose run app python manage.py initgroups` will initialize or update all permission groups.

### Initial user creation

During development, a menu is available at the top of every page which allows you to quickly log in as a variety of example users, each of which represents a different kind of CALC role.

Otherwise, you can create an initial superuser by running:

```sh
docker-compose run app python manage.py createsuperuser --noinput --username <USER_NAME> --email <USER_EMAIL>
```

where `<USER_EMAIL>` is a valid `@gsa.gov` email address, and `<USER_NAME>` is a descriptive (but ultimately unimportant) account name (e.g., `jseppi`).

This will create a user without a password, which is fine since CALC doesn't use password authentication.

Once the initial superuser is created, that user can log in to the admin interface and create additional user records and assign permissions to them.
