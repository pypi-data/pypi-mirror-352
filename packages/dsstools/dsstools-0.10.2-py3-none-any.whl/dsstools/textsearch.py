# Copyright (C) 2024 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""This module allows for text search in graph nodes. """

from __future__ import annotations

import logging
import warnings
from functools import singledispatchmethod
from typing import List, Union

import networkx as nx
import pandas as pd

from dsstools.wdcgeneric import WDC

from .attrs import Category, Code

logger = logging.getLogger("dsstools")


class TextSearch(WDC):
    """Class allowing to search for keywords in the WDC API.
    Args:
          identifier: Identifier of the network data. For the text search this is
          normally in the form `20121227_intermediaries` (a date string with a short
          text appended).
          token: Token for authorization.
          api: API address to send request to. Leave this as is.
          insecure: Hide warning regarding missing https.
          timeout: Set the timeout to the server. Increase this if you request large
            networks.
          params: These are additional keyword arguments passed onto the API endpoint. See
            https://dss-wdc.wiso.uni-hamburg.de/#_complex_datatypes_for_the_api_requests
            for further assistance.
            """

    endpoint = "snapshot"
    def __init__(self,
                 identifier: str | None = None,
                 *,
                 token: str | None = None,
                 api: str = "https://dss-wdc.wiso.uni-hamburg.de/api",
                 insecure: bool = False,
                 timeout: int = 60,
                 params: dict | None = None,
                 ):
        super().__init__(token=token, api=api, insecure=insecure, timeout=timeout, params=params)
        self.identifier = identifier

    @staticmethod
    def _handle_grafted_terms(fun):
        def wrapper(*args, **kwargs):
            domain, terms = args
            # Flatten list internally
            if all(isinstance(term, list) for term in terms):
                response = fun(domain, [t for te in terms for t in te], **kwargs)
                if response is not None:
                    return {
                        term_group[0]: sum(response.get(term) for term in term_group)
                        for term_group in terms
                    }
                else:
                    return response
            elif any(isinstance(term, list) for term in terms):
                raise ValueError(
                    "The passed term list does not exclusively contain either strings or lists."
                )
            else:
                return fun(domain, terms, **kwargs)

        return wrapper

    def _construct_url(self) -> str:
        if self.identifier:
            return f"{self.api}/{self.endpoint}/{self.identifier}/"
        else:
            raise ValueError("Please set a snapshot id to the TextSearch object first.")

    def get_missing(self, domains):
        domain_hits = set()
        for page in self._get_results(self._construct_url() + "domains"):
            for data in page["content"]:
                domain_hits.add(data["domainName"])
        return set(domains) - domain_hits

    def get_snapshots(self, name_tag="") -> set:
        snapshots = set()
        for page in self._get_results(self._construct_url_base() + "/list"):
            for data in page["content"]:
                if name_tag in data["name"]:
                    snapshots.add(data["name"])
        return snapshots

    def __query_domains(
            self, domains, query_term, missing_domains=None, key=None
    ) -> dict:
        if key is None:
            key = query_term

        domain_hits = {}
        # The argument query_term overwrites any passed "query" key.
        params = self.params | {"query": query_term}
        for page in self._get_results(self._construct_url() + "searchDomains", params):
            for data in page["content"]:
                domain_hits[data["domainName"]] = data["hits"]
        single_term_hits = {}
        for domain in domains:
            if domain in missing_domains:
                # Make missing domains a None for visualization purposes.
                single_term_hits[domain] = None
            else:
                # Make zero hits an actual zero (and not None).
                single_term_hits[domain] = domain_hits.get(domain, 0)
        return single_term_hits

    @singledispatchmethod
    def search(self, domains, terms, exact=True):
        """Searches the given keywords across a Graph or iterator.

        Args:
          domains (nx.Graph|list): Set of identifiers to search in.
          terms list[str]: Terms to search for.

        Returns:
          Updated graph or dict containing the responses, Set of all failed
          responses
        """
        raise NotImplementedError("Can only search on domain lists or graphs.")

    # TODO How to handle literal terms?
    @search.register
    def _(
        self,
        domains: list,
        terms: Union[
            List[str],
            List[List[str]],
            dict[str, str],
            dict[str, List[str]],
            pd.Series,
            pd.DataFrame,
        ],
        exact=True,
    ) -> dict:
        if not exact:
            raise NotImplementedError()

        term_hits = {}
        missing_domains = self.get_missing(domains)
        logger.info(f"The following terms are set for the query: {terms}")
        keys = {}
        if isinstance(terms, list):
            terms_iter = terms
        else:
            terms_iter = terms.items()

        for term in terms_iter:
            if isinstance(terms, (dict, pd.Series)):
                key, term = term
            elif isinstance(terms, pd.DataFrame):
                key, column = term
                term = column.to_list()
            elif isinstance(terms, list) and isinstance(term, list):
                key = term[0]
            else:
                key = term

            query_term = " OR ".join(term) if isinstance(term, list) else term
            logger.info(f"Querying API for {term}...")
            term_hits[key] = self.__query_domains(
                domains, query_term, missing_domains, key=key
            )

        # Transpose dict of dict (nested dict). We first get the keys from the first
        # entry and then construct the resulting new dictionary. See for an explanation
        # here:
        # https://stackoverflow.com/questions/33425871/rearranging-levels-of-a-nested-dictionary-in-python
        # This could also be done by converting to a Pandas DataFrame as a dict of dict
        # is equivalent to a 2D matrix:
        # df = pd.DataFrame.from_dict(term_hits).T
        keys = term_hits[next(iter(term_hits.keys()))].keys()
        return {
            key: {k: term_hits[k][key] for k in term_hits if key in term_hits[k]}
            for key in keys
        }

    @search.register
    def _(
        self,
        domains: nx.Graph,
        terms: Union[List[str], List[List[str]]],
        exact=True,
    ) -> nx.Graph:
        domain_hits = self.search(list(domains.nodes), terms)
        for node_id, values in domain_hits.items():
            node = domains.nodes[node_id]
            for key, value in values.items():
                if value is not None:
                    node[str(Code(key, Category.TEXT))] = value
        return domains
