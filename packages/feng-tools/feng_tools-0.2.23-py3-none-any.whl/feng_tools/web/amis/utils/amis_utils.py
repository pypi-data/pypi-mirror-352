from functools import lru_cache
from string import Template


@lru_cache()
def amis_templates(template_file: str, encoding="utf8") -> Template:
    """page template"""
    with open(template_file, encoding=encoding) as f:
        return Template(f.read())