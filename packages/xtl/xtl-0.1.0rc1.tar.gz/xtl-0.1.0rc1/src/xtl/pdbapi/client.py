import json
import requests
import warnings

from xtl.pdbapi.attributes import DataAttribute, DataAttributeGroup
from xtl.pdbapi.search.options import ReturnType, RequestOptions
from xtl.pdbapi.search.nodes import SearchQueryNode, SearchQueryField, SearchQueryGroup
from xtl.pdbapi.data.options import GQLField
from xtl.pdbapi.data.nodes import DataQueryField, DataQueryGroup
from xtl.exceptions import InvalidArgument


class SearchQueryResponse:

    def __init__(self, response: requests.Response):
        """
        Representation of a RCSB Search API response.

        :param response: requests.Response object to process
        """
        try:
            self.json = response.json()
        except:
            self.json = {}
        self.query_id = self.json.get('query_id', '')
        self.result_type = self.json.get('result_type', '')
        self.total_count = self.json.get('total_count', 0)
        self.explain_metadata = self.json.get('explain_metadata', {})
        self.result_set = self.json.get('result_set', [])
        self.group_by = self.json.get('group_by', {})
        self.group_set = self.json.get('group_set', [])
        self.facets = self.json.get('facets', [])

    @property
    def pdbs(self) -> list[str]:
        """
        A list of the PDB IDs that resulted from a search.

        :return:
        """
        return [item['identifier'] for item in self.result_set]


class DataQueryResponse:

    def __init__(self, query_tree: dict, response: requests.Response):
        """
        Representation of a RCSB Data API response

        :param query_tree:
        :param response:
        """
        try:
            self.json = response.json()
        except:
            self.json = {}
        self.query_tree = query_tree
        self._errors = self.json.get('errors', {})
        self.data = self.json.get('data', {})
        self.entries = self.data.get('entries', [])
        self.polymer_entities = self.data.get('polymer_entities', [])
        self.branched_entities = self.data.get('branched_entities', [])
        self.nonpolymer_entities = self.data.get('nonpolymer_entities', [])
        self.polymer_instances = self.data.get('polymer_instances', [])
        self.branched_instances = self.data.get('branched_instances', [])
        self.nonpolymer_instances = self.data.get('nonpolymer_instances', [])
        self.assemblies = self.data.get('assemblies', [])
        self.chem_comps = self.data.get('chem_comps', [])
        self._valid_id_types = ('entries', 'polymer_entities', 'nonpolymer_entities', 'polymer_instances',
                                'branched_instances', 'nonpolymer_instances', 'assemblies', 'chem_comps')

    @property
    def ok(self):
        if self._errors:
            return False
        return True

    @property
    def error(self, msg_only=True):
        if msg_only:
            return self._errors[0]['message']
        else:
            return self._errors

    def _flatten_dict(self, dict_):
        new_dict = {}
        for key, value in dict_.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, dict):
                        new_dict[f"{key}.{k}"] = self._flatten_dict(v)
                    else:
                        new_dict[f"{key}.{k}"] = v
            else:
                new_dict[key] = value
        return new_dict

    def _flatten_tree(self):
        titles = []
        for key, value in self.query_tree.items():
            if key == '':
                titles += [f'{v}' for v in value]
            elif isinstance(value, list):
                titles += [f'{key}.{v}' for v in value]
            else:
                raise Exception(f'Unsupported case: {key=} {value=}')
        return titles

    def tabulate(self, attr: str = 'entries'):
        if attr not in self._valid_id_types:
            raise InvalidArgument(raiser='attr', message=f'Must be one of: {", ".join(self._valid_id_types)}')
        titles = self._flatten_tree()
        flattened = [self._flatten_dict(i) for i in getattr(self, attr, [])]
        table = [[entry[prop] for prop in titles] for entry in flattened]
        return table, titles


class Client:

    SEARCH_URL: str = 'https://search.rcsb.org/rcsbsearch/v2/query'
    # DATA_URL: str = 'https://data.rcsb.org/rest/v1/core'
    DATA_GRAPHQL_URL: str = 'https://data.rcsb.org/graphql'

    def __init__(self, request_options=RequestOptions()):
        """
        A client for quering the RCSB Search API

        :param request_options:
        """
        self.return_type = ReturnType.ENTRY
        self.request_options = request_options
        self._query: SearchQueryField or SearchQueryGroup

    @property
    def request(self):
        """
        Request to send to the API

        :return:
        """
        result = {
            'return_type': self.return_type.value,
        }
        if self._query:
            result['query'] = self._query.to_dict()
        if self.request_options.to_dict():
            result['request_options'] = self.request_options.to_dict()
        return result

    def search(self, query: SearchQueryField or SearchQueryGroup):
        """
        Perform a query using the RCSB Search API

        :param query:
        :return:
        """
        if not issubclass(query.__class__, SearchQueryNode):
            raise InvalidArgument(raiser='query', message='Must be QueryField or QueryGroup')
        self._query = query
        response = requests.post(url=Client.SEARCH_URL, data=json.dumps(self.request))

        if not response.ok:
            warnings.warn(f'It appears request failed with status {response.status_code}:\n{response.text}')
            response.raise_for_status()
        if response.status_code == 204:
            warnings.warn('Request processed successfully, but no hits were found (status: 204).')

        return SearchQueryResponse(response)

    # def data(self, query: list, schema: str = 'entry'):
    #     '''
    #     Perform a query using the RCSB Data REST API. Experimental implementation!
    #
    #     :param query:
    #     :param schema:
    #     :return:
    #     '''
    #     warnings.warn('Experimental implementation of Client.data()')
    #     response = requests.get(url=f'{Client.DATA_URL}/{schema}/{"/".join(query)}')
    #
    #     if not response.ok:
    #         warnings.warn(f'It appears request failed with status {response.status_code}:\n{response.text}')
    #         response.raise_for_status()
    #     if response.status_code == 204:
    #         warnings.warn('Request processed successfully, but no hits were found (status: 204).')
    #
    #     return json.loads(response.text)

    def data(self, ids: list[str], attributes: DataQueryGroup or list[DataQueryField] or list[DataAttribute]):
        if isinstance(attributes, DataQueryGroup):
            attrs = attributes
        elif isinstance(attributes, list) or isinstance(attributes, tuple):
            attrs = DataQueryGroup.from_list(attributes)
        else:
            raise

        field = getattr(GQLField, attrs._data_service.name, GQLField.ENTRY).value
        entries = []
        for entry in ids:
            if field.separator not in entry:
                raise
            entries.append(f'"{entry}"')
        request = f'{self.DATA_GRAPHQL_URL}?query={{{field.name}({field.identifiers}:[{",".join(entries)}])' \
                  f'{{{attrs.to_gql()}}}}}'

        response = DataQueryResponse(query_tree=attrs.tree, response=requests.get(request))

        if not response.ok:
            warnings.warn(f'It appears request failed with message:\n{response.error()}')

        return response