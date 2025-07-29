from pathlib import Path
import requests
import sys

source = "https://raw.githubusercontent.com/curiouswalk/mscene/main"


def modsync(module):
    path = Path(__file__).parent
    release = path / module.upper()
    response = requests.get(f"{source}/{module}/RELEASE")

    if response.ok:
        content = response.content

        if not release.exists():
            txt = response.text.splitlines()
            names = [l[0] for i in txt if (l := i.split())]
        elif release.read_bytes() != content:
            txt = [response.text.splitlines(), release.read_text().splitlines()]
            rel = [{l[0]: l[1] for i in t if (l := i.split())} for t in txt]
            names = [i for i in rel[0] if rel[0][i] != rel[1].get(i)]
        else:
            names = None

        if names:
            error = None

            for name in names:
                resp = requests.get(f"{source}/{module}/{name}.py")
                if resp.ok:
                    filename = path / f"{name}.py"
                    filename.write_bytes(resp.content)
                else:
                    error = True

            if error is None:
                release.write_bytes(content)


def manchk(name):
    if name == "manim":
        status = True
    elif name.startswith("manim=="):
        pkg = name.replace("==", "/")
        status = requests.head(f"https://pypi.org/pypi/{pkg}/json").ok
    else:
        status = False
    return status


def main(args=None):

    if isinstance(args, str):
        args = args.split()
        pfx = "%mscene"
    else:
        args = sys.argv[1:]
        pfx = "mscene"

    args = list(set(args)) if args else None

    if "-h" in args or args is None:
        usage = f"""Usage: {pfx} <command>

Commands:
    manim                Install Manim with LaTeX
    -l manim             Install Manim without LaTeX
    manim==<ver>         Install specific Manim version
    plugins              Add or update plugins
    <filename>           Download source"""

        print(usage)

    else:
        plugins = None
        manver = None
        error = None
        lite = False

        for arg in args:
            if manchk(arg):
                if not manver:
                    manver = arg
                else:
                    error = "Error: invalid command"
                    break
            elif arg == "-l":
                lite = True
            elif arg == "plugins":
                plugins = True
            elif "." in arg[-6:-2]:
                resp = requests.get(f"{source}/source/{arg}")
                if resp.ok:
                    name = arg.split("/")[-1] if "/" in arg else arg
                    Path(name).write_bytes(resp.content)
                else:
                    error = f"Error: '{arg}' not found"
                    break
            else:
                error = "Error: invalid command"
                break

        if not error and lite and not manver:
            error = "Error: invalid command"

        if error is None:
            if plugins:
                modsync("plugins")
            if manver:
                modsync("colab")

                try:
                    from mscene.colab import setup
                except Exception:
                    print("Error: something went wrong")
                else:
                    setup(manver, lite)

            else:
                print("Mscene — Science Animation")

        else:
            print(f"{error}\nRun '{pfx} -h' to view usage")
