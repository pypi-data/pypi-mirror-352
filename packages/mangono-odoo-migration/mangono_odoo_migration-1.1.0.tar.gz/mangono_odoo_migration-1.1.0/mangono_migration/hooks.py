def create_migration_channel(cr):
    """create if necessary the root.migration_job channel for execution of job launched by migration"""
    cr.execute("SELECT relname FROM pg_class WHERE relkind IN ('r','v') AND relname='queue_job_channel'")
    if cr.fetchall():  # queue_job_channel may not exists if module connector is not installed
        cr.execute("""SELECT COUNT(*) FROM queue_job_channel WHERE NAME = 'root.migration_jobs'""")
        if not cr.fetchall()[0][0]:  # the channel doesn(t exist yet, let's create it
            cr.execute("""INSERT INTO queue_job_channel (name, parent_id) VALUES ('root.migration_jobs', 1)""")
