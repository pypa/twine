import pkg_resources


def install_commands():
    globals().update(
        (ep.name, ep.load())
        for ep in pkg_resources.iter_entry_points(group="twine.registered_commands")
    )


install_commands()
del install_commands
