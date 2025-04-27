from main.models import CustomUser, Election
from django.contrib.auth.models import Group

# Fetch groups
state_candidates_group = Group.objects.get(name="StateCandidates")
central_candidates_group = Group.objects.get(name="CentralElection")

# Fetch candidates belonging to the respective groups
state_candidates = CustomUser.objects.filter(groups=state_candidates_group)
central_candidates = CustomUser.objects.filter(groups=central_candidates_group)

# Create State Election
state_election = Election.objects.create(
    name="State Election 2025",
    description="Election for state-level representatives.",
    start_date="2025-05-01 09:00:00",
    end_date="2025-05-01 17:00:00"
)
state_election.candidates.set(state_candidates)  # Assign state candidates to the election

# Create Central Election
central_election = Election.objects.create(
    name="Central Election 2025",
    description="Election for central-level representatives.",
    start_date="2025-06-01 09:00:00",
    end_date="2025-06-01 17:00:00"
)
central_election.candidates.set(central_candidates)  # Assign central candidates to the election

print(f"State Election '{state_election.name}' created with candidates: {[c.username for c in state_candidates]}")
print(f"Central Election '{central_election.name}' created with candidates: {[c.username for c in central_candidates]}")