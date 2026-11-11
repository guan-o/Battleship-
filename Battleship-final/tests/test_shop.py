"""Tests for shop.py: cash, purchases, power-ups and the radar area."""

from shop import (
    SHOP_ITEMS,
    apply_power_up,
    can_afford,
    find_item,
    get_cash,
    get_shop_items,
    new_player_wallet,
    purchase_item,
    radar_area,
    use_extra_shot,
    use_radar_charge,
)


def test_new_wallet_starts_with_starting_cash():
    player = new_player_wallet()
    assert get_cash(player) > 0


def test_find_item_accepts_name_and_number():
    names = list(SHOP_ITEMS)
    assert find_item("1") == names[0]
    assert find_item(names[0]) == names[0]
    assert find_item(names[0].upper()) == names[0]


def test_find_item_rejects_unknown_choices():
    for bad in ["", "99", "0", "laser", None]:
        assert find_item(bad) is None


def test_purchase_deducts_the_price():
    player = new_player_wallet(100)
    item = list(SHOP_ITEMS)[0]
    price = SHOP_ITEMS[item]["price"]

    success, message = purchase_item(player, item)

    assert success is True
    assert get_cash(player) == 100 - price
    assert "Bought" in message


def test_purchase_fails_without_enough_cash():
    player = new_player_wallet(0)
    item = list(SHOP_ITEMS)[0]

    success, message = purchase_item(player, item)

    assert success is False
    assert get_cash(player) == 0            # cash must not change
    assert "Not enough cash" in message


def test_can_afford_boundary():
    item = list(SHOP_ITEMS)[0]
    price = SHOP_ITEMS[item]["price"]
    assert can_afford({"cash": price}, item) is True
    assert can_afford({"cash": price - 1}, item) is False
    assert can_afford({"cash": 999}, "not an item") is False


def test_apply_power_up_records_the_charge():
    state = {}
    apply_power_up("radar", state)
    assert state["radar_charges"] == 1
    apply_power_up("extra strike", state)
    assert state["extra_shots"] == 1


def test_charges_are_spent_once():
    state = {"extra_shots": 1, "radar_charges": 1}
    assert use_extra_shot(state) is True
    assert use_extra_shot(state) is False       # nothing left
    assert state["extra_shots"] == 0

    assert use_radar_charge(state) is True
    assert use_radar_charge(state) is False


def test_radar_area_is_3x3_in_open_water():
    assert len(radar_area(5, 5)) == 9


def test_radar_area_is_clipped_at_the_corner():
    area = radar_area(0, 0)
    assert len(area) == 4                        # 2x2 in the corner
    assert all(0 <= r < 10 and 0 <= c < 10 for r, c in area)


def test_shop_items_exposes_prices_only():
    items = get_shop_items()
    assert items and all(isinstance(price, int) for price in items.values())
