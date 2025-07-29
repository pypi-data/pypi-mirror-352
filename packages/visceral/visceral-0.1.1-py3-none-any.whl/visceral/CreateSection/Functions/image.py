import modal
survey_generator = modal.Image.debian_slim(python_version="3.10").pip_install(
    "fastapi",
    "pydantic", "openai", "requests"
)