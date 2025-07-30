"""Kozmograph toolkits."""

from typing import List

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import ConfigDict, Field

from langchain_kozmograph.graphs.kozmograph import Kozmograph
from langchain_kozmograph.tools import (
    QueryKozmographTool,
)


class KozmographToolkit(BaseToolkit):
    """Kozmograph toolkit for interacting with the Kozmograph database.

    Setup:
        Install ``langchain-kozmograph``.

        .. code-block:: bash

            pip install -U langchain-kozmograph
            pip install -U neo4j # Client for Kozmograph

    Key init args:
        db: KozmographDB
            KozmographDB database object.
        llm: BaseLanguageModel
            The language model used by the toolkit, in particular for query generation.

    Instantiate:
        .. code-block:: python

            from langchain-kozmograph.toolkits import KozmographToolkit
            from langchain-kozmograph.kozmograph import KozmographDB

            toolkit = KozmographToolkit(
                db=db,
                llm=llm,
            )
    Tools:
        .. code-block:: python

            toolkit.get_tools()

        .. code-block:: none

            QueryKozmographTool


    """  # noqa: E501

    db: Kozmograph = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def get_tools(self) -> List[BaseTool]:
        """Return the list of tools in the toolkit."""
        return [
            QueryKozmographTool(db=self.db),
        ]
