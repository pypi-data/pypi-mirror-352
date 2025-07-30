from odoo.addons.mangono_migration.mangono_migration import migrate_mangono


@migrate_mangono()
def post_fake_script(self, has_run):
    pass
