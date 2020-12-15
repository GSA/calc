from functools import wraps
from collections import namedtuple
from typing import List, Any
from django.conf.urls import url
from django.template.loader import render_to_string
from django.shortcuts import render


class Steps:
    '''
    The `Steps` class makes it easier to consolidate the view logic of
    multi-step workflows.

    The `Steps` constructor takes a format string representing what
    the template path for each step looks like:

        >>> steps = Steps('data_capture/tests/my_step_{}.html')

    The `@step` view decorator can be used to "register" steps in the
    workflow.  Each step's function name is expected to end with
    a number, and the steps are expected to be defined in
    ascending order, e.g.:

        >>> @steps.step
        ... def step_1(request, step): pass

        >>> @steps.step
        ... def step_2(request, step): pass

    (What's that extra `step` argument?  We'll get to that in a moment!)

    Breaking this ordering, e.g. by skipping numbers, is not allowed:

        >>> @steps.step
        ... def step_5(request, step): pass
        Traceback (most recent call last):
        ...
        ValueError: Expected "step_5" to end with the number 3

    At this point, our example workflow has two steps:

        >>> steps.num_steps
        2

    URL patterns for our steps are automatically defined, too, and can
    be included via Django's standard `include()` function. The names
    of each view will be identical to their view function's name:

        >>> steps.urls
        [<RegexURLPattern step_1 ^1$>, <RegexURLPattern step_2 ^2$>]

    Now, what's that `step` argument passed into each view function?

    It's a `StepRenderer` instance bound to the particular step that the
    view represents, and it provides some tools that make it easy to
    render steps.

    `StepRenderer` instances can also be retrieved manually if needed:

        >>> step1 = steps.get_step_renderer(1)

    A `StepRenderer` instance can be used to easily access
    commonly-used view logic, e.g.:

        >>> step1.number
        1

        >>> step1.steps.num_steps
        2

        >>> step1.description
        'step 1 of 2'

    Tools for templates and their contexts are also available.

    The `context()` function builds a context dictionary that always
    contains a `step` key referring to the `StepRenderer` instance for
    that step:

        >>> ctx = step1.context({'foo': 'bar'})
        >>> ctx['foo']
        'bar'
        >>> ctx['step']
        <StepRenderer for step 1 of 2>

    The `template_name` property always refers to the template for the step:

        >>> step1.template_name
        'data_capture/tests/my_step_1.html'

    And `render`/`render_to_string` ties everything together:

        >>> step1.render_to_string({'foo': 'bar'})
        'Hello from step 1 of 2! foo is bar.'

    Optionally, labels can be assigned to steps, which makes it
    easy to create widgets that indicate the current step to
    end-users:

        >>> steps = Steps('step_{}.html')

        >>> @steps.step(label='foo')
        ... def step_1(request, step): pass

    The widget is easily accessible from templates:

        >>> ctx = steps.get_step_renderer(1).context()
        >>> ctx['step'].widget
        <StepsWidget for step 1 of 1: foo>

    The widget is a callable that returns HTML, so you can use it
    in templates with something like {{ step.widget }}.
    '''

    def __init__(self, template_format, extra_ctx_vars=None,
                 extra_ctx_processors=None):
        self.extra_ctx_vars = extra_ctx_vars or {}
        self.extra_ctx_processors = extra_ctx_processors or []
        self.template_format = template_format
        self._views: List[Any] = []

    def _build_step_view(self, func, label=None):
        step_number = self.num_steps + 1

        if not func.__name__.endswith(str(step_number)):
            raise ValueError('Expected "{}" to end with the number {}'.format(
                func.__name__,
                step_number
            ))

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['step'] = self.get_step_renderer(step_number)
            return func(*args, **kwargs)

        # We're ignoring the type checking here due to:
        # https://github.com/python/mypy/issues/2087
        wrapper.label = label  # type: ignore

        self._views.append(wrapper)
        return wrapper

    def step(self, func=None, **kwargs):
        if func is None:
            # We were called in the form `@step()` w/ possible kwargs.
            return lambda f: self._build_step_view(f, **kwargs)
        # We were called in the form `@step`, w/o kwargs.
        return self._build_step_view(func)

    def get_step_renderer(self, step_number):
        return StepRenderer(self, step_number)

    @property
    def labels(self):
        return [view.label for view in self._views]

    @property
    def urls(self):
        urlpatterns = []

        for i in range(self.num_steps):
            view = self._views[i]
            regex = r'^' + str(i + 1) + r'$'
            urlpatterns.append(url(regex, view, name=view.__name__))

        return urlpatterns

    @property
    def num_steps(self):
        return len(self._views)


class StepRenderer:
    '''
    An object representing a particular step of a multi-step
    workflow, used to easily access commonly-used view logic.

    It's created automatically by `Steps`--you'll never
    need to manually call the constructor yourself.
    '''

    def __init__(self, steps, step_number):
        self.steps = steps
        self.number = step_number

    def context(self, context=None, request=None):
        final_ctx = {'step': self}
        final_ctx.update(self.steps.extra_ctx_vars)
        if request is not None:
            for processor in self.steps.extra_ctx_processors:
                final_ctx.update(processor(request))
        if context:
            final_ctx.update(context)
        return final_ctx

    @property
    def widget(self):
        return StepsWidget(labels=self.steps.labels, current=self.number)

    @property
    def template_name(self):
        return self.steps.template_format.format(self.number)

    def render(self, request, context=None):
        return render(request, self.template_name,
                      self.context(context, request))

    def render_to_string(self, context=None):
        return render_to_string(self.template_name, self.context(context))

    @property
    def description(self):
        return "step {} of {}".format(
            self.number,
            self.steps.num_steps
        )

    def __repr__(self):
        return '<{} for {}>'.format(
            self.__class__.__name__,
            self.description
        )


class StepsWidget:
    '''
    The steps widget can be used to visualize the user's progress through a
    multi-step process.

    While it is described as a "widget", it is not actually a widget
    in the Django sense--i.e., it is not used to present users with
    a form UI.
    '''

    _Step = namedtuple('Step', ['label', 'number', 'current'])

    def __init__(self, labels, current):
        self.steps = [
            self._Step(label=label, number=i, current=(i == current))
            for label, i in zip(labels, range(1, len(labels) + 1))
        ]
        self.current_step = self.steps[current - 1]
        for step in self.steps:
            if not step.label:
                raise ValueError('Step {} has no label'.format(
                    step.number
                ))

    def render(self):
        return render_to_string('frontend/steps.html', self.__dict__)

    def __call__(self):
        '''
        A convenience for rendering the widget directly from a Django
        template.
        '''

        return self.render()

    def __repr__(self):
        return '<{} for step {} of {}: {}>'.format(
            self.__class__.__name__,
            self.current_step.number,
            len(self.steps),
            self.current_step.label
        )
