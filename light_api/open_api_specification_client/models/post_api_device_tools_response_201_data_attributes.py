from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_device_tools_response_201_data_attributes_config import (
        PostApiDeviceToolsResponse201DataAttributesConfig,
    )


T = TypeVar("T", bound="PostApiDeviceToolsResponse201DataAttributes")


@_attrs_define
class PostApiDeviceToolsResponse201DataAttributes:
    """
    Attributes:
        config (PostApiDeviceToolsResponse201DataAttributesConfig | Unset):
        deleted_at (None | str | Unset):
    """

    config: PostApiDeviceToolsResponse201DataAttributesConfig | Unset = UNSET
    deleted_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        deleted_at: None | str | Unset
        if isinstance(self.deleted_at, Unset):
            deleted_at = UNSET
        else:
            deleted_at = self.deleted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_device_tools_response_201_data_attributes_config import (
            PostApiDeviceToolsResponse201DataAttributesConfig,
        )

        d = dict(src_dict)
        _config = d.pop("config", UNSET)
        config: PostApiDeviceToolsResponse201DataAttributesConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = PostApiDeviceToolsResponse201DataAttributesConfig.from_dict(_config)

        def _parse_deleted_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deleted_at = _parse_deleted_at(d.pop("deleted_at", UNSET))

        post_api_device_tools_response_201_data_attributes = cls(
            config=config,
            deleted_at=deleted_at,
        )

        post_api_device_tools_response_201_data_attributes.additional_properties = d
        return post_api_device_tools_response_201_data_attributes

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
