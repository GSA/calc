import abc

from uswds_forms import UswdsDateWidget


class AbstractBrowserForm(abc.ABC):
    '''
    This abstract base class represents a form on a web page.
    '''

    @staticmethod
    def get_id_for_radio(name, number):
        '''
        Given a radio button's name and its order in the radio button
        list, return the `id` of its <input> element. This is specific
        to the way Django assigns ids to its radio buttons.
        '''

        return 'id_{}_{}'.format(name, number)

    def set_date(self, name, month, day, year):
        '''
        Given a split date widget's name, set its individual fields.
        '''

        names = UswdsDateWidget.get_field_names(name)

        self.set_text(names.year, str(year))
        self.set_text(names.month, str(month))
        self.set_text(names.day, str(day))

    @abc.abstractmethod
    def set_text(self, name, value):
        '''
        Given a text input's name, set its value.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def set_radio(self, name, number):
        '''
        Set a radio button's value, given its name and its order in the
        radio button list.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def set_file(self, name, path):
        '''
        Set the value of a file input to the given absolute filesystem
        path.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def submit(self):
        '''
        Submit the form. Do not return until the result of the form
        has been loaded.
        '''

        raise NotImplementedError()


class AbstractBrowser(abc.ABC):
    '''
    This abstract base class represents a web browser that can be
    controlled via an API.
    '''

    @abc.abstractmethod
    def load(self, url):
        '''
        Load the given URL in the browser.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_title(self):
        '''
        Return the title of the current page, as a string.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_form(self, selector):
        '''
        Return an `AbstractBrowserForm` instance representing the form
        at the given CSS selector.
        '''

        raise NotImplementedError()
