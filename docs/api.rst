Twine's Proposed Programmatic API
=================================

Over the years, people have longed for an API so other Python tooling can take
advantage of how Twine interacts with PyPI and other package servers. It's
been a long road to get here, but here's what I'm proposing our API would look
like:

.. code-block:: python

    import os

    from twine import api as twine


    configuration = twine.Settings(
        repository_url='https://upload.pypi.org/legacy/',
        username=os.environ['TWINE_USERNAME'],
        password=os.environ['TWINE_PASSWORD'],
    )

    repository = configuration.create_repository()

    packages = [twine.FileUploader(filename, repository, configuration)
                for filename in os.listdir(path='./dist')]
    twine.upload(packages)


The design comes from the knowledge that there are already a lot of knobs to
tweak in Twine from the command-line and many of the users of the API will
expect similar abilities. The easiest way to manage all that configuration
would appear to be through a single object that understands how to validate
it - the ``Settings`` object. Part of the design of this object would force
users to pass all configuration via keyword arguments so there are no implicit
positional arguments. It would also handle parsing the user's ``~/.pypirc``
and attempting to retrieve the username and password. Finally, it would
provide a short-cut for producing the ``Repository`` object that is already
available as a semi-public API.

Next, we'll want to provide some way of generating the files to be uploaded.
Above we have a notion of a ``FileUploader`` object that would create the
semi-public ``PackageFile`` object and incorporate the configuration and then
handle the interaction between a repository and the package file. An
alternative might be a ``DirectoryUploader`` or a Builder object that produces
a ``PackageFile``. For example, the Builder object might behave like:

.. code-block:: python

    import os

    from twine import api as twine

    configuration = twine.Settings(...)
    repository = configuration.create_repository()

    builder = twine.UploadBuilder(
        ).add_repository(
            repository
        ).add_configuration(
            configuration
        )
    packages = [
        builder.add_filename(filename).finalize()
        for filename in os.listdir(path='./dist')
    ]
    twine.upload(packages)


There's also room here for a Settings builder object if one is desired.
Something like:

.. code-block:: python

    from twine import api as twine

    settings = twine.SettingsBuilder().authenticate_with(
        username=os.environ['TWINE_USERNAME'],
        password=os.environ['TWINE_PASSWORD'],
    ).upload_to(
        'https://upload.pypi.org/legacy'
    ).enable_signatures(
        sign_with='gpg',
        sign_as='my-identity',
    ).finalize()


We're also open to other designs as things move along. I (Ian) plan to split
this work up into the following:

1. Create the ``Settings`` object and replace our argparse parsing/options
   usage in core Twine with it. (Dogfooding our API is important.) The
   settings object:

    * should have a ``from_argparse`` classmethod that can do the right thing

    * should be able to be instantiated from a builder if desirable

    * provides validation of arguments, e.g., passing both ``--sign`` and
      ``--identity``

    * creates other objects that may be necessary for normal operations

2. Next we'll create the object(s) to manage configuration files on disk they
   will be used by the Settings object in lieu of the existing functionality
   and will

    * parse config files

    * discern correct config data to return

    * prints warnings based on configuration, e.g., detecting LEGACY_PYPI

    * retrieves username and password if unset

3. Next we'll work on the Uploader object(s) which will:

    * handle the work of coordinating required objects to perform the upload

    * handle logic of skipping an upload

    * handle logic of checking the status code

    * and will require:

      - Repository

      - PackageFile

      - Settings

At some point we'll need to work on the Repository object as well to remove
the use of ProgressBar without losing that functionality. An API shouldn't
force this on its users.
