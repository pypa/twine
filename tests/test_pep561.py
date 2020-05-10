import subprocess


def test_no_missing_import(tmpdir):
    src = tmpdir / "example.py"
    src.write("""import twine""")

    tmpdir.chdir()
    subprocess.run(["mypy", "--strict", src], check=True)
