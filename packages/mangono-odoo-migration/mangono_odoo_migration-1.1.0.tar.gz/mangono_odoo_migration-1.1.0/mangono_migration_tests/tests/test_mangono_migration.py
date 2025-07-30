from odoo.tests import common


class CommonTestMangonoMigration(common.TransactionCase):
    def get_nb_of_run_script(self):
        self.env.cr.execute("""SELECT COUNT(*) FROM mangono_migration where has_run IS TRUE""")
        return self.env.cr.fetchone()[0]


class TestPostMangonoMigration(CommonTestMangonoMigration):
    def test_10_script_run(self):
        # on est obligé d'avoir un step install dans le runbot car mangono_migration ne joue pas en mode test
        # du coup, les scripts pre et post sont exécutés dans le step install, donc on les trouve dans la table
        line_nb = self.get_nb_of_run_script()
        self.assertEqual(line_nb, 3, "3 scripts ont été exécutés après install (les pre+post)")
