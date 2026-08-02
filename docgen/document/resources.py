"""Validated resource lookup for document and presentation renderers."""

from docgen.config.document import FigureResource, ResourcesConfig, TableResource


class ResourceError(ValueError):
    pass


class ResourceRegistry:
    def __init__(self, resources: ResourcesConfig):
        self._tables = {table.id: table for table in resources.tables}
        self._figures = {figure.id: figure for figure in resources.figures}

    def table(self, resource_id: str) -> TableResource:
        try:
            return self._tables[resource_id]
        except KeyError as error:
            raise ResourceError(f"unknown table resource: {resource_id}") from error

    def figure(self, resource_id: str) -> FigureResource:
        try:
            return self._figures[resource_id]
        except KeyError as error:
            raise ResourceError(f"unknown figure resource: {resource_id}") from error
