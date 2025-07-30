from collections import defaultdict
from collections.abc import Iterator

import pandas as pd
from bs4 import BeautifulSoup, Tag

from .tabulate import tabulate_from_hyperpattern_tags

# Represents a structure defined by the elements in a section of the HTML tree e.g
# (
#     "div", (
#         "a", (
#             "p", ()
#         ),
#         "span", ()
#     )
# )
HYPER_STRUCTURE = tuple[str, tuple]


def get_tag_structures(tag: Tag) -> dict[Tag, HYPER_STRUCTURE]:
    """
    Find the HTML structure that each tag encapsulates.
    """
    tag_structures = {}
    substructure = []
    inner_tags = (element for element in tag if isinstance(element, Tag))

    for inner_tag in inner_tags:
        inner_tag_structures = get_tag_structures(inner_tag)
        inner_structure = inner_tag_structures[inner_tag]
        tag_structures.update(inner_tag_structures)
        substructure.append(inner_structure)

    structure = (tag.name, tuple(substructure))
    tag_structures[tag] = structure
    return tag_structures


class HyperPattern:
    """
    A hyper pattern is structure, along with it's Tag instances, which
    is both "maximal" and "recurrent".  (See is_structure_maximal and
    is_a_recurrent_structure).
    """

    def __init__(self, structure: HYPER_STRUCTURE, tags_with_structure: list[Tag]):
        self.structure = structure
        self.tags_with_structure = tags_with_structure

    def does_pattern_have_twinned_instance(self) -> bool:
        """
        Check if this pattern occurs more than once as a child of a single parent.

        Patterns containing related content often have a twinned instance.
        One may want to ignore patterns without a twinned instance.
        """
        parents = set()
        for tag in self.tags_with_structure:
            if tag.parent in parents:
                # Pattern occurs twice under parent
                return True
            parents.add(tag.parent)
        return False

    def get_hyperframe(self) -> pd.DataFrame:
        return tabulate_from_hyperpattern_tags(self.tags_with_structure)


class HyperPatternHunter:
    def __init__(self, soup: BeautifulSoup):
        self.tag_structures = get_tag_structures(soup)

        self.tags_by_structure = defaultdict(list)
        for tag, structure in self.tag_structures.items():
            self.tags_by_structure[structure].append(tag)

    def is_structure_maximal(self, tags_with_structure: list[Tag]) -> bool:
        """
        Check if this structure is maximal.

        A structure is not maximal if all of it's tags have different parents
        but the same parent structure.

        In other words a structure is maximal if there are no larger structures
        for which there is a one-to-one relationship between instances of the smaller
        structure and the larger structure defined by the larger instance
        containing the smaller instance.
        """
        parents = set()
        parent_structures = set()

        for tag in tags_with_structure:
            if tag.parent is None:
                return True

            if tag.parent in parents:
                # Must be maximal as two or more of these tags have the same parent
                return True

            parents.add(tag.parent)
            parent_structures.add(self.tag_structures[tag.parent])
            if len(parent_structures) > 1:
                return True
        return False

    def is_a_recurrent_structure(self, tags_with_structure: list[Tag]) -> bool:
        """
        Does this structure occur more than once?
        """
        n_instances_of_structure = len(tags_with_structure)
        return n_instances_of_structure > 1

    def yield_hyperpatterns(self) -> Iterator[HyperPattern]:
        """
        Yield hyperpatterns - maximally recurrent hyper structures in the html
        """
        for structure, tags_with_structure in self.tags_by_structure.items():
            is_recurrent_and_maximal = self.is_a_recurrent_structure(
                tags_with_structure
            ) and self.is_structure_maximal(tags_with_structure)
            if is_recurrent_and_maximal:
                # This is a hyper pattern.
                yield HyperPattern(structure, tags_with_structure)
