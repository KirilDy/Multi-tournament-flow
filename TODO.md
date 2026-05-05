# Registration logic + UI fixes

**Requirements:**
1. Registration available ONLY during registration_start to registration_end (strict time check)
2. Rename "Telegram / Discord" to "Контакти" and make optional (remove required)

**Registration logic implemented:**

1. ✅ teams/forms.py: Strict time check ONLY registration_start-end, detailed error with dates
2. ✅ teams/templates/teams/team_create.html: "Контакти (Telegram/Discord)" optional field + hint
3. ✅ tournaments/templates/tournaments/tournament_detail.html: Button hidden if !is_registration_open + time display

Registration now STRICTLY time-based. Test by setting tournament dates.
