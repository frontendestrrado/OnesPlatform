
from dataclasses import dataclass
from typing import List, Union
import os, json


class PageKeys:
    PAGE_NAME: str = "page_name"
    PAGE_INTERESTS: str = "interests"
    AGE: str = "age"
    LOCATION: str = "location"
    LANGUAGE = str = 'language'
    MORE_INTERESTS: str = "more_interests"
    PAGE_MAIN_ATTRIBS = [PAGE_NAME, PAGE_INTERESTS, AGE, LOCATION, LANGUAGE]
    PAGE_OTHER_ATTRIBS = [MORE_INTERESTS]


class PageKeyWords:
    MAIN_PAGE: List[str] = ["wants to reach people like you who may have", "wants 10 reach people like you who may have"]
    PAGE_NAME: List[str] = ["wants to reach people like you who may have", "wants 10 reach people like you who may have"]
    PAGE_INTERESTS: List[str] = ["shown interest in"]
    AGE: List[str] = ["set their age"]
    LOCATION: List[str] = ["aprimary location in"]
    LANGUAGE: List[str] = ['A Communicated in']
    MORE_INTERESTS: List[str] = [""]

    ATTRIBS_MAP = {
        PageKeys.PAGE_NAME: PAGE_NAME,
        PageKeys.PAGE_INTERESTS: PAGE_INTERESTS,
        PageKeys.AGE: AGE,
        PageKeys.LOCATION: LOCATION,
        PageKeys.LANGUAGE: LANGUAGE,
        PageKeys.MORE_INTERESTS: MORE_INTERESTS,
    }


@dataclass
class Pages:
    pages_data: str

    def __post_init__(self):
        self.ordered_pages_data = dict(enumerate(self.pages_data))
        self.pages = {}
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.related_pages = {}

    def __add_page(
        self,
        page_name: str,
        interests: str,
        age: str,
        location: str,
        language: str,
        more_interests: List[str],
    ):
        page_data = {
            PageKeys.PAGE_NAME: page_name,
            PageKeys.PAGE_INTERESTS: interests,
            PageKeys.MORE_INTERESTS: more_interests,
            PageKeys.AGE: age,
            PageKeys.LANGUAGE: language,
            PageKeys.LOCATION: location,
        }
        self.pages[str(len(self.pages))] = page_data

    @staticmethod
    def __list_filter(item: List[str], filters: List[str]) -> List[str]:
        for filter_str in filters:
            is_filter_matched = (
                len([data_str for data_str in item if filter_str in data_str.lower()])
                > 0
            )
            if is_filter_matched:
                return True
        return False

    def _get_main_pages(self):
        main_pages = dict(
            filter(
                lambda item: self.__list_filter(item[1], PageKeyWords.MAIN_PAGE),
                self.ordered_pages_data.items(),
            )
        )
        self.related_pages = dict(
            filter(
                lambda item: item[0] not in main_pages, self.ordered_pages_data.items()
            )
        )
        return list(main_pages.values())

    @staticmethod
    def __extract_attrib_Value(
        main_page: List[str],
        attrib_keywords: List[str],
        extract_type: int = 1,
    ) -> str:
        for attrib_keyword in attrib_keywords:
            for item_str in main_page:
                if item_str and attrib_keyword in item_str.lower():
                    if extract_type == 1:
                        return item_str

                    elif extract_type == 2:
                        return item_str.replace(attrib_keyword, "").strip()
        return None

    def _extract_attribs(self, main_page, other_attribs=False):
        attribs = {}
        current_attribs = (
            PageKeys.PAGE_OTHER_ATTRIBS if other_attribs else PageKeys.PAGE_MAIN_ATTRIBS
        )
        if other_attribs:
            return dict(more_interests=main_page[:-1])
        extract_type = 1
        for attrib in current_attribs:
            if attrib == PageKeys.PAGE_NAME:
                extract_type = 2
            attrib_keywords = PageKeyWords.ATTRIBS_MAP[attrib]
            attribs[attrib] = self.__extract_attrib_Value(
                main_page, attrib_keywords, extract_type
            )
        return attribs

    @staticmethod
    def __lowerizer_list(lists: List[str]) -> List[str]:
        return [item_str.lower().strip() for item_str in lists]

    def __word_matched(self, item_str: List[str], interests: List[str]) -> bool:
        item_words, interests_words = self.__lowerizer_list(
            item_str.split(" ")
        ), self.__lowerizer_list(interests.split(" ") if interests else '')

        return len([word for word in item_words if word in interests_words]) > 0

    def _find_related_page(self, main_page: List[str], page_main_attribs: dict):
        if PageKeys.PAGE_INTERESTS in page_main_attribs:
            main_page_interests = page_main_attribs[PageKeys.PAGE_INTERESTS]
            for related_page_id, related_page in self.related_pages.items():
                for item_str in related_page:
                    if related_page_id not in self.related_pages:
                        return ""
                    if self.__word_matched(item_str, main_page_interests):
                        del self.related_pages[related_page_id]
                        return related_page

        return ""

    def parse_pages(self):
        main_pages = self._get_main_pages()
        for main_page in main_pages:
            page_main_attribs = self._extract_attribs(main_page)
            related_page = self._find_related_page(main_page, page_main_attribs)
            page_other_attribs = self._extract_attribs(related_page, other_attribs=True)
            self.__add_page(**page_main_attribs, **page_other_attribs)

    def to_dict(self) -> dict:
        return self.pages

    def save(self, filename: str) -> str:
        file_path = os.path.join(self.root_path, f"{filename}.json")
        with open(file_path, "w") as file:
            json.dump(self.pages, file)
        return file_path

    def show_dict(self):
        return self.pages


# pages_client = Pages(sample_data)
# pages_client.parse_pages()
# pages_client.save("sample")
