

Configuration
-------------

.. autoclass:: Config
   :members:


Stream Helpers
--------------

.. autofunction:: stream_with_context

Useful Internals
----------------

.. autoclass:: flask.ctx.RequestContext
   :members:

.. data:: flask.globals.request_ctx

    The current :class:`~flask.ctx.RequestContext`. If a request context
    is not active, accessing attributes on this proxy will raise a
    ``RuntimeError``.

    This is an internal object that is essential to how Flask handles
    requests. Accessing this should not be needed in most cases. Most
    likely you want :data:`request` and :data:`session` instead.

.. autoclass:: flask.ctx.AppContext
   :members:

.. data:: flask.globals.app_ctx

    The current :class:`~flask.ctx.AppContext`. If an app context is not
    active, accessing attributes on this proxy will raise a
    ``RuntimeError``.

    This is an internal object that is essential to how Flask handles
    requests. Accessing this should not be needed in most cases. Most
    likely you want :data:`current_app` and :data:`g` instead.

.. autoclass:: flask.blueprints.BlueprintSetupState
   :members:

.. _core-signals-list:

Signals
-------

Signals are provided by the `Blinker`_ library. See :doc:`signals` for an introduction.

.. _blinker: https://blinker.readthedocs.io/

.. data:: template_rendered

   This signal is sent when a template was successfully rendered. The
   signal is invoked with the instance of the template as `template`
   and the context as dictionary (named `context`).

   Example subscriber::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import template_rendered
        template_rendered.connect(log_template_renders, app)

.. data:: flask.before_render_template
   :noindex:

   This signal is sent before template rendering process. The
   signal is invoked with the instance of the template as `template`
   and the context as dictionary (named `context`).

   Example subscriber::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import before_render_template
        before_render_template.connect(log_template_renders, app)

.. data:: request_started

   This signal is sent when the request context is set up, before
   any request processing happens. Because the request context is already
   bound, the subscriber can access the request with the standard global
   proxies such as :class:`~flask.request`.

   Example subscriber::

        def log_request(sender, **extra):
            sender.logger.debug('Request context is set up')

        from flask import request_started
        request_started.connect(log_request, app)

.. data:: request_finished

   This signal is sent right before the response is sent to the client.
   It is passed the response to be sent named `response`.

   Example subscriber::

        def log_response(sender, response, **extra):
            sender.logger.debug('Request context is about to close down. '
                                'Response: %s', response)

        from flask import request_finished
        request_finished.connect(log_response, app)

.. data:: got_request_exception

    This signal is sent when an unhandled exception happens during
    request processing, including when debugging. The exception is
    passed to the subscriber as ``exception``.

    This signal is not sent for
    :exc:`~werkzeug.exceptions.HTTPException`, or other exceptions that
    have error handlers registered, unless the exception was raised from
    an error handler.

    This example shows how to do some extra logging if a theoretical
    ``SecurityException`` was raised:

    .. code-block:: python

        from flask import got_request_exception

        def log_security_exception(sender, exception, **extra):
            if not isinstance(exception, SecurityException):
                return

            security_logger.exception(
                f"SecurityException at {request.url!r}",
                exc_info=exception,
            )

        got_request_exception.connect(log_security_exception, app)

.. data:: request_tearing_down

   This signal is sent when the request is tearing down. This is always
   called, even if an exception is caused. Currently functions listening
   to this signal are called after the regular teardown handlers, but this
   is not something you can rely on.

   Example subscriber::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import request_tearing_down
        request_tearing_down.connect(close_db_connection, app)

   As of Flask 0.9, this will also be passed an `exc` keyword argument
   that has a reference to the exception that caused the teardown if
   there was one.

.. data:: appcontext_tearing_down

   This signal is sent when the app context is tearing down. This is always
   called, even if an exception is caused. Currently functions listening
   to this signal are called after the regular teardown handlers, but this
   is not something you can rely on.

   Example subscriber::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import appcontext_tearing_down
        appcontext_tearing_down.connect(close_db_connection, app)

   This will also be passed an `exc` keyword argument that has a reference
   to the exception that caused the teardown if there was one.

.. data:: appcontext_pushed

   This signal is sent when an application context is pushed. The sender
   is the application. This is usually useful for unittests in order to
   temporarily hook in information. For instance it can be used to
   set a resource early onto the `g` object.

   Example usage::

        from contextlib import contextmanager
        from flask import appcontext_pushed

        @contextmanager
        def user_set(app, user):
            def handler(sender, **kwargs):
                g.user = user
            with appcontext_pushed.connected_to(handler, app):
                yield

   And in the testcode::

        def test_user_me(self):
            with user_set(app, 'john'):
                c = app.test_client()
                resp = c.get('/users/me')
                assert resp.data == 'username=john'

   .. versionadded:: 0.10

.. data:: appcontext_popped

   This signal is sent when an application context is popped. The sender
   is the application. This usually falls in line with the
   :data:`appcontext_tearing_down` signal.

   .. versionadded:: 0.10

.. data:: message_flashed

   This signal is sent when the application is flashing a message. The
   messages is sent as `message` keyword argument and the category as
   `category`.

   Example subscriber::

        recorded = []
        def record(sender, message, category, **extra):
            recorded.append((message, category))

        from flask import message_flashed
        message_flashed.connect(record, app)

   .. versionadded:: 0.10


Class-Based Views
-----------------

.. versionadded:: 0.7

.. currentmodule:: None

.. autoclass:: flask.views.View
   :members:

.. autoclass:: flask.views.MethodView
   :members:

.. _url-route-registrations:

URL Route Registrations
-----------------------

Generally there are three ways to define rules for the routing system:

1.  You can use the :meth:`flask.Flask.route` decorator.
2.  You can use the :meth:`flask.Flask.add_url_rule` function.
3.  You can directly access the underlying Werkzeug routing system
    which is exposed as :attr:`flask.Flask.url_map`.

Variable parts in the route can be specified with angular brackets
(``/user/<username>``). By default a variable part in the URL accepts any
string without a slash however a different converter can be specified as
well by using ``<converter:name>``.

Variable parts are passed to the view function as keyword arguments.

The following converters are available:

=========== ===============================================
`string`    accepts any text without a slash (the default)
`int`       accepts integers
`float`     like `int` but for floating point values
`path`      like the default but also accepts slashes
`any`       matches one of the items provided
`uuid`      accepts UUID strings
=========== ===============================================

Custom converters can be defined using :attr:`flask.Flask.url_map`.

Here are some examples::

    @app.route('/')
    def index():
        pass

    @app.route('/<username>')
    def show_user(username):
        pass

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        pass

An important detail to keep in mind is how Flask deals with trailing
slashes. The idea is to keep each URL unique so the following rules
apply:

1. If a rule ends with a slash and is requested without a slash by the
   user, the user is automatically redirected to the same page with a
   trailing slash attached.
2. If a rule does not end with a trailing slash and the user requests the
   page with a trailing slash, a 404 not found is raised.

This is consistent with how web servers deal with static files. This
also makes it possible to use relative link targets safely.

You can also define multiple rules for the same function. They have to be
unique however. Defaults can also be specified. Here for example is a
definition for a URL that accepts an optional page::

    @app.route('/users/', defaults={'page': 1})
    @app.route('/users/page/<int:page>')
    def show_users(page):
        pass

This specifies that ``/users/`` will be the URL for page one and
``/users/page/N`` will be the URL for page ``N``.

If a URL contains a default value, it will be redirected to its simpler
form with a 301 redirect. In the above example, ``/users/page/1`` will
be redirected to ``/users/``. If your route handles ``GET`` and ``POST``
requests, make sure the default route only handles ``GET``, as redirects
can't preserve form data. ::

   @app.route('/region/', defaults={'id': 1})
   @app.route('/region/<int:id>', methods=['GET', 'POST'])
   def region(id):
      pass

Here are the parameters that :meth:`~flask.Flask.route` and
:meth:`~flask.Flask.add_url_rule` accept. The only difference is that
with the route parameter the view function is defined with the decorator
instead of the `view_func` parameter.

=============== ==========================================================
`rule`          the URL rule as string
`endpoint`      the endpoint for the registered URL rule. Flask itself
                assumes that the name of the view function is the name
                of the endpoint if not explicitly stated.
`view_func`     the function to call when serving a request to the
                provided endpoint. If this is not provided one can
                specify the function later by storing it in the
                :attr:`~flask.Flask.view_functions` dictionary with the
                endpoint as key.
`defaults`      A dictionary with defaults for this rule. See the
                example above for how defaults work.
`subdomain`     specifies the rule for the subdomain in case subdomain
                matching is in use. If not specified the default
                subdomain is assumed.
`**options`     the options to be forwarded to the underlying
                :class:`~werkzeug.routing.Rule` object. A change to
                Werkzeug is handling of method options. methods is a list
                of methods this rule should be limited to (``GET``, ``POST``
                etc.). By default a rule just listens for ``GET`` (and
                implicitly ``HEAD``). Starting with Flask 0.6, ``OPTIONS`` is
                implicitly added and handled by the standard request
                handling. They have to be specified as keyword arguments.
=============== ==========================================================


View Function Options
---------------------

For internal usage the view functions can have some attributes attached to
customize behavior the view function would normally not have control over.
The following attributes can be provided optionally to either override
some defaults to :meth:`~flask.Flask.add_url_rule` or general behavior:

-   `__name__`: The name of a function is by default used as endpoint. If
    endpoint is provided explicitly this value is used. Additionally this
    will be prefixed with the name of the blueprint by default which
    cannot be customized from the function itself.

-   `methods`: If methods are not provided when the URL rule is added,
    Flask will look on the view function object itself if a `methods`
    attribute exists. If it does, it will pull the information for the
    methods from there.

-   `provide_automatic_options`: if this attribute is set Flask will
    either force enable or disable the automatic implementation of the
    HTTP ``OPTIONS`` response. This can be useful when working with
    decorators that want to customize the ``OPTIONS`` response on a per-view
    basis.

-   `required_methods`: if this attribute is set, Flask will always add
    these methods when registering a URL rule even if the methods were
    explicitly overridden in the ``route()`` call.

Full example::

    def index():
        if request.method == 'OPTIONS':
            # custom options handling here
            ...
        return 'Hello World!'
    index.provide_automatic_options = False
    index.methods = ['GET', 'OPTIONS']

    app.add_url_rule('/', index)

.. versionadded:: 0.8
   The `provide_automatic_options` functionality was added.

Command Line Interface
----------------------

.. currentmodule:: flask.cli

.. autoclass:: FlaskGroup
   :members:

.. autoclass:: AppGroup
   :members:

.. autoclass:: ScriptInfo
   :members:

.. autofunction:: load_dotenv

.. autofunction:: with_appcontext

.. autofunction:: pass_script_info

   Marks a function so that an instance of :class:`ScriptInfo` is passed
   as first argument to the click callback.

.. autodata:: run_command

.. autodata:: shell_command
from flask import Flask, request, jsonify
from cosmic_compress import CosmicCompress
import numpy as np

app = Flask(__name__)
compressor = CosmicCompress()

@app.route('/compress', methods=['POST'])
def compress():
    data = request.get_json(force=True).get('data', [])
    algorithm = request.get_json(force=True).get('algorithm', 'zlib')
    data_bytes = np.array(data, dtype=np.uint8).tobytes()
    compressed_data = compressor.compress(data_bytes, algorithm=algorithm)
    return jsonify({"compressed_data": list(compressed_data)})

@app.route('/decompress', methods=['POST'])
def decompress():
    compressed_data = bytes(request.get_json(force=True).get('compressed_data', []))
    algorithm = request.get_json(force=True).get('algorithm', 'zlib')
    decompressed_data = compressor.decompress(compressed_data, algorithm=algorithm)
    return jsonify({"data": list(decompressed_data)})

if __name__ == '__main__':
    app.run(debug=True)
