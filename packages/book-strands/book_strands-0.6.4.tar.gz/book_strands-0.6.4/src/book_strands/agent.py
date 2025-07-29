import logging

from strands import Agent
from strands_tools import http_request  # type: ignore

from book_strands.constants import BEDROCK_MODEL, BOOK_HANDLING_PROMPT
from book_strands.tools.filesystem import file_delete
from book_strands.utils import calculate_bedrock_cost  # type: ignore

from .tools import (
    download_ebook,
    file_move,
    metadata_agent,
    path_list,
)

log = logging.getLogger(__name__)


def agent(
    output_path: str,
    output_format: str,
    query: str,
    enable_downloads: bool = True,
    enable_deletions: bool = True,
    enable_renaming: bool = True,
):
    system_prompt = f"""
You are a book downloader, renamer, and metadata fixer agent.
Your task is to download ebooks, rename them according to the provided format ({output_format}), and fix their metadata.
The output ebooks should be saved in the specified output path ({output_path}).
The output format should follow regular language conventions (capital letters, spaces, punctuation, etc) except where they would not be supported on a filesystem.

Check the output directory for the following:
- Any naming conventions to follow
- If the requested books have already been downloaded (then do not download them again, just process the books that are not downloaded)
- Unless you are asked otherwise, only call the metadata_agent on newly downloaded books

From the input query, extract the list of book titles and authors to download. This may involve using the http_request tool to look up required information from free sources that do not need authentication.
If the query does not contain anything that can be resolved to a book title and/or author, return an error message indicating that no books were found.

If there are multiple books to download, use the download_ebook tool to download them all in a single request.
The file extensions of ebooks do not matter, use the extensions as provided by the tools. When downloading a book you may be returned a different format ebook, this is acceptable.

When you are finshed, print a summary of what books were downloaded, what ones already existed and their file paths.

{BOOK_HANDLING_PROMPT}
"""

    model = BEDROCK_MODEL
    tools = [
        metadata_agent,
        path_list,
        http_request,
    ]

    if enable_downloads:
        tools.append(download_ebook)
    if enable_deletions:
        tools.append(file_delete)
    if enable_renaming:
        tools.append(file_move)

    a = Agent(system_prompt=system_prompt, model=model, tools=tools)

    response = a(query)
    log.info(f"Accumulated token usage: {response.metrics.accumulated_usage}")

    total_cost = calculate_bedrock_cost(
        response.metrics.accumulated_usage,
        model,
    )
    log.info(f"Total cost: US${total_cost:.3f}")

    return response
