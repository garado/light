from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_playlists_sort_mode_response_400_errors import PostApiPlaylistsSortModeResponse400Errors


T = TypeVar("T", bound="PostApiPlaylistsSortModeResponse400")


@_attrs_define
class PostApiPlaylistsSortModeResponse400:
    """
    Attributes:
        errors (PostApiPlaylistsSortModeResponse400Errors):
    """

    errors: PostApiPlaylistsSortModeResponse400Errors
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        errors = self.errors.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_playlists_sort_mode_response_400_errors import PostApiPlaylistsSortModeResponse400Errors

        d = dict(src_dict)
        errors = PostApiPlaylistsSortModeResponse400Errors.from_dict(d.pop("errors"))

        post_api_playlists_sort_mode_response_400 = cls(
            errors=errors,
        )

        post_api_playlists_sort_mode_response_400.additional_properties = d
        return post_api_playlists_sort_mode_response_400

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
