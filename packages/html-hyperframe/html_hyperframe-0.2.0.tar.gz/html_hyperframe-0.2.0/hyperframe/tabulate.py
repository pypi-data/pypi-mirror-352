import pandas as pd
from bs4 import NavigableString, Tag

# A path to some content within a hyper structure
# e.g (div, 0, div, 2, p, text)
HyperPath = tuple[str | int, ...]


def get_cleaned_attributes(tag: Tag) -> dict[str, str]:
    attributes = {}
    for attr, content in tag.attrs.items():
        if isinstance(content, list):
            # Beautiful soup turns class content into a list by splitting
            # at spaces. This turns it back into a single string.
            content = " ".join(content)
        attributes[attr] = content
    return attributes


def extract_content_from_tag(tag: Tag) -> dict[HyperPath, str]:
    content_by_hyperpath: dict[HyperPath, str] = {
        (tag.name, attr): content
        for attr, content in get_cleaned_attributes(tag).items()
    }

    for i, inner_element in enumerate(tag):
        if isinstance(inner_element, NavigableString):
            element_path: HyperPath = (tag.name, i, "text")
            content_by_hyperpath[element_path] = str(inner_element).strip()

        if isinstance(inner_element, Tag):
            inner_content_by_path = extract_content_from_tag(inner_element)
            for inner_path, inner_content in inner_content_by_path.items():
                element_path = (tag.name, i, *inner_path)
                content_by_hyperpath[element_path] = inner_content

    return content_by_hyperpath


def tabulate_from_hyperpattern_tags(tags_with_structure: list[Tag]) -> pd.DataFrame:
    """
    Takes tags with the same HYPER_STRUCTURE and returns a DataFrame with a row
    for every tag, and a column for each text string or attribute contained by
    the elements within the structure.

    An example:
                                (article, id)       (article, 0, a, href) (article, 0, a, 0, h1, 0, text)  ... (article, 0, a, 3, p, 0, text) (article, 0, a, 3, p, 2, text) (article, 0, a, 2, p, 4, text)
    0    cdbfd41c-186f-5955-b005-37107d694df4       /film/born-in-flames-                  Born in Flames  ...                    Directed by                  Lizzie Borden                            NaN
    1    856e9118-c9db-56c4-8da6-3c4a8ba66aed          /film/pandoras-box                   Pandora's Box  ...                    Directed by                     G.W. Pabst                        Germany
    2    6684a8db-7b4b-559b-97c3-a1c940e2903e     /film/sullivans-travels              Sullivan's Travels  ...                    Directed by                Preston Sturges                            USA
    3    37565e9a-6847-5a43-abea-6659ef2cce22            /film/annie-hall                      Annie Hall  ...                    Directed by                    Woody Allen                            USA
    4    7ecb717a-9c37-5071-a235-93386e7167b7                 /film/earth                           Earth  ...                    Directed by            Alexander Dovzhenko                           USSR
    ..                                    ...                         ...                             ...  ...                            ...                            ...                            ...
    258  cefccdb2-b558-5623-9c17-72b4be7bd4c1  /film/2001-a-space-odyssey           2001: A Space Odyssey  ...                    Directed by                Stanley Kubrick            USA, United Kingdom
    259  1b8c3bcb-842f-5ba2-90ee-39b6b40b7c21  /film/in-the-mood-for-love            In the Mood for Love  ...                    Directed by                   Wong Kar Wai              Hong Kong, France
    260  65edaa59-6546-57b5-9fa3-9409f93d1383           /film/tokyo-story                     Tokyo Story  ...                    Directed by                   Yasujirō Ozu                          Japan
    261  f4c92833-af39-5cd6-a41e-8df5933d0dc1          /film/citizen-kane                    Citizen Kane  ...                    Directed by                   Orson Welles                            USA
    262  489eada8-7d7e-594c-acac-5903f43f4b85               /film/vertigo                         Vertigo  ...                    Directed by               Alfred Hitchcock                            USA
    """  # noqa: E501
    tag_contents = [extract_content_from_tag(tag) for tag in tags_with_structure]
    hyperframe = pd.DataFrame.from_records(tag_contents)

    # Drop columns in which all values are empty (None, Nan or empty string)
    is_column_empty = ~hyperframe.any(axis=0)
    empty_columns = hyperframe.columns[is_column_empty]
    hyperframe.drop(columns=empty_columns, inplace=True)

    return hyperframe
