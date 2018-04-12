from pathlib import Path

from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse


def get_tasks_log(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return HttpResponseRedirect("/admin/login/?next=" + reverse("tasks-log"))
    with (Path(__file__) / ".." / ".." / "tasks.log").resolve().open() as f:
        text = f.read()
    return HttpResponse(text, content_type="text/plain")
