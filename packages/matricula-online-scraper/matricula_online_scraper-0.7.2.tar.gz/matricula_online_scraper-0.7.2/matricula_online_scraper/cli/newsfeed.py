"""`newsfeed` command group for interacting with Matricula Online's newsfeed at https://data.matricula-online.eu/en/nachrichten/."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor

from matricula_online_scraper.logging_config import get_logger
from matricula_online_scraper.spiders.newsfeed_spider import NewsfeedSpider

from ..utils.file_format import FileFormat

logger = get_logger(__name__)

app = typer.Typer()


@app.command()
def fetch(
    outfile: Annotated[
        Path,
        typer.Option(
            "-o",
            "--outfile",
            help=(
                f"File to which the data is written (formats: {', '.join(FileFormat)})."
                " Use '-' to write to stdout."
            ),
            exists=False,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            allow_dash=True,  # use '-' to write to stdout
        ),
    ] = Path("matricula_news.jsonl"),
    # options
    last_n_days: Annotated[
        Optional[int],
        typer.Option(
            "--days", help="Scrape news from the last n days (including today).", min=1
        ),
    ] = None,
    limit: Annotated[
        Optional[int],
        typer.Option(
            help=(
                "Limit the number of max news articles to scrape"
                "(note that this is a upper bound, it might be less depending on other parameters)."
            ),
            min=1,
        ),
    ] = 100,
):
    """Download Matricula Online's newsfeed.

    Matricula has a minimal newsfeed where they announce new parishes, new registers, and\
 other changes: https://data.matricula-online.eu/en/nachrichten/.\
 This command will download the entire newsfeed or a limited number of news articles.
    """
    cmd_logger = logger.getChild(fetch.__name__)

    use_stdout = outfile == Path("-")
    feed: dict[str, dict[str, str]]

    if use_stdout:
        feed = {"stdout:": {"format": "jsonlines"}}
    else:
        try:
            format = FileFormat(outfile.suffix[1:])
        except Exception as e:
            raise typer.BadParameter(
                f"Invalid file format: '{outfile.suffix[1:]}'. Allowed file formats are: {', '.join(FileFormat)}",
                param_hint="outfile",
            )

        # seems like this is not handled by typer even if suggested through `exists=False`
        # maybe only `exists=True` has meaning and is checked
        if outfile.exists():
            raise typer.BadParameter(
                f"A file with the same path as the outfile already exists: {outfile.resolve()}."
                " Will not overwrite it. Delete the file or choose a different path. Aborting.",
                param_hint="outfile",
            )

        feed = {str(outfile): {"format": format.to_scrapy()}}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
        console=Console(stderr=True),
    ) as progress:
        progress.add_task(
            "Scraping...",
            total=limit,  # use limit as a rough estimate
        )

        try:
            runner = CrawlerRunner(
                settings={
                    "FEEDS": feed,
                    # NOTE: Force a non-asyncio reactor (https://docs.scrapy.org/en/2.13/topics/asyncio.html#switching-to-a-non-asyncio-reactor).
                    # Scrapy 3.12.0 made the asyncio reactor the default one (https://docs.scrapy.org/en/2.13/news.html#scrapy-2-13-0-2025-05-08).
                    # which causes the process to run indefinitely and never finish,
                    # see https://github.com/lsg551/matricula-online-scraper/issues/100
                    # For now, use a sync reactor to avoid this issue.
                    "TWISTED_REACTOR": None,
                }
            )
            crawler = runner.create_crawler(NewsfeedSpider)
            deferred = runner.crawl(crawler, limit=limit, last_n_days=last_n_days)
            deferred.addBoth(lambda _: reactor.stop())  # type: ignore
            reactor.run()  # type: ignore  # blocks until the crawling is finished

        except Exception as exception:
            cmd_logger.exception(
                "An error occurred while scraping Matricula Online's newsfeed."
            )
            raise typer.Exit(code=1) from exception

    cmd_logger.info(
        f"Done! Successfully scraped the newsfeed."
        + (f" The output was saved to: {outfile.resolve()}" if not use_stdout else "")
    )
