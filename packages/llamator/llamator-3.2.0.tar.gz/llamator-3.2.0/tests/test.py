import pandas as pd

class AttackPrep:
    def __init__(self, num_attempts: int):
        self.num_attempts = num_attempts

    def _prepare_attack_dataset(self, dataset: pd.DataFrame) -> pd.DataFrame:
        rows = dataset.shape[0]

        if rows == 0:
            return dataset
        elif self.num_attempts > rows:
            repeats = -(-self.num_attempts // rows)  # ceil
            return (
                pd.concat([dataset] * repeats)
                  .head(self.num_attempts)
                  .sort_index()
                  .reset_index(drop=True)
            )
        else:
            return dataset.head(self.num_attempts).reset_index(drop=True)


def make_df(n: int) -> pd.DataFrame:
    return pd.DataFrame({"val": range(n)})


def run_tests() -> None:
    cases = [
        # label, num_attempts, df_size, expected vals
        ("empty",        4, 0, []),
        ("equal_rows",   3, 3, [0, 1, 2]),
        ("trim_head",    2, 5, [0, 1]),
        ("repeat_short", 5, 3, [0, 0, 1, 1, 2]),
        ("exact_repeat", 6, 3, [0, 0, 1, 1, 2, 2]),
    ]

    for label, attempts, df_size, exp in cases:
        out = AttackPrep(attempts)._prepare_attack_dataset(make_df(df_size))
        assert out["val"].tolist() == exp, f"{label} failed"
        print(f"{label}: OK")


if __name__ == "__main__":
    run_tests()