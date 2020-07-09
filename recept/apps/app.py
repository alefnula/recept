import sys

import sh


def app(name, *args, _out=sys.stdout, _err=sys.stderr, _tee=True, **kwargs):
    try:
        return sh.Command(name).bake(
            *args, _out=_out, _err=_err, _tee=_tee, **kwargs
        )
    except sh.CommandNotFound:
        return sh.Command(sys.executable).bake(
            "-c",
            (
                f"import sys; import click; click.secho('Command `{name}` "
                f"not found', fg='red'); sys.exit(1)"
            ),
        )
