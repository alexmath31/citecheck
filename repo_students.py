import dataclasses
import json
import os
from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Union, overload, List


@dataclass
class Link:
    url: str
    hash_id: str
    created_at: datetime
    views: int = 0

    def to_dict(self):
        asdict = dataclasses.asdict(self)
        asdict["created_at"] = self.created_at.isoformat()
        return asdict

    @classmethod
    def from_dict(cls, link_as_dict):
        return cls(
            url=link_as_dict["url"],
            hash_id=link_as_dict["hash_id"],
            created_at=datetime.fromisoformat(link_as_dict["created_at"]),
            views=link_as_dict.get("views", 0),
        )


class LinkRepository(ABC):
    @overload
    def get(self) -> List[Link]:
        ...

    @overload
    def get(self, hash_id: str) -> Link:
        ...

    @abstractmethod
    def get(self, hash_id: Optional[str] = None) -> Union[List[Link], Link]:
        pass

    @abstractmethod
    def create(self, link: Link) -> Link:
        pass


class InMemoryLinkRepository(LinkRepository):
    def __init__(self) -> None:
        self._links: Dict[str, Link] = {}

    @overload
    def get(self) -> List[Link]:
        ...

    @overload
    def get(self, hash_id: str) -> Link:
        ...

    def get(self, hash_id: Optional[str] = None) -> Union[List[Link], Link]:
        if hash_id is None:
            return list(self._links.values())
        else:
            return self._links[hash_id]

    def create(self, link: Link) -> Link:
        self._links[link.hash_id] = link
        return link

    def update(self, link, add_views: int = 1) -> Link:
        link.views += add_views
        self._links[link.hash_id] = link
        return link


class FileSystemLinkRepository(LinkRepository):
    def __init__(self, path: Union[str, Path]):
        self.path = os.path.join(path, "db")
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def create(self, link: Link) -> Link:
        with open(os.path.join(self.path, f"{link.hash_id}.txt"), "x") as f:
            json.dump(link.to_dict(), fp=f)
        return link

    @overload
    def get(self) -> List[Link]:
        ...

    @overload
    def get(self, hash_id: str) -> Link:
        ...

    def get(self, hash_id: Optional[str] = None) -> Union[Link, List[Link]]:
        if hash_id is not None:
            return self._read_single_link(hash_id)
        else:
            links = []
            for filename in os.listdir(self.path):
                hash_id = filename.removesuffix(".txt")
                link = self._read_single_link(hash_id)
                links.append(link)
            return links

    def _read_single_link(self, hash_id):
        with open(os.path.join(self.path, f"{hash_id}.txt")) as f:
            link_json = json.load(f)
            link = Link.from_dict(link_json)
        return link

    def update(self, link, add_views: int = 1):
        link.views += add_views
        with open(os.path.join(self.path, f"{link.hash_id}.txt"), "w") as f:
            json.dump(link.to_dict(), fp=f)
        return link


repository = FileSystemLinkRepository(os.getcwd())
