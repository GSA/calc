## Email

CALC sends email in HTML and plaintext format.

Absolute URLs in the emails are generated via the
[Django "sites" framework][sites], so you will need to use the
CALC admin UI to configure the domain of the singleton `Site` model
to match the host and port of your deployment.

For example, if your CALC instance is at http://localhost:8000/, you should
set your `Site` model's domain to `localhost:8000`.

All other email configuration options are defined via
[environment variables](environment.md).

### Sending test emails

The `send_test_html_email` management command can be used to send
emails and ensure that they're received and/or render properly, with
proper links back to your CALC instance. To use it, just supply
the email addresses of the recipients like so:

```
docker-compose run app python manage.py send_test_html_email foo@example.org bar@example.org
```

You can also send "example" versions of all CALC emails to a single
email address like so:

```
docker-compose run app python manage.py send_example_emails foo@example.org
```

### Reading email in development

As part of our [Docker setup](setup.md), we use a container with
[MailCatcher][] to make it easy to read the emails sent by the app. You
can view it at port 1080: http://localhost:1080.

### Iterating on email in development

All emails have "example" versions that can be found on the
["Emails" section of the style guide][styleguide]. You can load these
in your browser, make changes to the email template, and see the
changes in your browser just as you would with any standard Django view.

[sites]: https://docs.djangoproject.com/en/1.10/ref/contrib/sites/
[MailCatcher]: https://mailcatcher.me/
[styleguide]: https://calc-dev.app.cloud.gov/styleguide/#emails
