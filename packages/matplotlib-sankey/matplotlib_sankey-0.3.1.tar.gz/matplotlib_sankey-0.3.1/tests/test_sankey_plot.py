import matplotlib.pyplot as plt
from matplotlib_sankey import sankey


def test_sankey_simple_plot():
    """Testing simple sankey plot."""
    data = [
        [(0, 2, 20), (0, 1, 10), (3, 4, 15), (3, 2, 10), (5, 1, 5), (5, 2, 50)],
        [(2, 6, 40), (1, 6, 15), (2, 7, 40), (4, 6, 15)],
        [(7, 8, 5), (7, 9, 5), (7, 10, 20), (7, 11, 10), (6, 11, 55), (6, 8, 15)],
    ]
    sankey(data, frameon=True)
    sankey(data, curve_type="curve3")
    sankey(data, curve_type="line")
    sankey(data, title="test", annotate_columns="index")
    sankey(data, color="Reds", annotate_columns="weight")
    sankey(data, color="tab:red", annotate_columns="weight_percent", annotate_columns_font_color="white")
    sankey(data, color=["tab:red", "Reds", (0.1, 0.4, 1.0), "viridis"])
    sankey(data, show_legend=True)
    sankey(data, color="tab:red", column_labels=["A", "B", "C", "D"], show=False)

    _, ax = plt.subplots()
    sankey(data, ax=ax)
