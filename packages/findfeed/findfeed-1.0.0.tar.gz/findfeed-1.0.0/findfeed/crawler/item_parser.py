from abc import ABC, abstractmethod
from types import AsyncGeneratorType
from typing import Union

from findfeed.crawler.item import Item
from findfeed.crawler.request import Request
from findfeed.crawler.response import Response


class ItemParser(ABC):
    def __init__(self, crawler):
        self.crawler = crawler
        self.follow = crawler.follow

    @abstractmethod
    async def parse_item(
        self, request: Request, response: Response, *args, **kwargs
    ) -> Union[Item, AsyncGeneratorType]:
        raise NotImplementedError("Not Implemented")
