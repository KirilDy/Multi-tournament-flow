import django.contrib.auth.decorators
import django.contrib.auth.mixins
import django.views.generic
import django.shortcuts


def is_jury(user):
    return user.is_authenticated and user.role == 'JURY'

# Використання у views.py
@django.contrib.auth.decorators.user_passes_test(is_jury, login_url='login')
def jury_dashboard(request):
    return django.shortcuts.render(request, 'jury/dashboard.html')



class JuryTaskListView(django.contrib.auth.mixins.UserPassesTestMixin, django.views.generic.ListView):
    #model = Task
    template_name = 'jury/tasks.html'

    def test_func(self):
        # Повертає True, якщо доступ дозволено
        return self.request.user.role == 'JURY'