# ruff: noqa: E402
import inspect
import logging
import os
import sys
from inspect import getmembers, isfunction
from operator import attrgetter
from typing import Any, Union, Dict

from typing_extensions import Self

import odoo

MAJOR = odoo.release.version_info[0]
MIGRATION_DIR = [
    "ndp_migration",
    "mangono_migration",  # Name of the directory where the script must be located
]
from odoo import (
    SUPERUSER_ID,
    api,
    fields,
    registry,  # pylint: disable=ungrouped-imports; pylint: disable=ungrouped-imports
)

# from odoo.addons.queue_job.models import with_delay
from odoo.conf import server_wide_modules  # pylint: disable=ungrouped-imports
from odoo.modules.migration import MigrationManager  # pylint: disable=ungrouped-imports
from odoo.modules.module import (
    get_module_path,
    get_modules,  # pylint: disable=ungrouped-imports; pylint: disable=ungrouped-imports
)
from odoo.tools import config  # pylint: disable=ungrouped-imports

_logger = logging.getLogger(__name__)


def _is_valid_migration_file_for_stage(stage: str, name: str) -> bool:
    """
    :param name: filename without path
    :return: True is filename is in the form : stage_XXXX.py (case insensitive)
    """
    _, ext = os.path.splitext(name)
    return ext.lower() == ".py" and name.lower().startswith((stage + "_").lower())


def table_exists_in_db(cr, tablename: str) -> bool:
    """
    :param cr: a cursor object
    :param tablename: name of the table (stock_move)
    :return: True if the table exists in database, False otherwise
    """
    cr.execute(
        """
    SELECT EXISTS (
        SELECT FROM pg_catalog.pg_class c
        JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE  n.nspname = 'public'
        AND    c.relname = %s)
        """,
        (tablename,),
    )
    return cr.fetchone()[0]


def column_exists_in_db(cr, table_name: str, column_name: str) -> bool:
    """
    :param cr: cursor object
    :param table_name: 'stock_move' for exmaple
    :param column_name: 'location_id' for example
    :return: True if column exists in table, false if columns or table doesn't exist
    """
    if table_exists_in_db(cr, table_name):
        cr.execute(
            """
        SELECT EXISTS(SELECT *
          FROM   INFORMATION_SCHEMA.COLUMNS
          WHERE  TABLE_NAME = %s
                 AND COLUMN_NAME = %s);
        """,
            (table_name, column_name),
        )
        return cr.fetchone()[0]
    return False


def mangono_migrate_module(self, pkg, stage: str):
    # this function is called from loading.py, self gives access to cr and graph
    if pkg.name not in ["base", "mangono_migration"]:
        run_migration_script(self, stage, pkg)
    result = MigrationManager.origin_migrate_module(self, pkg, stage)
    return result


# ruff: noqa: PERF203
def get_module_filetree(module_path):
    res = {}
    for directory in MIGRATION_DIR:
        try:
            res.update(
                {f: os.path.join(module_path, directory, f) for f in os.listdir(os.path.join(module_path, directory))}
            )
        except FileNotFoundError:
            continue
    return res


def just_after_base(self, stage: str, pkg) -> None:
    """
    :param stage: the migration stage
    :param pkg: a Package object
    :return: if the package is the first one after base, looks for scripts with stage 'afterbase' in all migration dirs
    During an "update base", this will execute these migration script beginning with afterbase_ ...
    before any other community, common, ... modules are loaded (only base is loaded)
    """
    list_pkg = list(pkg.graph)
    if stage == "pre" and list_pkg[0].name == "base" and list_pkg[1] == pkg:  # we are the first package after base
        mods = get_modules()
        for mod in mods:
            self.cr.execute("""select state from ir_module_module where name = %s""", (mod,))
            state = self.cr.fetchone()
            if state and state[0] in [
                "installed",
                "to upgrade",
            ]:  # we check only installed modules
                module_path = get_module_path(mod)
                file_tree = get_module_filetree(module_path)
                if file_tree:
                    run_scripts_of_module(self, file_tree, "afterbase")


def run_migration_script(self, stage: str, pkg) -> None:
    if MAJOR >= 18:
        _registry = odoo.modules.registry.Registry(self.cr.dbname)
    else:
        _registry = registry(self.cr.dbname)
    just_after_base(self, stage, pkg)
    module_path = get_module_path(pkg.name)
    file_tree = get_module_filetree(module_path)
    if file_tree:
        if stage == "pre":
            _registry.setup_models(self.cr)
        _logger.debug("=== found mangono migration directory in %s for stage %s", pkg.name, stage)
        run_scripts_of_module(self, file_tree, stage)


def run_scripts_of_module(self, file_tree, stage: str) -> None:
    """run all script in this module matching stage (python file beginning with stage_)"""
    for filename in file_tree.keys():
        # python file must be directly under mangono_migration directory
        if _is_valid_migration_file_for_stage(stage, filename):
            file_without_ext = os.path.splitext(filename)[0]
            file_path = file_tree[filename]
            # load and execute _pre_migrate()
            py_mod = load_module_from_file(file_without_ext, file_path)
            # we recognize the python function to run because the @mangono_migrate wrapper adds an
            # 'is_mangono_migration' attribute to it, <migrate_mangono> is imported by the import, must not be run
            scripts = [
                f[1]
                for f in getmembers(py_mod, isfunction)
                if f[0] != "migrate_mangono" and hasattr(f[1], "is_mangono_migration")
            ]
            for script in sorted(scripts, key=attrgetter("priority")):
                script(self.cr)


def patch_migration() -> None:
    if "mangono_migration" in server_wide_modules and not config["test_enable"]:
        MigrationManager.origin_migrate_module = (
            hasattr(MigrationManager, "origin_migrate_module")
            and MigrationManager.origin_migrate_module
            or MigrationManager.migrate_module
        )
        MigrationManager.migrate_module = mangono_migrate_module
        MigrationManager._logger = hasattr(MigrationManager, "_logger") and MigrationManager._logger or _logger
        _logger.info("module mangono_migration enabled")


class MangonoMigration:  # pylint: disable=useless-object-inheritance
    """
    Provide service for pre-installation and post-installation scripts
    see <documentation.adoc> for detailed documentation
    """

    _description = "Automation scripting system for pre and post installation scripting"

    def __init__(
        self,
        ticket: str,
        md5: str = None,
        has_run: bool = False,
        create_date=None,
        write_date=None,
        log: str = None,
    ):
        """prepare the table for script execution recording if necessary"""
        super().__init__()
        self.ticket = ticket
        self.md5 = md5 or ""
        self.log = log or ""
        self.has_run = has_run
        self.create_date = create_date or fields.datetime.now()
        self.write_date = write_date or fields.datetime.now()

    @classmethod
    def create_table_if_needed(cls, cr) -> None:
        cr.execute("ALTER TABLE IF EXISTS ndp_migration RENAME TO mangono_migration")
        cr.execute(
            """CREATE TABLE IF NOT EXISTS mangono_migration ( id serial  NOT NULL
            CONSTRAINT
            mangono_migration_pkey
            PRIMARY
            KEY,
            create_date
            timestamp,
            write_date
            timestamp,
            ticket
            varchar
            NOT
            NULL
            CONSTRAINT
            mangono_migration_unique_ticket
            UNIQUE,
            md5
            varchar,
            has_run bool,
            log varchar
            );"""
        )

    def set_run(self, cr) -> None:
        """record the fact that this script has been run"""
        md5 = ""
        self.create_table_if_needed(cr)
        date_str = fields.Datetime.to_string(fields.datetime.now())
        _logger.debug("script %s has run succesfully", self.ticket)
        cr.execute(
            """UPDATE mangono_migration SET has_run = TRUE, md5 = %s, write_date = %s, log = %s
                      WHERE ticket = %s""",
            (md5, date_str, self.log + "\n" + date_str + " has_run", self.ticket),
        )

    @classmethod
    def get_or_create(cls, cr, ident: str) -> Self:
        """return MangonoMigration object from existing record of database, create it in base if it doesn't exists"""

        def get_value(ident: str) -> Dict[str, Any]:
            # odoo himself use string formating to insert table name into query
            cls.create_table_if_needed(cr)
            cr.execute("""SELECT * FROM mangono_migration WHERE ticket = %s""", (ident,))
            return cr.dictfetchone()

        res = get_value(ident)
        if not res:
            cr.execute(
                """INSERT INTO mangono_migration
                        (ticket, has_run, create_date, write_date)
                        VALUES (%s, FALSE, %s, %s)""",
                (ident, fields.datetime.now(), fields.datetime.now()),
            )
            res = get_value(ident)
        res.pop("id")
        return MangonoMigration(**res)

    def log_error(self, cr, msg: str) -> None:
        self.create_table_if_needed(cr)
        cr.execute(
            """UPDATE mangono_migration SET log = %s WHERE ticket = %s""",
            (
                f"{self.log}\n{fields.Datetime.to_string(fields.datetime.now())} : {msg}",
                self.ticket,
            ),
        )


class ProxySelf:  # pylint: disable=useless-object-inheritance
    """provide a factice object with env attribute to be able to use self.env, self.env.cr in script
    self.has_run is true when the script has already been run (for run_always script)
    """

    def __init__(self, cr, has_run: bool = False):
        super().__init__()
        env = api.Environment(cr, SUPERUSER_ID, {})
        self.env = env
        self.cr = cr
        self.uid = SUPERUSER_ID
        self.context = self.env.context
        self.has_run = has_run


def migrate_mangono(
    run_always: Union[bool, callable] = False, priority: int = 9999, allowed_to_fail: bool = False
) -> callable:
    def _migrate_mangono(method: callable) -> callable:
        def migrate_wrapper(cr, *args, **kwargs):
            """
            Decorator to use for script method
            after succesfull running of the script, it is written in database
            When a pre_xxx script fails, the base is rollbacked, the script is not written as runned
            and the instalation is broken (further script will not be runned)
            When a post_xxx failed, the installation is stopped, all changes from post_xxx are rollbacked. Changes from
            pre_xxx scripts are committed in database
            """
            filename = inspect.getfile(method)
            module = filename.split("/")[-3]
            ident = "{module}.{method}".format(module=module or "", method=method.__name__)
            script = MangonoMigration.get_or_create(cr, ident)
            try:
                if run_always or not script.has_run:
                    if allowed_to_fail:
                        with cr.savepoint():  # when failed, changes are rollbacked
                            _logger.info(
                                "mangono_migration executing %s allowed to fail",
                                method.__name__,
                            )
                            _call_method(method, cr, script)
                    else:
                        _logger.info(
                            "mangono_migration executing %s not allowed to fail",
                            method.__name__,
                        )
                        _call_method(method, cr, script)
            # pylint: disable=broad-except
            except Exception as err:
                _logger.error("Error during migration script <%s>: %s", ident, err)
                script.log_error(cr, f"{err}")
                if not allowed_to_fail:
                    # note that the script allowed_to_fail which fails will have an error log, but not set to run
                    raise err
            else:
                if run_always or not script.has_run:
                    script.set_run(cr)

        migrate_wrapper.run_always = run_always
        migrate_wrapper.priority = priority
        migrate_wrapper.allowed_to_fail = allowed_to_fail
        migrate_wrapper.is_mangono_migration = True  # to identify script needing to be run
        return migrate_wrapper

    if callable(run_always):  # cas où on décore avec @migrate_mangono sans parenthèse
        return _migrate_mangono(run_always)
    return _migrate_mangono


def _call_method(method: callable, cr, script: MangonoMigration) -> None:
    parameters = inspect.signature(method).parameters
    if len(parameters) > 2:
        script.log_error(cr, f"{method.__name__} wrong signature (too many arguments)")
    elif len(parameters) == 2 and parameters.get("has_run"):
        # old signature with parameter has_run
        method(ProxySelf(cr, script.has_run), script.has_run)
    else:  # cas où la méthode ne prend pas has_run en paramètre
        method(ProxySelf(cr, script.has_run))


##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
# Extract from spack
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
##############################################################################
def load_module_from_file(module_name, module_path):
    """Loads a python module from the path of the corresponding file.
    Args:
        module_name (str): namespace where the python module will be loaded,
            e.g. ``foo.bar``
        module_path (str): path of the python file containing the module
    Returns:
        A valid module object
    Raises:
        ImportError: when the module can't be loaded
        FileNotFoundError: when module_path doesn't exist
    """
    if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        import importlib.util

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    elif sys.version_info[0] == 3 and sys.version_info[1] < 5:
        import importlib.machinery

        loader = importlib.machinery.SourceFileLoader(module_name, module_path)
        module = loader.load_module()

    return module
