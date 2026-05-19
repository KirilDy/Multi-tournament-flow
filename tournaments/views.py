from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import TournamentForm, RoundForm, MustHaveCriteriaFormSet, RoundSubmissionForm
from .models import Tournament, Round, MustHaveCriteria, RoundSubmission
from django.views.generic import DeleteView


class RoundDetailView(LoginRequiredMixin, DetailView):
    model = Round
    template_name = 'tournaments/round_detail.html'
    context_object_name = 'round_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        round_obj = self.get_object()
        context['tournament'] = round_obj.tournament

        team = None
        if self.request.user.is_authenticated and self.request.user.role == 'TEAM':
            team = (
                round_obj.tournament.teams.filter(members__user=self.request.user).distinct().first()
            )
        context['my_team'] = team

        submission = None
        if team is not None:
            submission = RoundSubmission.objects.filter(round=round_obj, team=team).first()
        context['my_submission'] = submission
        return context


class RoundSubmissionCreateView(LoginRequiredMixin, View):
    def post(self, request, tournament_pk, pk):
        round_obj = get_object_or_404(Round, pk=pk, tournament_id=tournament_pk)

        if not (request.user.is_authenticated and request.user.role == 'TEAM'):
            return redirect('round_detail', tournament_pk=tournament_pk, pk=pk)

        team = (
            round_obj.tournament.teams.filter(members__user=request.user).distinct().first()
        )
        if team is None:
            return redirect('round_detail', tournament_pk=tournament_pk, pk=pk)

        form = RoundSubmissionForm(request.POST)
        if form.is_valid():
            submission, _ = RoundSubmission.objects.get_or_create(
                round=round_obj,
                team=team,
                defaults={'captain_user': request.user},
            )
            submission.captain_user = request.user
            submission.comment = form.cleaned_data['comment']
            submission.save()

        return redirect('round_detail', tournament_pk=tournament_pk, pk=pk)


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


class RoundCreateView(AdminRequiredMixin, CreateView):
    model = Round
    form_class = RoundForm
    template_name = 'tournaments/round_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.tournament = get_object_or_404(Tournament, pk=kwargs.get('tournament_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['tournament'] = self.tournament
        return initial

    def get_success_url(self):
        return reverse_lazy('tournament_detail', kwargs={'pk': self.tournament.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # при створенні Round instance ще не існує, тому формсет беремо без instance
            context['criteria_formset'] = MustHaveCriteriaFormSet(self.request.POST)
        else:
            context['criteria_formset'] = MustHaveCriteriaFormSet(instance=self.object)

        context['tournament'] = self.tournament
        return context

    def form_valid(self, form):
        form.instance.tournament = self.tournament
        context = self.get_context_data()
        criteria_formset = context['criteria_formset']

        if criteria_formset.is_valid():
            self.object = form.save()
            criteria_formset.instance = self.object
            criteria_formset.save()
            return redirect(self.get_success_url())

        return self.form_invalid(form)


class RoundEditView(AdminRequiredMixin, UpdateView):
    model = Round
    form_class = RoundForm
    template_name = 'tournaments/round_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['criteria_formset'] = MustHaveCriteriaFormSet(self.request.POST, instance=self.object)
        else:
            context['criteria_formset'] = MustHaveCriteriaFormSet(instance=self.object)
        context['tournament'] = self.object.tournament
        return context

    def get_success_url(self):
        return reverse_lazy('tournament_detail', kwargs={'pk': self.object.tournament.pk})

    def form_valid(self, form):
        context = self.get_context_data()
        criteria_formset = context['criteria_formset']

        if criteria_formset.is_valid():
            self.object = form.save()
            criteria_formset.instance = self.object
            criteria_formset.save()
            return redirect(self.get_success_url())

        return self.form_invalid(form)

