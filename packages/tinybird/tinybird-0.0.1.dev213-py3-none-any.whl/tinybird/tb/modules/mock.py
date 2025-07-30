import glob
from pathlib import Path
from typing import Any, Dict, List

import click

from tinybird.prompts import mock_prompt
from tinybird.tb.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import coro, push_data
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import persist_fixture, persist_fixture_sql
from tinybird.tb.modules.exceptions import CLIMockException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml
from tinybird.tb.modules.project import Project


@cli.command()
@click.argument("datasource", type=str)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@click.option(
    "--prompt",
    type=str,
    default="",
    help="Extra context to use for data generation",
)
@click.option(
    "--format",
    "format_",
    type=click.Choice(["ndjson", "csv"], case_sensitive=False),
    default="ndjson",
    help="Format of the fixture to create",
)
@click.pass_context
@coro
async def mock(ctx: click.Context, datasource: str, rows: int, prompt: str, format_: str) -> None:
    """Generate sample data for a data source.

    Args:
        datasource: Path to the datasource file to load sample data into
        rows: Number of events to send
        prompt: Extra context to use for data generation
        skip: Skip following up on the generated data
    """

    try:
        tb_client: TinyB = ctx.ensure_object(dict)["client"]
        project: Project = ctx.ensure_object(dict)["project"]
        ctx_config = ctx.ensure_object(dict)["config"]
        env = ctx.ensure_object(dict)["env"]
        datasource_path = Path(datasource)
        datasource_name = datasource
        folder = project.folder
        click.echo(FeedbackManager.highlight(message=f"\n» Creating fixture for {datasource_name}..."))
        if datasource_path.suffix == ".datasource":
            datasource_name = datasource_path.stem
        else:
            datasource_from_glob = glob.glob(f"{folder}/**/{datasource}.datasource")
            if datasource_from_glob:
                datasource_path = Path(datasource_from_glob[0])

        if not datasource_path.exists():
            raise Exception(f"Datasource '{datasource_path.stem}' not found")

        datasource_content = datasource_path.read_text()
        config = CLIConfig.get_project_config()
        user_token = ctx_config.get("user_token")

        if not user_token:
            raise Exception("This action requires authentication. Run 'tb login' first.")

        data = await create_mock_data(
            datasource_name,
            datasource_content,
            rows,
            prompt,
            config,
            ctx_config,
            user_token,
            tb_client,
            format_,
            folder,
        )

        fixture_path = persist_fixture(datasource_name, data, folder, format=format_)
        click.echo(FeedbackManager.info(message=f"✓ /fixtures/{datasource_name}.{format_} created"))
        if env == "cloud":
            await append_fixture(tb_client, datasource_name, str(fixture_path))

        click.echo(FeedbackManager.success(message=f"✓ Sample data for {datasource_name} created with {rows} rows"))

    except Exception as e:
        raise CLIMockException(FeedbackManager.error(message=str(e)))


async def append_fixture(
    tb_client: TinyB,
    datasource_name: str,
    url: str,
):
    await push_data(
        tb_client,
        datasource_name,
        url,
        mode="append",
        concurrency=1,
        silent=True,
    )


async def create_mock_data(
    datasource_name: str,
    datasource_content: str,
    rows: int,
    prompt: str,
    config: CLIConfig,
    ctx_config: Dict[str, Any],
    user_token: str,
    tb_client: TinyB,
    format_: str,
    folder: str,
) -> List[Dict[str, Any]]:
    user_client = config.get_client(token=ctx_config.get("token"), host=ctx_config.get("host"))
    llm = LLM(user_token=user_token, host=user_client.host)
    prompt = f"<datasource_schema>{datasource_content}</datasource_schema>\n<user_input>{prompt}</user_input>"
    sql = ""
    attempts = 0
    data = []
    error = ""
    sql_path = None
    while True:
        try:
            response = llm.ask(system_prompt=mock_prompt(rows, error), prompt=prompt)
            sql = extract_xml(response, "sql")
            sql_path = persist_fixture_sql(datasource_name, sql, folder)
            sql_format = "JSON" if format_ == "ndjson" else "CSV"
            result = await tb_client.query(f"SELECT * FROM ({sql}) LIMIT {rows} FORMAT {sql_format}")
            if sql_format == "JSON":
                data = result.get("data", [])[:rows]
                error_response = result.get("error", None)
                if error_response:
                    raise Exception(error_response)
            else:
                data = result
            break
        except Exception as e:
            error = str(e)
            attempts += 1
            if attempts > 5:
                raise Exception(f"Failed to generate a valid solution. Check {str(sql_path)} and try again.")
            else:
                continue
    return data
