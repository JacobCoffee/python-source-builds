================
About the Server
================

The server side of the app is utilizing the `Litestar <https://litestar.dev>`_ framework.
It is an immensely powerful, fast, and easy to use framework that is perfect for the app.

The server is responsible for handling all of the requests to and from the database,
as well as serving the frontend to the user; it utilizes the `Jinja2 <https://jinja.palletsprojects.com/en/3.0.x/>`_
templating engine to do so.

The domain is further broken down into logical components, such as:

* ``core/``: The core logic for this small app, including front end and back end logic as well as templates.

This structure allows for a clear separation of concerns and makes it easy to find and maintain the server's logic.
