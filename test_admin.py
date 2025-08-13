import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
import pytest
from unittest.mock import patch, MagicMock

# Import the admin_menu from your module
from pharmacy_portal import admin_menu

def test_admin_menu_all_choices():
    # Simulate user inputs in order for each menu option 1 through 7
    inputs = iter(["1", "2", "3", "4", "5", "6", "7"])

    with patch("builtins.input", lambda _: next(inputs)), \
         patch("pharmacy_portal.view_products") as mock_view_products, \
         patch("pharmacy_portal.place_order") as mock_place_order, \
         patch("pharmacy_portal.view_orders") as mock_view_orders, \
         patch("pharmacy_portal.register") as mock_register, \
         patch("pharmacy_portal.add_new_product") as mock_add_new_product, \
         patch("pharmacy_portal.delete_product") as mock_delete_product, \
         patch("builtins.print") as mock_print:

        admin_menu()

        # Check that each function was called exactly once
        mock_view_products.assert_called_once()
        mock_place_order.assert_called_once_with(None)
        mock_view_orders.assert_called_once_with(admin=True)
        mock_register.assert_called_once()
        mock_add_new_product.assert_called_once()
        mock_delete_product.assert_called_once()

        # Check that "Logging out..." was printed once
        mock_print.assert_any_call("Logging out...")

def test_admin_menu_invalid_choice_then_logout():
    # Inputs: invalid choice first, then logout
    inputs = iter(["invalid", "7"])

    with patch("builtins.input", lambda _: next(inputs)), \
         patch("builtins.print") as mock_print:

        admin_menu()

        # Check that invalid choice message was printed
        mock_print.assert_any_call("Invalid choice 👎, try again.")

        # Check that logout message was printed
        mock_print.assert_any_call("Logging out...")
