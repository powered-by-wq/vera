from wq.db.patterns.identify.filters import IdentifierFilterBackend


class ChartFilterBackend(IdentifierFilterBackend):
    exclude_apps = ['dbio']

    def filter_by_site(self, qs, ids):
        return qs.filter(event_site__in=ids)

    def filter_by_parameter(self, qs, ids):
        return qs.filter(result_type__in=ids)
