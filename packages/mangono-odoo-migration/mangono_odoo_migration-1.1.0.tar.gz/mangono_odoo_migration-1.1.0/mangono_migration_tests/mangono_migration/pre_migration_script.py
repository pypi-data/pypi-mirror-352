from odoo.addons.mangono_migration.mangono_migration import migrate_mangono


@migrate_mangono()
def pre_fake_script(self, has_run):
    pass


@migrate_mangono(run_always=True, allowed_to_fail=True, priority=100)
def pre_fake_script_run_always(self, has_run):
    pass
