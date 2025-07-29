from django import template


register = template.Library()

@register.filter(name="duration")   
def duration(td):
    if td is None:
        return ""
    
    total_seconds = int(td.total_seconds())
    hours, minutes = divmod(total_seconds // 60, 60)
    
    if hours and minutes:
        return f"{hours} h {minutes} min"
    if hours:
        return f"{hours} h"
    return f"{minutes} min"