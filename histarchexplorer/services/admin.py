from histarchexplorer.database.admin import (
    set_hidden_entities, set_index_background, set_shown_entities)


class Admin:

    @staticmethod
    def set_hidden_entities(form: list[str]) -> None:
        return set_hidden_entities(form)

    @staticmethod
    def set_shown_entities(form: list[str]) -> None:
        return set_shown_entities(form)

    @staticmethod
    def set_index_background(settings: dict[str, str]) -> None:
        return set_index_background(settings)
