from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_dependant
from fastapi.routing import APIRoute
from graphviz import Digraph


def solve_dependencies(app: FastAPI) -> list[Dependant]:
    dependencies: list[Dependant] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        dependencies.append(
            get_dependant(
                path="",
                call=route.endpoint,
                name=route.name,
            )
        )

    return dependencies


def get_dependency_name(dependency: Dependant) -> str:
    if dependency.call is not None:
        return dependency.call.__name__

    if dependency.name is not None:
        return dependency.name

    return ""


CacheKey = tuple[Callable[..., Any] | None, tuple[str, ...]]


def populate_digraph(
    dot: Digraph,
    dependencies: list[Dependant],
) -> None:
    visisted: set[CacheKey] = set()
    queue: list[Dependant] = [*dependencies]

    while len(queue) > 0:
        dependency = queue.pop(0)

        cache_key = dependency.cache_key
        if cache_key in visisted:
            continue

        visisted.add(cache_key)

        parent_name = get_dependency_name(dependency)
        dot.node(parent_name)

        for sub_dependency in dependency.dependencies:
            child_name = get_dependency_name(sub_dependency)
            dot.node(child_name)
            dot.edge(parent_name, child_name)

            queue.append(sub_dependency)
