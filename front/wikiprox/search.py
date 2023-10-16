from elastictools import search


def limit_offset(request, results_per_page):
    return search.limit_offset(request, results_per_page)

class Searcher(search.Searcher):

    def prepare(
        self,
        params,            # {}
        params_whitelist,  # SEARCH_PARAM_WHITELIST
        search_models,     # SEARCH_MODELS
        sort,              # []
        fields,            # SEARCH_INCLUDE_FIELDS
        fields_nested,     # SEARCH_NESTED_FIELDS
        fields_agg,        # SEARCH_AGG_FIELDS
        wildcards=False,
    ):
        if search_models == ['encycarticle']:
            params['published_encyc'] = True  # only show Encyclopedia items
        return super().prepare(
            params, params_whitelist, search_models, sort,
            fields, fields_nested, fields_agg, wildcards,
        )
