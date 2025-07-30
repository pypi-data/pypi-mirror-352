from unittest.mock import MagicMock

from kit.tree_sitter_symbol_extractor import TreeSitterSymbolExtractor


class TestSymbolTypeProcessing:
    """Tests for symbol type processing to ensure correct prefix removal."""

    def test_symbol_type_from_fallback_label_function(self):
        """Test that @function correctly becomes 'function' and not 'unction'."""
        # Mock the necessary components
        mock_query = MagicMock()
        mock_parser = MagicMock()
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_node = MagicMock()

        # Set up the mock node
        mock_node.text = b"testFunction"
        mock_node.start_point = (10, 0)
        mock_node.end_point = (15, 0)
        mock_node.start_byte = 100
        mock_node.end_byte = 200

        # Set up the captures that would trigger the fallback path
        captures = {"@function": mock_node}
        matches = [(0, captures)]

        mock_query.matches.return_value = matches
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root

        # Mock the class methods
        TreeSitterSymbolExtractor.get_query = MagicMock(return_value=mock_query)
        TreeSitterSymbolExtractor.get_parser = MagicMock(return_value=mock_parser)

        source_code = "def testFunction():\n    pass"

        # Call the method
        symbols = TreeSitterSymbolExtractor.extract_symbols(".py", source_code)

        # Verify the result
        assert len(symbols) == 1
        assert symbols[0]["type"] == "function"  # Should be "function", not "unction"
        assert symbols[0]["name"] == "testFunction"

    def test_symbol_type_from_fallback_label_class(self):
        """Test that @class correctly becomes 'class'."""
        # Mock similar to above but with @class
        mock_query = MagicMock()
        mock_parser = MagicMock()
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_node = MagicMock()

        mock_node.text = b"TestClass"
        mock_node.start_point = (5, 0)
        mock_node.end_point = (10, 0)
        mock_node.start_byte = 50
        mock_node.end_byte = 150

        captures = {"@class": mock_node}
        matches = [(0, captures)]

        mock_query.matches.return_value = matches
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root

        TreeSitterSymbolExtractor.get_query = MagicMock(return_value=mock_query)
        TreeSitterSymbolExtractor.get_parser = MagicMock(return_value=mock_parser)

        source_code = "class TestClass:\n    pass"

        symbols = TreeSitterSymbolExtractor.extract_symbols(".py", source_code)

        assert len(symbols) == 1
        assert symbols[0]["type"] == "class"
        assert symbols[0]["name"] == "TestClass"

    def test_symbol_type_from_definition_capture(self):
        """Test that definition.function correctly becomes 'function'."""
        mock_query = MagicMock()
        mock_parser = MagicMock()
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_name_node = MagicMock()
        mock_def_node = MagicMock()

        mock_name_node.text = b"myFunction"
        mock_name_node.start_point = (3, 0)
        mock_name_node.end_point = (3, 10)

        mock_def_node.text = b"def myFunction():\n    return 42"
        mock_def_node.start_point = (3, 0)
        mock_def_node.end_point = (4, 14)
        mock_def_node.start_byte = 30
        mock_def_node.end_byte = 65

        captures = {"name": mock_name_node, "definition.function": mock_def_node}
        matches = [(0, captures)]

        mock_query.matches.return_value = matches
        mock_parser.parse.return_value = mock_tree
        mock_tree.root_node = mock_root

        TreeSitterSymbolExtractor.get_query = MagicMock(return_value=mock_query)
        TreeSitterSymbolExtractor.get_parser = MagicMock(return_value=mock_parser)

        source_code = "def myFunction():\n    return 42"

        symbols = TreeSitterSymbolExtractor.extract_symbols(".py", source_code)

        assert len(symbols) == 1
        assert symbols[0]["type"] == "function"  # Should correctly extract "function" from "definition.function"
        assert symbols[0]["name"] == "myFunction"

    def test_removeprefix_behavior_verification(self):
        """Test that our fix correctly handles the prefix removal."""
        # Test the specific case that was failing
        test_label = "@function"

        # Old buggy behavior would be:
        # "@function".lstrip("definition.") -> "@unction" (removes 'f')
        # "@unction".lstrip("@") -> "unction"

        # New correct behavior:
        result = test_label.removeprefix("definition.").removeprefix("@")
        assert result == "function"

        # Test with definition.function
        test_label2 = "definition.function"
        result2 = test_label2.removeprefix("definition.").removeprefix("@")
        assert result2 == "function"

        # Test edge case where definition. is not at start
        test_label3 = "not_definition.function"
        result3 = test_label3.removeprefix("definition.").removeprefix("@")
        assert result3 == "not_definition.function"  # Should remain unchanged
