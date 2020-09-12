from pathlib import Path
from typing import List, Dict

import markdown
from django.conf import settings
from django.db import models
from django.utils.translation import get_language, gettext

WIKI_PATH = settings.PLASTIC_TICKETS_STATIC_PATH.joinpath('wiki/')


class MarkdownDescription:
    def __init__(self, markdown_content: str):
        self.markdown_content = markdown_content

    def get_summary(self) -> str:
        summary = ''
        for line in self.markdown_content.splitlines():
            if line == '':
                break
            summary += line

        return markdown.markdown(summary)

    def get_as_html(self) -> str:
        # TODO: Cache html
        return markdown.markdown(self.markdown_content)

    def to_json(self):
        return self.get_summary()

    PLACEHOLDER = None

    @classmethod
    def get_placeholder(cls):
        if cls.PLACEHOLDER is None:
            cls.PLACEHOLDER = MarkdownDescription(
                f'*{gettext("not available")}*'
            )
        return cls.PLACEHOLDER

    def __str__(self):
        return self.get_as_html()


class DescribedOption:
    """A named option and its description"""

    def __init__(self, name: str, description: MarkdownDescription):
        """
        Initialize a print type using its description
        """
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

    def to_json(self):
        return {'name': self.name, 'description': self.description}

    def __eq__(self, other):
        return self.name == other.name

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

            name = name.upper()

            if lang not in options:
                options[lang] = []

            options[lang].append(
                DescribedOption(name, MarkdownDescription(file.read_text())))

        # Also always include english options,
        # where no translations is available
        for opt in options['en']:
            for lang in options.keys():
                if opt not in options[lang]:
                    options[lang].append(opt)

        return options


class Options:
    PRODUCTION_METHODS = DescribedOption.load_options_from_path(
        WIKI_PATH.joinpath('production-methods/'))
    MATERIAL_TYPES = DescribedOption.load_options_from_path(
        WIKI_PATH.joinpath('material-types/'))

    @staticmethod
    def get_for_current_language(opt: Dict[str, List[DescribedOption]]):
        lang = get_language()
        if lang in opt:
            return opt[lang]
        return opt['en']

    @classmethod
    def get_material_types(cls) -> List[DescribedOption]:
        return Options.get_for_current_language(cls.MATERIAL_TYPES)

    @classmethod
    def get_production_methods(cls) -> List[DescribedOption]:
        return Options.get_for_current_language(cls.PRODUCTION_METHODS)


class ProductionMethod(models.Model):
    name = models.TextField()

    def __str__(self) -> str:
        return self.name


class MaterialType(models.Model):
    production_type = models.ForeignKey(ProductionMethod,
                                        on_delete=models.CASCADE)
    name = models.TextField()

    def __str__(self) -> str:
        return self.name


class MaterialColor(models.Model):
    """A material color with its display name"""
    name = models.TextField()
    color = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Material(models.Model):
    """A physical material that is/was in Stock"""
    color = models.ForeignKey(MaterialColor, on_delete=models.CASCADE)
    type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    name = models.TextField()
    url = models.URLField()
    optimal_temp = models.FloatField()
    min_temp = models.FloatField()
    max_temp = models.FloatField()

    def __str__(self) -> str:
        return self.name


class MaterialStock(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    label = models.PositiveIntegerField(
        help_text=gettext('The internal label to identify the material'),
        unique=True)
    consumed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.label} ({self.material})'


class PrintConfig(models.Model):
    file = models.FilePathField()
    count = models.PositiveIntegerField()
    material = Material()


class MaterialColorOption:
    def __init__(self, option: DescribedOption):
        self.option = option

    def to_json(self):
        return {'name': self.option.name,
                'description': self.option.description}


class MaterialTypeOption:
    def __init__(self, option: DescribedOption):
        self.option = option
        self.material_colors = []

    def to_json(self):
        return {'name': self.option.name,
                'description': self.option.description,
                'material_colors': self.material_colors}


class ProductionMethodOption:
    def __init__(self, option: DescribedOption):
        self.option = option
        self.material_types = []

    def to_json(self):
        return {'name': self.option.name,
                'description': self.option.description,
                'material_types': self.material_types}


def get_option_tree() -> List[ProductionMethodOption]:
    pm_descriptions = Options.get_production_methods()
    mt_descriptions = Options.get_material_types()

    production_methods: List[ProductionMethodOption] = []

    for production_method in ProductionMethod.objects.all():
        desc = next(
            (p for p in pm_descriptions if production_method.name == p.name),
            DescribedOption(production_method.name,
                            MarkdownDescription.get_placeholder()))
        pm = ProductionMethodOption(desc)
        production_methods.append(pm)

        for material_type in production_method.materialtype_set.all():
            desc = next(
                (d for d in mt_descriptions if material_type.name == d.name),
                DescribedOption(material_type.name,
                                MarkdownDescription.get_placeholder()))
            mt = MaterialTypeOption(desc)
            pm.material_types.append(mt)
        if len(pm.material_types) == 0:
            production_methods.pop()

    return production_methods
