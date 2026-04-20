import pandas as pd


def test_target_columns_exist():
    df = pd.DataFrame({"finish_position": [1, 2, 6]})
    df["is_winner"] = (df["finish_position"] == 1).astype(int)
    df["is_top3"] = (df["finish_position"] <= 3).astype(int)

    assert "is_winner" in df.columns
    assert "is_top3" in df.columns
    assert df["is_winner"].sum() == 1
    assert df["is_top3"].sum() == 2
