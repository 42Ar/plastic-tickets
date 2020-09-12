from typing import List

from django.db import models
from django.utils.translation import gettext
from plastic_wiki.models import DescribedOption, Options


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
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    color = models.ForeignKey(MaterialColor, on_delete=models.CASCADE)


class MaterialColorOption:
    def __init__(self, option: DescribedOption):
        self.option = option

    def to_json(self):
        return {'name': self.option.display_name,
                'description': self.option.description}

    def __eq__(self, other):
        return self.option == other.option


class MaterialTypeOption:
    def __init__(self, option: DescribedOption):
        self.option = option
        self.material_colors: List[MaterialColorOption] = []

    def to_json(self):
        return {'name': self.option.display_name,
                'description': self.option.description,
                'material_colors': self.material_colors}


class ProductionMethodOption:
    def __init__(self, option: DescribedOption):
        self.option = option
        self.material_types: List[MaterialTypeOption] = []

    def to_json(self):
        return {'name': self.option.display_name,
                'description': self.option.description,
                'material_types': self.material_types}


def get_option_tree() -> List[ProductionMethodOption]:
    pm_descriptions = Options.get_production_methods()
    mt_descriptions = Options.get_material_types()
    mc_descriptions = Options.get_material_colors()

    production_methods: List[ProductionMethodOption] = []

    for production_method in ProductionMethod.objects.all():
        desc = next(
            (d for d in pm_descriptions if
             production_method.name.lower() == d.name),
            DescribedOption.get_placeholder(production_method.name))
        pm = ProductionMethodOption(desc)
        production_methods.append(pm)

        for material_type in production_method.materialtype_set.all():
            desc = next(
                (d for d in mt_descriptions if
                 material_type.name.lower() == d.name),
                DescribedOption.get_placeholder(material_type.name))
            mt = MaterialTypeOption(desc)
            pm.material_types.append(mt)

            for material in material_type.material_set.all():
                desc = next(
                    (d for d in mc_descriptions if
                     material.color.name.lower() == d.name),
                    DescribedOption.get_placeholder(material.color.name))
                color = MaterialColorOption(desc)
                if color in mt.material_colors:
                    continue
                mt.material_colors.append(color)
            if len(mt.material_colors) == 0:
                pm.material_types.pop()
        if len(pm.material_types) == 0:
            production_methods.pop()

    return production_methods
