"""Kozmograph tools."""

from typing import Any, Dict, List, Optional, Type

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from langchain_kozmograph.graphs.kozmograph import Kozmograph


class BaseKozmographTool(BaseModel):
    """
    Base tool for interacting with Kozmograph.
    """

    db: Kozmograph = Field(exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class _QueryKozmographToolInput(BaseModel):
    """
    Input query for Kozmograph Query tool.
    """

    query: str = Field(..., description="The query to be executed in Kozmograph.")


class QueryKozmographTool(BaseKozmographTool, BaseTool):  # type: ignore[override]
    """Tool for querying Kozmograph.

    Setup:
        Install ``langchain-kozmograph`` and make sure Kozmograph is running.

        .. code-block:: bash
            pip install -U langchain-kozmograph

    Instantiation:
        .. code-block:: python

            tool = QueryKozmographTool(
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"query" : "MATCH (n) RETURN n LIMIT 1"})

        .. code-block:: python

            # Output of invocation
            # List[Dict[str, Any]
            [
                {
                    "n": {
                        "name": "Alice",
                        "age": 30
                    }
                }
            ]

    """  # noqa: E501

    name: str = "kozmograph_cypher_query"
    """The name that is passed to the model when performing tool calling."""

    description: str = (
        "Tool is used to query Kozmograph via Cypher query and returns the result."
    )
    """The description that is passed to the model when performing tool calling."""

    args_schema: Type[BaseModel] = _QueryKozmographToolInput
    """The schema that is passed to the model when performing tool calling."""

    # TODO: Add any other init params for the tool.
    # param1: Optional[str]
    # """param1 determines foobar"""

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Dict[str, Any]]:
        return self.db.query(query)
