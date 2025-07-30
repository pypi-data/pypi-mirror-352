from __future__ import annotations

from abc import ABC, abstractmethod

import networkx as nx

from typing import Callable, Iterator, Mapping, Optional, TypeVar
from networkx.classes.reportviews import InEdgeDataView, OutEdgeDataView, NodeDataView

import numpy as np

NxElementView = TypeVar(
    "NxElementView", NodeDataView, OutEdgeDataView, InEdgeDataView, Iterator[tuple]
)


class IncorrectKeyword(Exception):
    pass


class Supplier(ABC):
    """Basic interface for supplying graph element values."""

    def __init__(self):
        self.fallback = None

    def _set_fallback(self, fallback):
        self.fallback = fallback

    @abstractmethod
    def _get_values(self, graph_element, graph: nx.Graph) -> dict:
        pass


class ElementAttribute(Supplier):
    """Class for graph element values (already set in the graph."""

    keyword: str = ""

    def __init__(self, keyword: str):
        """
        Args:
            keyword: the key of the inherent attribute
        """
        super().__init__()
        self.keyword = keyword

    def __str__(self):
        return f"scaling: on '{self.keyword}'"

    def __repr__(self):
        return str(self)

    def _get_values(self, graph_element: NxElementView, graph) -> dict:
        """Get values based on scalable attributes inherent to graph items.

        Args:
            graph_element:
            graph:

        Returns:
            a dictionary with the graph element item[key] and the attribute value corresponding to the
            keyword[value] stored in the graph element
        """
        # Node Element
        try:
            supplier = {i: k.get(self.keyword) for i, k in graph_element}
            if all(v is None for v in supplier.values()):
                raise IncorrectKeyword(
                    f'No valid values for "{self.keyword}" found. Try checking that the keyword is correct. The keyword must reference numeric values.'
                )

            return supplier
        # Edge Element
        except ValueError:
            supplier = {(i, j): k.get(self.keyword) for i, j, k in graph_element}

            if all(v is None for v in supplier.values()):
                raise IncorrectKeyword(
                    f'No valid values for "{self.keyword}" found. Try checking that the keyword is correct. The keyword must reference numeric values.'
                )

            return supplier


class StructuralAttribute(Supplier):
    """Class for providing structural graph element values.

    These are attributes based on the graph structure and need to be calculated."""

    ATTRIBUTES = [
        "indegree",
        "outdegree",
        "degree",
        "centrality",
        "betweenness",
        "closeness",
    ]

    def __init__(
        self,
        keyword: Optional[str] = None,
        *,
        reverse: bool = False,
        alt_nx_calculation: Optional[Callable] = None,
    ):
        """

        Args:
            keyword: the keyword for the calculation
            reverse: determines if the calculation should use inverted edge values if True, default False
        """
        super().__init__()
        self.__keyword: str | None = keyword.lower() if keyword is not None else None
        self.reverse = reverse
        self.alt_nx_calculation = alt_nx_calculation if keyword is None else None

        if self.alt_nx_calculation == self.__keyword:
            raise ValueError(
                f"Either pass a keyword or pass an alternative nx graph calculation"
            )

    def _get_values(self, graph_element: NxElementView, graph: nx.Graph) -> dict:
        """Calculate the attributes of the graph based off the given keyword.

        Valid keywords are the following:
        indegree, outdegree, degree, centrality, betweenness, closeness

        Args:
            graph_element: NxElementView
            graph: nx.Graph

        Returns:
            a dictionary with the node[key] and the calculated value[value]
        """
        if self.reverse:
            graph = nx.reverse(graph)

        if self.__keyword is None and self.alt_nx_calculation:
            return self.alt_nx_calculation(graph)

        # The following takes a long time to calculate, old implementation saves
        # it as inherent attr as an inbetween step.
        if self.__keyword == "betweenness":
            if isinstance(graph_element, NodeDataView):
                return nx.betweenness_centrality(graph)
            else:
                return nx.edge_betweenness_centrality(graph)

        if isinstance(graph_element, NodeDataView):
            if self.__keyword == "indegree":
                return nx.in_degree_centrality(graph)

            if self.__keyword == "outdegree":
                return nx.out_degree_centrality(graph)

            if self.__keyword == "degree":
                return nx.degree_centrality(graph)

            if self.__keyword == "closeness":
                return nx.closeness_centrality(graph)
            raise ValueError(f"Unable to parse the given keyword: {self.__keyword}")

        raise ValueError(f"This type of calculation is not supported for edges")


class Percentile(Supplier):
    """Class for filtering an existing supplier by the percentile."""

    def __init__(self, supplier: Supplier):
        """

        Args:
            supplier: Supplier whose values will be evaluated based on the percentile range, must contain numeric values
        """
        super().__init__()
        self.supplier = supplier
        self.percentile_method = "linear"
        self.percentile_range = None
        self.fallback = None

    def _set_percentile_method(self, method: str):
        self.percentile_method = method

    def _set_percentile_range(self, perc_range: tuple[int, int]):
        self.percentile_range = perc_range

    def _set_fallback(self, fallback):
        self.fallback = fallback

    def _get_values(self, graph_element, graph: nx.Graph) -> dict:
        """Calculate the percentile for each node in the graph element.

        Compare the result to the percentile range. If it is outside the percentile
        range, the node will be assigned the value True. If it is inside the percentile
        range, the node will be assigned the value False.

        Args:
            graph_element: NxElementView
            graph: nx.Graph

        Returns:
            a dictionary with the node[key] and the boolean value[value]
        """
        # NOTE np.percentile only goes from percentile to absolute values not absolute
        # values to percentile, works for filter not as calculation for supplier.
        # supplier returns boolean value for range

        if self.percentile_range is None:
            raise ValueError(
                "percentile_range cannot be None. Please set a valid range between 1-100"
            )
        supplier = self.supplier._get_values(graph_element, graph)
        # TODO? no need for if i != self.fallback check here because fallback only applies to Mapping
        values_filtered = [i for i in supplier.values() if i != self.fallback]
        values = np.fromiter(values_filtered, dtype=float)
        percentile_values = np.nanpercentile(
            a=values, q=self.percentile_range, method=self.percentile_method
        )

        # fallback = parse_color(self.percentile_fallback)
        percentile_iterator = {}

        # iterator for boolean supplier output
        for node, value in supplier.items():
            if (
                value is not None
                and not (percentile_values[0] <= value <= percentile_values[1])
                and value != self.fallback
            ):  # value != self.fallback unique to Sequential
                percentile_iterator[node] = True
            else:
                percentile_iterator[node] = False
        return percentile_iterator


# TODO create scale supplier to replace preprocessor (for node sizes + flexibility for
# filters)


class RawDictionary(Supplier):
    def __init__(self, dictionary: dict):
        """ Assign a dictionary to the graph elements.

        This can be a subgraph or a normal graph.  The keys must match at least one of
        the node ids or edge tuples. Example: The dictionaries returned by NetworkX
        calculations on graphs return suitable dictionaries

        Args:
            dictionary: key is GraphElement, value is value to be supplied
        """
        self.dictionary = dictionary
        self.fallback = None

    def _set_fallback(self, fallback):
        self.fallback = fallback

    def _get_values(self, graph_element, graph: nx.Graph) -> dict:
        # Node Element
        try:
            supplier = {i: k for i, k in graph_element}

        # Edge Element
        except ValueError:
            supplier = {(i, j): k for i, j, k in graph_element}

        for node, value in supplier.items():
            if (
                value is not None
                and node in self.dictionary.keys()
                and value != self.fallback
            ):  # value != self.fallback unique to Sequential
                supplier[node] = self.dictionary[node]
            else:
                supplier[node] = self.fallback

        return supplier
