"""Cache invalidation: when data changes, drop the cached summary so it is never stale.

The slide warns: "If student records change, the cached count can become stale for up to
five minutes. Production applications should consider cache invalidation".  This is it.
(The per-view cache on /api/departments/ is NOT invalidated on purpose - see README.)
"""
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .cache_keys import SUMMARY_KEY
from .models import Department, Student


@receiver([post_save, post_delete], sender=Student)
@receiver([post_save, post_delete], sender=Department)
def clear_summary_cache(sender, **kwargs):
    cache.delete(SUMMARY_KEY)


@receiver(m2m_changed, sender=Student.courses.through)
def clear_summary_on_enrolment(sender, **kwargs):
    cache.delete(SUMMARY_KEY)
