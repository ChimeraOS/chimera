import argparse
from chimera_app.data import update_data
from chimera_app.compat_tools import install_all_compat_tools
from chimera_app.shortcuts import create_all_shortcuts
from chimera_app.steam_config import apply_all_tweaks
from chimera_app.steam_images import apply_custom_steam_images
from chimera_app.splash_screen import SplashScreen


def setup_argparse():
    parser = argparse.ArgumentParser(
        description='Chimera app for managing ChimeraOS')

    parser.add_argument('-u', '--update',
                        action="store_true",
                        help='Update data from repository'
                        )
    parser.add_argument('-f', '--force-update',
                        action="store_true",
                        help='Force update even if already updated'
                        )
    parser.add_argument('-p', '--port',
                        action="store",
                        type=int,
                        default=8844,
                        help=('Port to use for web server (default: 8844)')
                        )
    parser.add_argument('-l', '--splash',
                        action="store_true",
                        help='Show splash screen when downloading data'
                        )
    group_ex = parser.add_mutually_exclusive_group()
    group_ex.add_argument('-d', '--daemon',
                          action="store_true",
                          help=('Start chimera app web server '
                                '(default behaviour)')
                          )
    group_ex.add_argument('-t', '--tweaks',
                          action="store_true",
                          help='Apply all tweaks; equivalent to --compat --config --shortcuts'
                          )
    group_ex.add_argument('-c', '--compat',
                          action="store_true",
                          help='Generate stubs for compatibility tools'
                          )
    group_ex.add_argument('-s', '--shortcuts',
                          action="store_true",
                          help='Read shortcuts files and add them to Steam'
                          )
    group_ex.add_argument('-g', '--config',
                          action="store_true",
                          help=('Apply configuration for Steam games')
                          )
    group_ex.add_argument('-i', '--images',
                          action="store_true",
                          help=('Apply custom artwork for Steam games')
                          )

    return parser.parse_args()


def run_server(port):
    import os
    import shutil
    import bottle
    from chimera_app.server import server
    from chimera_app.config import RESOURCE_DIR, FTP_SERVER, UPLOADS_DIR

    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":0.0"

    if os.path.exists(UPLOADS_DIR):
        shutil.rmtree(UPLOADS_DIR)

    os.chdir(RESOURCE_DIR)
    FTP_SERVER.run()

    # Server   | url encoding | large file download (3.6 GB) | starts | multi-threaded | installed size
    # default  | y            | y (32s)                      | y      | n              | 0 MB
    # waitress | y            | y (32s)                      | y      | y              | 1 MB
    # eventlet | y            | y (32s)                      | y      | y              | 17 MB
    # paste    | n            | y (32s)                      | y      | y              | ?
    # tornado  | y            | n                            | y      | y              | ?
    # gunicorn | ?            | n                            | y      | y              | ?
    # gevent   | ?            | ?                            | n      | y              | 10 MB
    # twisted  | ?            | ?                            | n      | y              | ?
    # cherrypy | ?            | ?                            | n      | y              | ?

    bottle.run(app=server, host='0.0.0.0', port=port, server='waitress')


def main():
    args = setup_argparse()
    if (args.daemon or
            not ((args.daemon
                  or args.compat
                  or args.shortcuts
                  or args.images
                  or args.config
                  or args.tweaks
                  or args.update))):
        run_server(args.port)

    if args.update:
        splash = None
        if args.splash:
            splash = SplashScreen()
            splash.launch()
        try:
            update_data(args.force_update)
        except:
            print('Data update failed')
        finally:
            if args.splash and splash:
                splash.kill()

    if args.compat:
        try:
            install_all_compat_tools()
        except:
            print('Compatibility tools stub generation failed')

    if args.shortcuts:
        try:
            create_all_shortcuts()
        except:
            print('Shortcuts creation failed')

    if args.images:
        try:
            apply_custom_steam_images()
        except:
            print('Applying custom Steam images failed')

    if args.config:
        try:
            apply_all_tweaks()
        except:
            print('Failed to apply tweaks')

    if args.tweaks:
        try:
            install_all_compat_tools()
        except:
            print('Compatibility tools stub generation failed')

        try:
            apply_all_tweaks()
        except:
            print('Failed to apply tweaks')

        try:
            create_all_shortcuts()
        except:
            print('Shortcuts creation failed')


if __name__ == '__main__':
    main()
