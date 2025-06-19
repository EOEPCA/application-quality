from django.db import migrations

CREATE_VIEWS = """
  CREATE OR REPLACE VIEW executions AS
  SELECT backend_pipeline.name AS pipeline_name,
    backend_pipelinerun.*,
    (backend_pipelinerun.usage_report->>'total_tasks')::int AS total_tasks,
    (backend_pipelinerun.usage_report->>'total_cpu_hours')::float AS total_cpu_hours,
    (backend_pipelinerun.usage_report->>'elapsed_hours')::float AS elapsed_hours,
    (backend_pipelinerun.usage_report->>'total_disk_megabytes')::float AS total_disk_megabytes,
    (backend_pipelinerun.usage_report->>'total_ram_megabyte_hours')::float AS total_ram_megabyte_hours
  FROM backend_pipeline,
    backend_pipelinerun
  WHERE backend_pipelinerun.pipeline_id = backend_pipeline.id
    AND backend_pipelinerun.user = SESSION_USER;

  CREATE OR REPLACE VIEW executions_admin AS
  SELECT backend_pipeline.name AS pipeline_name,
    backend_pipelinerun.*,
    (backend_pipelinerun.usage_report->>'total_tasks')::int AS total_tasks,
    (backend_pipelinerun.usage_report->>'total_cpu_hours')::float AS total_cpu_hours,
    (backend_pipelinerun.usage_report->>'elapsed_hours')::float AS elapsed_hours,
    (backend_pipelinerun.usage_report->>'total_disk_megabytes')::float AS total_disk_megabytes,
    (backend_pipelinerun.usage_report->>'total_ram_megabyte_hours')::float AS total_ram_megabyte_hours
  FROM backend_pipeline,
    backend_pipelinerun
  WHERE backend_pipelinerun.pipeline_id = backend_pipeline.id;

  CREATE OR REPLACE VIEW reports AS
  SELECT backend_jobreport.*,
    backend_pipelinerun.started_by_id
  FROM backend_jobreport
    INNER JOIN backend_pipelinerun ON backend_jobreport.run_id = backend_pipelinerun.id
  WHERE backend_pipelinerun.user = SESSION_USER;

  CREATE OR REPLACE VIEW reports_admin AS
  SELECT backend_jobreport.*,
    backend_pipelinerun.started_by_id
  FROM backend_jobreport
    INNER JOIN backend_pipelinerun ON backend_jobreport.run_id = backend_pipelinerun.id;
"""

DROP_VIEWS = """
  DROP VIEW IF EXISTS reports_admin;
  DROP VIEW IF EXISTS reports;
  DROP VIEW IF EXISTS executions_admin;
  DROP VIEW IF EXISTS executions;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0003_pipeline_default_inputs"),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE_VIEWS, reverse_sql=DROP_VIEWS),
    ]
