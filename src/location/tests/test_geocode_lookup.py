from location.geocode_lookup import get_coordinates


def test_city_hit_returns_city_precision():
    c = get_coordinates("Bengaluru", "Karnataka")
    assert c.precision == "city"
    assert c.latitude is not None and c.longitude is not None


def test_old_dataset_city_name_resolves_via_rename_alias():
    """Gazetteer matches store the OLD dataset name ('Bangalore'); the
    centroid CSV (built from current GeoNames data) uses 'Bengaluru'.
    Both must normalize to the same key."""
    c = get_coordinates("Bangalore", "Karnataka")
    assert c.precision == "city"


def test_unlisted_city_falls_back_to_state_without_raising():
    c = get_coordinates("Nonexistentcityxyz123", "Kerala")
    assert c.precision == "state"
    assert c.latitude is not None


def test_nothing_matches_returns_none_precision_without_raising():
    c = get_coordinates(None, None)
    assert c.precision == "none"
    assert c.latitude is None and c.longitude is None
