"""Reference policy: only canonical paths inside the public tree are downloadable."""


def resolve_public(site, name):
    public = (site / "public").resolve()
    target = (site / name).resolve()
    if not target.is_relative_to(public):
        return None
    return target if target.is_file() else None
