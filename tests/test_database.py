from database import ScoreDB


def test_database_starts_empty(tmp_path):
    db = ScoreDB(tmp_path / "test_scores.db")
    assert db.top_scores() == []
    db.close()


def test_add_and_sort_scores(tmp_path):
    db = ScoreDB(tmp_path / "test_scores.db")
    db.add_score("LOW", 100, 1)
    db.add_score("HIGH", 500, 3)
    db.add_score("MID", 300, 2)

    assert db.top_scores() == [
        ("HIGH", 500, 3),
        ("MID", 300, 2),
        ("LOW", 100, 1),
    ]
    db.close()


def test_delete_score_by_leaderboard_index(tmp_path):
    db = ScoreDB(tmp_path / "test_scores.db")
    db.add_score("FIRST", 900, 5)
    db.add_score("SECOND", 500, 3)
    db.delete_score_at(0)

    assert db.top_scores() == [("SECOND", 500, 3)]
    db.close()


def test_clear_scores(tmp_path):
    db = ScoreDB(tmp_path / "test_scores.db")
    db.add_score("PILOT", 250, 2)
    db.clear_scores()
    assert db.top_scores() == []
    db.close()
