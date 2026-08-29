import pandas as pd

from misinformation.compare_baselines import run_comparison, select_winner


def test_select_winner_big_margin_challenger_wins():
    scores = {"logistic_regression": 0.90, "random_forest": 0.94, "svm_linear": 0.80}
    assert select_winner(scores, margin=0.01) == "random_forest"


def test_select_winner_within_margin_keeps_logreg():
    scores = {"logistic_regression": 0.90, "random_forest": 0.905, "svm_linear": 0.895}
    assert select_winner(scores, margin=0.01) == "logistic_regression"


def _synthetic_df(n_per_class: int = 40, hard: bool = False) -> pd.DataFrame:
    """Small, fast, obviously-separable-by-vocabulary synthetic dataset --
    NOT the real 894-row IFND subset -- used only to exercise the pipeline
    and selection logic quickly in tests."""
    true_rows = [f"real flood rescue update number {i} confirmed by officials" for i in range(n_per_class)]
    fake_rows = [f"fabricated hoax rumor number {i} debunked completely" for i in range(n_per_class)]
    texts = true_rows + fake_rows
    labels = [1] * n_per_class + [0] * n_per_class
    return pd.DataFrame({"Statement": texts, "y": labels})


def test_all_three_models_produce_metrics():
    summary, results, _ = run_comparison(_synthetic_df())
    assert set(summary["models"].keys()) == {"logistic_regression", "random_forest", "svm_linear"}
    for name, metrics in summary["models"].items():
        assert 0.0 <= metrics["macro_f1"] <= 1.0
        assert len(metrics["confusion_matrix"]) == 2


def test_selection_stays_with_logreg_when_no_challenger_clears_margin():
    summary, _, _ = run_comparison(_synthetic_df())
    # on this easy, well-separated synthetic set all three should score
    # very close to perfect, so no challenger should clear the margin
    assert summary["winner"] == "logistic_regression"
    assert summary["margin_over_logreg"] == 0.0
