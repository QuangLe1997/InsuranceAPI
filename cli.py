import typer
import uvicorn

from app import app
from configs import settings

cli = typer.Typer(name="project_name API")


@cli.command()
def run(
    port: int = settings.server.port,
    host: str = settings.server.host,
    log_level: str = settings.server.log_level,
    reload: bool = settings.server.reload,
):  # pragma: no cover
    """Run the API server."""
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )
