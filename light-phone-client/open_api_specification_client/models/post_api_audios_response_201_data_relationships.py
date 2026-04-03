from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_audios_response_201_data_relationships_processed_file import (
        PostApiAudiosResponse201DataRelationshipsProcessedFile,
    )
    from ..models.post_api_audios_response_201_data_relationships_raw_file import (
        PostApiAudiosResponse201DataRelationshipsRawFile,
    )


T = TypeVar("T", bound="PostApiAudiosResponse201DataRelationships")


@_attrs_define
class PostApiAudiosResponse201DataRelationships:
    """
    Attributes:
        processed_file (PostApiAudiosResponse201DataRelationshipsProcessedFile):
        raw_file (PostApiAudiosResponse201DataRelationshipsRawFile):
    """

    processed_file: PostApiAudiosResponse201DataRelationshipsProcessedFile
    raw_file: PostApiAudiosResponse201DataRelationshipsRawFile
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        processed_file = self.processed_file.to_dict()

        raw_file = self.raw_file.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processed_file": processed_file,
                "raw_file": raw_file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_audios_response_201_data_relationships_processed_file import (
            PostApiAudiosResponse201DataRelationshipsProcessedFile,
        )
        from ..models.post_api_audios_response_201_data_relationships_raw_file import (
            PostApiAudiosResponse201DataRelationshipsRawFile,
        )

        d = dict(src_dict)
        processed_file = PostApiAudiosResponse201DataRelationshipsProcessedFile.from_dict(d.pop("processed_file"))

        raw_file = PostApiAudiosResponse201DataRelationshipsRawFile.from_dict(d.pop("raw_file"))

        post_api_audios_response_201_data_relationships = cls(
            processed_file=processed_file,
            raw_file=raw_file,
        )

        post_api_audios_response_201_data_relationships.additional_properties = d
        return post_api_audios_response_201_data_relationships

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
