"""Run fdroidserver with a custom public root URL before generating signatures."""
import sys


def configure_repo(address):
    from fdroidserver import common

    # fdroidserver 2.4.5 validates config URLs as ending in /repo. Load the
    # conventional staging configuration, then set the public URL in memory.
    # All indexes, signatures, HTML, and QR codes are generated after this.
    config = common.read_config()
    config["repo_url"] = address
    return config


if __name__ == "__main__":
    from fdroidserver import update

    configure_repo(sys.argv[1])
    # Match fdroid's CLI dispatch, including the name used in status output.
    sys.argv = ["fdroid update"]
    update.main()
