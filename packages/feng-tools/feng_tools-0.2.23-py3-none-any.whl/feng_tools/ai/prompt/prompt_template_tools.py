import os.path
from string import Template
from typing import Any


def create_template(template_file: str, encoding="utf8") -> Template:
    """创建Template"""
    with open(template_file, encoding=encoding) as f:
        return Template(f.read())


def read_template(template_file: str, data_dict:dict[str, Any]=None, encoding="utf8") -> str:
    """读取模板内容"""
    context_dict = {}
    template = create_template(template_file, encoding)
    if data_dict:
        context_dict.update(data_dict)
    return template.safe_substitute(context_dict)


if __name__ == '__main__':
    from config.default_settings import SCR_PATH

    prompt_file = os.path.join(SCR_PATH, "core", 'text_split', 'user_prompt.txt')
    content = read_template(prompt_file, data_dict={'novel_content':'这是一部分小说内容'})
    print(content)
