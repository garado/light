from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiToolsResponse200DataItemAttributes")


@_attrs_define
class GetApiToolsResponse200DataItemAttributes:
    """
    Attributes:
        component (str):
        min_apk_version (int):
        namespace (str):
        status (str):
        title (str):
    """

    component: str
    min_apk_version: int
    namespace: str
    status: str
    title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component = self.component

        min_apk_version = self.min_apk_version

        namespace = self.namespace

        status = self.status

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "component": component,
                "min_apk_version": min_apk_version,
                "namespace": namespace,
                "status": status,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        component = d.pop("component")

        min_apk_version = d.pop("min_apk_version")

        namespace = d.pop("namespace")

        status = d.pop("status")

        title = d.pop("title")

        get_api_tools_response_200_data_item_attributes = cls(
            component=component,
            min_apk_version=min_apk_version,
            namespace=namespace,
            status=status,
            title=title,
        )

        get_api_tools_response_200_data_item_attributes.additional_properties = d
        return get_api_tools_response_200_data_item_attributes

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
