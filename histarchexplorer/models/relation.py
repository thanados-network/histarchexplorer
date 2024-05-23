from typing import Any

from histarchexplorer.models.util import format_date, split_date_string


class Relation:
    def __init__(self, data: dict[str, Any]):
        self.label = data['label']
        self.relation_to_id = data['relationTo'].rsplit('/', 1)[-1]
        self.relation_to = data['relationTo']
        self.relation_type = data['relationType']
        self.relation_system_class = data['relationSystemClass']
        self.relation_description = data['relationDescription']
        self.type = data['type']
        self.begin_from = None
        self.begin_to = None
        self.begin_comment = None
        self.end_from = None
        self.end_to = None
        self.begin = None
        self.end = None
        if 'when' in data:
            self.begin_from = split_date_string(
                data['when']['timespans'][0]['start']['earliest'])
            self.begin_to = split_date_string(
                data['when']['timespans'][0]['start']['latest'])
            self.end_from = split_date_string(
                data['when']['timespans'][0]['end']['earliest'])
            self.end_to = split_date_string(
                data['when']['timespans'][0]['end']['latest'])
            self.begin = format_date(self.begin_from, self.begin_to)
            self.end = format_date(self.end_from, self.end_to)

    def __repr__(self) -> str:
        return str(self.__dict__)
