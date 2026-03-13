# ----- POST /api/inventory/ -----


def test_given_valid_body_when_post_inventory_then_returns_202_with_id_and_identifier(client, mock_service):
    pass


def test_given_name_with_accents_when_post_inventory_then_creates_normalized_identifier(client, mock_service):
    pass


def test_given_missing_required_fields_when_post_inventory_then_returns_422(client, mock_service):
    pass


def test_given_invalid_types_when_post_inventory_then_returns_422(client, mock_service):
    pass


# ----- GET /api/inventory/ (list) -----


def test_given_items_in_inventory_when_get_list_then_returns_all_items(client, mock_service):
    pass


def test_given_order_by_and_direction_when_get_list_then_returns_sorted(client, mock_service):
    pass


def test_given_order_by_name_quantity_or_last_updated_when_get_list_then_accepts_and_applies(client, mock_service):
    pass


def test_given_no_query_params_when_get_list_then_orders_critical_first_then_last_updated_desc_then_name_asc(
    client, mock_service
):
    pass


# ----- GET /api/inventory/<id>/ -----


def test_given_existing_id_when_get_item_then_returns_item(client, mock_service):
    pass


def test_given_non_existing_id_when_get_item_then_returns_404(client, mock_service):
    pass


# ----- DELETE /api/inventory/<id>/ -----

def test_given_non_existing_id_when_delete_quantity_then_returns_404(client, mock_service):
    pass

def test_given_valid_quantity_when_delete_quantity_then_returns_200(client, mock_service):
    pass
