from pathlib import Path
from typing import List, Dict

import markdown
from django.conf import settings
from django.utils.translation import gettext, get_language


class MarkdownDescription:
    def __init__(self, markdown_content: str):
        self.markdown_content = markdown_content

    def __str__(self):
        return self.get_as_html()

    def get_as_html(self) -> str:
        # TODO: Cache html
        return markdown.markdown(self.markdown_content)

    def to_json(self):
        return str(self)

    PLACEHOLDER = None

    @classmethod
    def get_placeholder(cls) -> 'MarkdownDescription':
        if cls.PLACEHOLDER is None:
            cls.PLACEHOLDER = MarkdownDescription(
                f'*{gettext("not available")}*'
            )
        return cls.PLACEHOLDER


class DescribedOption:
    """A named option and its description"""

    def __init__(self, name: str, display_name: str,
                 description: MarkdownDescription):
        """
        Initialize an option using its description
        """
        self.name = name
        self.display_name = display_name
        self.description = description

    def __str__(self) -> str:
        return self.display_name

    def to_json(self):
        return {'name': self.display_name, 'description': self.description}

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def get_placeholder(name: str) -> 'DescribedOption':
        return DescribedOption(name, name,
                               MarkdownDescription.get_placeholder())

    @staticmethod
    def make_option_from_file(file: Path, name: str) -> 'DescribedOption':
        lines = file.read_text().splitlines()

        # If the first line is a header, this will be the display name
        if len(lines) > 0 and lines[0].startswith('#'):
            display_name = lines.pop(0).replace('#', '').strip()
        else:
            display_name = name

        # Skip leading blank lines
        while len(lines) > 0 and lines[0].strip() == '':
            lines.pop(0)

        # The summary is the first paragraph
        summary = ''
        for line in lines:
            if line == '':
                break
            summary += line + '\n'

        if len(summary) > 0:
            return DescribedOption(name, display_name,
                                   MarkdownDescription(summary))
        return DescribedOption(name, display_name,
                               MarkdownDescription.get_placeholder())

    @staticmethod
    def load_options_from_path(path: Path) -> Dict[str,
                                                   List['DescribedOption']]:
        options = {'en': []}

        for file in path.glob('*.md'):
            split = file.name.replace('.md', '').split('_')

            if len(split) == 2:
                name = split[0]
                lang = split[1]
            elif len(split) == 1:
                name = split[0]
                lang = 'en'
            else:
                continue

            if lang not in options:
                options[lang] = []

            options[lang].append(
                DescribedOption.make_option_from_file(file, name))

        # Also always include english options,
        # where no translations is available
        for opt in options['en']:
            for lang in options.keys():
                if opt not in options[lang]:
                    options[lang].append(opt)

        return options


WIKI_PATH = settings.PLASTIC_WIKI_STATIC_PATH.joinpath('wiki/')


class Options:
    PRODUCTION_METHODS = DescribedOption.load_options_from_path(
        WIKI_PATH.joinpath('production-methods/'))
    MATERIAL_TYPES = DescribedOption.load_options_from_path(
        WIKI_PATH.joinpath('material-types/'))
    MATERIAL_COLORS = DescribedOption.load_options_from_path(
        WIKI_PATH.joinpath('colors/'))

    @staticmethod
    def get_for_current_language(opt: Dict[str, List[DescribedOption]]):
        lang = get_language()
        if lang in opt:
            return opt[lang]
        return opt['en']

    @classmethod
    def get_production_methods(cls) -> List[DescribedOption]:
        return Options.get_for_current_language(cls.PRODUCTION_METHODS)

    @classmethod
    def get_material_types(cls) -> List[DescribedOption]:
        return Options.get_for_current_language(cls.MATERIAL_TYPES)

    @classmethod
    def get_material_colors(cls) -> List[DescribedOption]:
        return Options.get_for_current_language(cls.MATERIAL_COLORS)
