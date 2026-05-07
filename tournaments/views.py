from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import TournamentForm
from .models import Tournament
from django.views.generic import DeleteView


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == self.request.user.Role.ADMIN


class TournamentListView(LoginRequiredMixin, ListView):
    model = Tournament
    template_name = 'tournaments/tournament_list.html'
    context_object_name = 'tournaments'

    def get_queryset(self):
        qs = Tournament.objects.all().order_by('-created_at')

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Tournament.Status.choices
        context['current_status'] = self.request.GET.get('status')
        return context


class TournamentDetailView(LoginRequiredMixin, DetailView):
    model = Tournament
    template_name = 'tournaments/tournament_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament = self.get_object()

        # Показуємо «Моя команда» лише якщо користувач входить у команду цього турніру
        if self.request.user.is_authenticated and self.request.user.role == 'TEAM':
            context['my_team'] = (
                tournament.teams.filter(members__user=self.request.user).distinct().first()
            )
        else:
            context['my_team'] = None

        return context




class TournamentCreateView(AdminRequiredMixin, CreateView):
    model = Tournament
    form_class = TournamentForm
    template_name = 'tournaments/tournament_form.html'
    success_url = reverse_lazy('tournament_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TournamentEditView(AdminRequiredMixin, UpdateView):
    model = Tournament
    form_class = TournamentForm
    template_name = 'tournaments/tournament_form.html'
    success_url = reverse_lazy('tournament_list')


class TournamentChangeStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)

        new_status = request.POST.get("status")

        if new_status in dict(Tournament.Status.choices):
            tournament.status = new_status
            tournament.save()

        return redirect('tournament_detail', pk=pk)

class TournamentDeleteView(AdminRequiredMixin, DeleteView):
    model = Tournament
    template_name = 'tournaments/tournament_confirm_delete.html'
    success_url = reverse_lazy('tournament_list')