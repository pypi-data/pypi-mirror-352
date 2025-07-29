"""Stream generation utilities for HTMX and Turbo."""

from typing import Optional

from .types import HypermediaType, StreamContent


class StreamGenerator:
    """Generates hypermedia streams for HTMX and Turbo."""

    @staticmethod
    def _make_turbo_stream(
        action: str, content: str, target: str, multiple: bool = False
    ) -> StreamContent:
        """Generate a Turbo Stream element."""
        target_attr = "targets" if multiple else "target"
        return (
            f'<turbo-stream action="{action}" {target_attr}="{target}">'
            f"<template>{content}</template></turbo-stream>"
        )

    @staticmethod
    def _make_htmx_stream(action: str, content: str, target: str) -> StreamContent:
        """Generate an HTMX stream object."""
        return {
            "type": "htmx",
            "action": action,
            "target": target,
            "content": content,
        }

    def append(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> StreamContent:
        """Create an append/afterend stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("beforeend", content, target)
        else:  # Turbo
            return self._make_turbo_stream("append", content, target, multiple)

    def prepend(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> StreamContent:
        """Create a prepend/afterbegin stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("afterbegin", content, target)
        else:  # Turbo
            return self._make_turbo_stream("prepend", content, target, multiple)

    def replace(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> StreamContent:
        """Create a replace/outerHTML stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("outerHTML", content, target)
        else:  # Turbo
            return self._make_turbo_stream("replace", content, target, multiple)

    def update(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> StreamContent:
        """Create an update/innerHTML stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("innerHTML", content, target)
        else:  # Turbo
            return self._make_turbo_stream("update", content, target, multiple)

    def remove(
        self, target: str, multiple: bool = False, hypermedia_type: Optional[str] = None
    ) -> StreamContent:
        """Create a remove/delete stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("delete", "", target)
        else:  # Turbo
            return self._make_turbo_stream("remove", "", target, multiple)

    def after(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> StreamContent:
        """Create an after/afterend stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("afterend", content, target)
        else:  # Turbo
            return self._make_turbo_stream("after", content, target, multiple)

    def before(
        self,
        content: str,
        target: str,
        multiple: bool = False,
        hypermedia_type: Optional[str] = None,
    ) -> StreamContent:
        """Create a before/beforebegin stream."""
        if hypermedia_type == HypermediaType.HTMX:
            return self._make_htmx_stream("beforebegin", content, target)
        else:  # Turbo
            return self._make_turbo_stream("before", content, target, multiple)
