import djclick as click

from data_capture import email


@click.command()
@click.argument('to', default='user@example.com')
def command(to):
    '''
    Send examples of all the email templates in the Data Capture application.
    '''

    for example in email.EXAMPLES:
        kwargs = {'to': [to]}
        kwargs.update(example)
        email.send_mail(**kwargs)
