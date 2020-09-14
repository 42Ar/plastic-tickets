from pathlib import Path

from django.contrib.auth.models import User
from django.forms import forms
from django.http import QueryDict

from . import models


def cache_config(active_file: Path, user: User, post: QueryDict):
    fc = post['file_count']
    pm = post['production_method']
    mt = post['material_type']
    mc = post['material_color']

    # Get DB objects for Options
    material_type = models.MaterialType.objects.filter(
        name__iexact=mt, production_method__name__iexact=pm).first()
    color = models.MaterialColor.objects.filter(name__iexact=mc).first()
    if material_type is None or color is None:
        return False
    # Check for existing cached config
    config = models.PrintConfig.objects.filter(
        file=active_file, cachedprintconfig__user=user).first()

    # Update existing config and return
    if config is not None:
        config.count = int(fc)
        config.material_type = material_type
        config.color = color
        config.save()
        return True

    # Create new cached config
    config = models.PrintConfig(file=active_file,
                                count=int(fc),
                                material_type=material_type,
                                color=color
                                )
    config.save()
    models.CachedPrintConfig(config=config, user=user).save()
    return True


class ConfigForm(forms.Form):
    production_method = models.ProductionMethod()
    material_type = models.MaterialType()
    material_color = models.MaterialColor()
