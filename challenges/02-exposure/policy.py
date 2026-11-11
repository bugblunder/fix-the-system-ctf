"""Participant edit surface: decide what can be downloaded."""


def resolve_public(site, name):
    target = (site / name).resolve()
    if not target.is_relative_to(site.resolve()):
        return None
    return target if target.is_file() else None
