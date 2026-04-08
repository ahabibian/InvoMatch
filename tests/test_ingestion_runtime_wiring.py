from invomatch.main import create_app


def test_app_exposes_ingestion_run_runtime_adapter():
    app = create_app()

    adapter = getattr(app.state, "ingestion_run_runtime_adapter", None)

    assert adapter is not None