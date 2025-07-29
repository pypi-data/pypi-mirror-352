import os
import tempfile
from pathlib import Path
from typing import Literal

import click

from .core.files import AESCipher, ChaChaCipher, FileCryptor, FileFlipper, KeyMan

DEFAULT_ALGO = "chacha"


def get_file_cryptor(algo: Literal["aes", "chacha"] = DEFAULT_ALGO):
    km = KeyMan()
    key = km.load()
    if not key:
        msg = click.style("Set you master password", fg="green")
        passwd = click.prompt(msg, hide_input=True)
        key = km.reset_passwd(passwd.encode("utf8"))
    kls = AESCipher if algo == "aes" else ChaChaCipher
    return FileCryptor(key, kls)


def crypt_opts(fn):
    wfn = (
        click.option("--replace/--no-replace", default=False, help="replace existing files"),
        click.option(
            "-a",
            "--algorithm",
            default=DEFAULT_ALGO,
            help="the encryption algorithm to use: [chacha] / aes",
        ),
        click.argument("files", type=click.Path(exists=True), nargs=-1),
    )
    for f in wfn:
        fn = f(fn)
    return fn


# https://click.palletsprojects.com/en/latest/commands/
@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


def crypt(action: Literal["encrypt", "decrypt"], algo, files):
    fc = get_file_cryptor(algo)
    fn = getattr(fc, action)
    # with click.progressbar(files) as bar:
    for filename in files:
        file_in = Path(filename)
        if not file_in.is_file():
            click.secho(f"not a file: {filename}", fg="yellow")
            continue

        file_out = Path(filename + ".dec")
        if file_out.is_file():
            tmp = tempfile.NamedTemporaryFile(prefix=file_in.stem, dir=file_in.parent)
            file_out = tmp.name

        fn(file_in, file_out)
        os.rename(file_out, file_in)
        click.echo(f"{action}ed in place: {file_in}")


@cli.command()
@crypt_opts
@click.pass_context
def encrypt(ctx, replace, algorithm, files):
    """
    encrypt files
    """
    crypt("encrypt", algorithm, files)


@cli.command()
@crypt_opts
@click.pass_context
def decrypt(ctx, replace, algorithm, files):
    """
    decrypt files
    """
    crypt("decrypt", algorithm, files)


# https://click.palletsprojects.com/en/8.1.x/arguments/
@cli.command()
@click.option("-s", "--size", type=int, default=256, help="how many bytes to flip")
@click.argument("files", type=click.Path(exists=True), nargs=-1)
def flip(size: int, files):
    """
    flip leading bytes of files
    """
    ff = FileFlipper(size)
    for filename in files:
        click.echo(f"flipping: {filename}")
        ff.flip(filename)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
