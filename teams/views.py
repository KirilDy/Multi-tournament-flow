from django.views.generic import ListView, DetailView, CreateView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.forms import formset_factory
from .models import Team, TeamMember
from .forms import TeamCreateForm, TeamMemberForm, get_team_member_formset
from tournaments.models import Tournament
from accounts.models import User








class TeamRoleMixin(LoginRequiredMixin):

    """Mixin для перевірки ролі TEAM"""
    def test_func(self):
        return self.request.user.role == User.Role.TEAM


class JuryRoleMixin(LoginRequiredMixin):
    """Mixin для перевірки ролі JURY"""
    def test_func(self):
        return self.request.user.role == User.Role.JURY


class TeamOrJuryRoleMixin(LoginRequiredMixin):
    """Mixin для перевірки ролі TEAM або JURY"""
    def test_func(self):
        return self.request.user.role in [User.Role.TEAM, User.Role.JURY]


class TeamCreateView(TeamRoleMixin, CreateView):
    """View для створення команди в турнірі"""
    model = Team
    form_class = TeamCreateForm
    template_name = 'teams/team_create.html'
    
    def get_success_url(self):
        return reverse('team_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament_pk = self.kwargs.get('tournament_pk')
        tournament = get_object_or_404(Tournament, pk=tournament_pk)
        context['tournament'] = tournament
        return context
    
    def dispatch(self, request, *args, **kwargs):
        tournament_pk = self.kwargs.get('tournament_pk')
        self.tournament = get_object_or_404(Tournament, pk=tournament_pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.tournament
        return kwargs
    
    def form_valid(self, form):
        form.instance.tournament = self.tournament
        form.instance.created_by = self.request.user
        messages.success(self.request, "Команду успішно створено!")

        # Додати творця команди одразу в список учасників
        response = super().form_valid(form)
        team = self.object

        # щоб уникнути дублювання на випадок повторних запитів
        if not team.members.filter(email=self.request.user.email).exists():
            TeamMember.objects.create(
                team=team,
                user=self.request.user,
                full_name=getattr(self.request.user, 'full_name', None) or self.request.user.username,
                email=self.request.user.email,
                is_captain=True,
            )

        return response

    
    def form_invalid(self, form):
        if form.non_field_errors():
            messages.error(self.request, f"Помилка: {' '.join(form.non_field_errors())}")
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{form.fields[field].label}: {error}")
            messages.error(self.request, '; '.join(errors))
        return super().form_invalid(form)


class TeamDetailView(LoginRequiredMixin, DetailView):
    """View для перегляду деталей команди"""
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        
        # Перевірка чи користувач є творцем команди
        context['is_creator'] = (team.created_by == self.request.user)
        
        # Перевірка чи користувач є журі
        context['is_jury'] = (self.request.user.role == User.Role.JURY)
        
        # Отримання списку учасників
        context['members'] = team.members.all()
        
        return context


class TeamLeaveView(LoginRequiredMixin, View):
    """Учасник може вийти з команди (видаляє свій запис TeamMember)."""

    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)

        # Забороняємо вихід капітану (і лише капітану)
        membership = TeamMember.objects.filter(team=team, user=request.user).first()
        if not membership:
            messages.error(request, "Ви не є учасником цієї команди.")
            return redirect('team_detail', pk=pk)

        if membership.is_captain:
            messages.error(request, "Капітан не може вийти з команди.")
            return redirect('team_detail', pk=pk)

        membership.delete()

        messages.success(request, "Ви вийшли з команди.")
        return redirect('tournament_teams', pk=team.tournament_id)


class TeamAddMemberView(LoginRequiredMixin, View):

    """View для додавання учасників в команду (тільки для творця)"""
    
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        
        # Перевірка чи користувач є творцем команди
        if team.created_by != request.user:
            messages.error(request, "Ви не можете додавати учасників у цю команду.")
            return redirect('team_detail', pk=pk)
        
        # Створення форми для нового учасника
        # Правило: перший доданий учасник команди має бути капітаном (і це має бути творець команди)
        initial = {}
        if not team.members.exists():
            # Перший учасник команди має бути капітаном
            initial['is_captain'] = True

            # Зафіксуємо, що email першого учасника = email творця (щоб точно з'явився капітан у списку)
            if team.created_by and getattr(team.created_by, 'email', None):
                initial['email'] = team.created_by.email


        form = TeamMemberForm(initial=initial)



        
        return render(request, 'teams/team_add_member.html', {
            'team': team,
            'form': form
        })

    def post(self, request, pk):

        team = get_object_or_404(Team, pk=pk)
        
        # Перевірка чи користувач є творцем команди
        if team.created_by != request.user:
            messages.error(request, "Ви не можете додавати учасників у цю команду.")
            return redirect('team_detail', pk=pk)
        
        # Правило: перший доданий учасник команди завжди є капітаном
        # (незалежно від того, що передав користувач у чекбоксі)
        is_first_member = not team.members.exists()
        if is_first_member:
            # Заблокуємо, що перший учасник точно капітан: змусимо is_captain=True навіть якщо в POST не було чекбокса
            form = TeamMemberForm(request.POST)
            form.initial = {**(form.initial or {}), 'is_captain': True}
        else:
            form = TeamMemberForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Користувач з таким email не існує.")
                return render(request, 'teams/team_add_member.html', {
                    'team': team,
                    'form': form,
                })

            member = form.save(commit=False)
            member.team = team
            member.user = user

            # Підтягуємо full_name з User
            member.full_name = getattr(user, 'full_name', None) or user.username

            # Жорстко гарантуємо капітанство для першого учасника
            if is_first_member:
                member.is_captain = True

            try:
                member.save()

                messages.success(request, "Учасника успішно додано!")
            except Exception as e:
                messages.error(request, f"Помилка при додаванні учасника: {e}")
                return redirect('team_add_member', pk=pk)

            return redirect('team_detail', pk=pk)
        
        return render(request, 'teams/team_add_member.html', {
            'team': team,
            'form': form
        })


class JuryTeamListView(JuryRoleMixin, ListView):
    """View для журі - перегляд всіх команд турніру"""
    model = Team
    template_name = 'teams/jury_team_list.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        tournament_pk = self.kwargs.get('tournament_pk')
        return Team.objects.filter(tournament_id=tournament_pk).select_related('created_by').prefetch_related('members')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament_pk = self.kwargs.get('tournament_pk')
        tournament = get_object_or_404(Tournament, pk=tournament_pk)
        context['tournament'] = tournament
        return context


class JuryTournamentListView(JuryRoleMixin, ListView):
    """View для журі - перегляд списку турнірів"""
    model = Tournament
    template_name = 'teams/jury_tournament_list.html'
    context_object_name = 'tournaments'
    
    def get_queryset(self):
        return Tournament.objects.all().order_by('-created_at')


class JuryPeopleListView(JuryRoleMixin, ListView):
    """View для журі: список користувачів з роллю JURY"""
    model = User
    template_name = 'teams/jury_people_list.html'
    context_object_name = 'juries'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.JURY).order_by('id')



class TournamentTeamsView(JuryRoleMixin, ListView):
    """View для перегляду команд конкретного турніру (тільки ADMIN/JURY)"""
    model = Team
    template_name = 'teams/tournament_teams.html'
    context_object_name = 'teams'

    def get_queryset(self):
        tournament_pk = self.kwargs.get('pk')
        return (
            Team.objects.filter(tournament_id=tournament_pk)
            .select_related('created_by')
            .prefetch_related('members')
        )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament_pk = self.kwargs.get('pk')
        tournament = get_object_or_404(Tournament, pk=tournament_pk)
        context['tournament'] = tournament
        return context


