from matplotlib_sankey._colors import is_color, is_colormap, colormap_to_list, is_hex_color, unify_color


def test_color_utils() -> None:
    """Testing color utils."""
    assert all(
        [
            is_color("blue"),
            is_color("tab:red"),
            is_color("#3456ad"),
            is_color([1, 0.4, 0.2]),
            is_color([255, 60, 60]),
        ]
    )

    assert is_hex_color("#345") is False
    assert is_hex_color("test") is False
    assert is_hex_color([255, 60, 60]) is False

    assert unify_color("#FFFFFF") == (1, 1, 1)

    assert is_colormap("tab10")
    assert is_colormap("blue") is False

    assert len(colormap_to_list("Reds", 20)) == 20
