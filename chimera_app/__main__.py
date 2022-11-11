import argparse
from chimera_app.data import update_data
from chimera_app.compat_tools import install_all_compat_tools
from chimera_app.shortcuts import create_all_shortcuts
from chimera_app.steam_config import apply_all_tweaks
from chimera_app.steam_images import apply_custom_steam_images


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
    group_ex = parser.add_mutually_exclusive_group()
    group_ex.add_argument('-d', '--daemon',
                          action="store_true",
                          help=('Start chimera app web server '
                                '(default behaviour)')
                          )
    group_ex.add_argument('-t', '--tweaks',
                          action="store_true",
                          help='Download and apply all tweaks'
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
    bottle.run(app=server, host='0.0.0.0', port=port)


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
        try:
            update_data(args.force_update)
        except:
            print('Data update failed')

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
