from app.schemas.leaderboard import LeaderboardEntry


def test_leaderboard_entry_shape() -> None:
    entry = LeaderboardEntry(rank=1, name="Aditi", problems_solved=42, score=900)
    assert entry.rank == 1
    assert entry.name == "Aditi"
    assert entry.problems_solved == 42
    assert entry.score == 900
