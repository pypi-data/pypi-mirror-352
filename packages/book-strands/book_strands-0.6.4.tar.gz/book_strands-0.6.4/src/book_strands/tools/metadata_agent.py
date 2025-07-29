import logging

from strands import Agent, tool
from strands.types.models import Model
from strands_tools import http_request  # type: ignore

from book_strands.constants import BEDROCK_MODEL
from book_strands.tools import read_ebook_metadata, write_ebook_metadata
from book_strands.utils import calculate_bedrock_cost

WAIT_TIME = 1  # seconds to wait between book downloads and retries

log = logging.getLogger(__name__)


@tool
def metadata_agent(
    input_file: str,
):
    """
    Metadata agent to ensure the provided ebook files are tagged with the correct metadata.

    Args:
        input_file (str): The path to an input ebook file.
    """
    system_prompt = """
        You are in charge of making sure ebooks are tagged with the correct metadata, you will be provided with a list of input file paths.
        Use the tools available to gather the information required and then write the updated metadata to the files
        The book title should be purely the title of the book, without any extra information such as series or series index.
        Ensure that if the book is a part of a series, that the series name is correct.
        The series name should not contain the word 'series'. If there is no series name, leave it blank.
        Note that all series indexes should be in the format 1.0, 2.0, 2.5 etc based on common practice.
        For author names, use "firstname lastname" ordering.
        For the description of the book, it should be 100-400 words, use a style that would typically be found on the back cover of a book and in html format. If there is already a description that fits this criteria, keep it the same.
        """
    model: Model

    query = f"The input file to process is: {input_file}"

    model = BEDROCK_MODEL
    a = Agent(
        system_prompt=system_prompt,
        model=model,
        tools=[read_ebook_metadata, write_ebook_metadata, http_request],
    )

    response = a(query)
    log.info(f"Accumulated token usage: {response.metrics.accumulated_usage}")

    calculate_bedrock_cost(
        response.metrics.accumulated_usage,
        model,
    )

    return response
