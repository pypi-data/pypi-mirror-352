{
    "name": "mangono_migration",
    "description": """
mangono migration
=================

This server wide module provides support to run pre- and post-installation scripts
Not installable, only server wide
""",
    "category": "Extra Tools",
    "depends": ["base"],
    "installable": False,
    "auto_install": False,
    "version": "1.0",
    "author": "mangono",
    "license": "AGPL-3",
    "maintainer": "Mangono",
    "data": [],
    "pre_init_hook": "create_migration_channel",
    "post_load": "patch_migration",
}
