from django.db.models import Q

from .models import ResearchProject


def find_similar_topics(title):
    words = [word.strip() for word in title.lower().split() if len(word.strip()) > 3]
    query = Q()
    for word in words[:8]:
        query |= Q(title__icontains=word)
    if not query:
        return ResearchProject.objects.none()
    return ResearchProject.objects.filter(query)[:5]


def supervisor_has_conflict(supervisor, student):
    return supervisor.department and student.department and supervisor.department != student.department
