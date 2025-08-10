from django.db import migrations

def gen_unique_slug(apps, schema_editor):
    Shop = apps.get_model('booking', 'Shop')
    from django.utils.text import slugify

    existing = set(
        s.slug for s in Shop.objects.exclude(slug__isnull=True).exclude(slug__exact='')
    )

    for s in Shop.objects.all():
        if s.slug:
            continue
        base = slugify(s.name, allow_unicode=True) or "shop"
        slug = base
        i = 2
        # ensure uniqueness both in DB and in-memory batch
        while Shop.objects.filter(slug=slug).exclude(pk=s.pk).exists() or slug in existing:
            slug = f"{base}-{i}"
            i += 1
        s.slug = slug
        s.save(update_fields=['slug'])
        existing.add(slug)

class Migration(migrations.Migration):
    dependencies = [
        ('booking', '0017_shop_slug'),
    ]
    operations = [
        migrations.RunPython(gen_unique_slug, migrations.RunPython.noop),
    ]
