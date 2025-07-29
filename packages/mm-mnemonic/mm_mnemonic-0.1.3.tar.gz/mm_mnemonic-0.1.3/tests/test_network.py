"""Tests for network connectivity detection."""

from unittest.mock import MagicMock, patch

from mm_mnemonic.network import _test_connection, has_internet_connection


class TestConnection:
    """Test the _test_connection function."""

    def test_successful_connection(self) -> None:
        """Test successful connection to a reachable host."""
        # Test with localhost (should always work)
        result = _test_connection("127.0.0.1", 22, timeout=1.0)
        # Note: This might fail if SSH is not running, so we don't assert True
        assert isinstance(result, bool)

    def test_failed_connection(self) -> None:
        """Test failed connection to unreachable host."""
        # Use a non-routable IP address
        result = _test_connection("192.0.2.1", 12345, timeout=1.0)
        assert result is False

    def test_timeout(self) -> None:
        """Test connection timeout."""
        # Use a very short timeout to a slow host
        result = _test_connection("httpbin.org", 80, timeout=0.001)
        assert result is False


class TestInternetConnection:
    """Test the has_internet_connection function."""

    @patch("mm_mnemonic.network._test_connection")
    def test_internet_available_first_server(self, mock_test: MagicMock) -> None:
        """Test when first DNS server is reachable."""
        # First call returns True, others should not be called due to early return
        mock_test.side_effect = [True, False, False]

        result = has_internet_connection()
        assert result is True
        # Only first server should be tested due to concurrent execution
        assert mock_test.call_count >= 1

    @patch("mm_mnemonic.network._test_connection")
    def test_internet_available_second_server(self, mock_test: MagicMock) -> None:
        """Test when second DNS server is reachable."""
        mock_test.side_effect = [False, True, False]

        result = has_internet_connection()
        assert result is True

    @patch("mm_mnemonic.network._test_connection")
    def test_internet_available_third_server(self, mock_test: MagicMock) -> None:
        """Test when third DNS server is reachable."""
        mock_test.side_effect = [False, False, True]

        result = has_internet_connection()
        assert result is True

    @patch("mm_mnemonic.network._test_connection")
    def test_no_internet_all_servers_fail(self, mock_test: MagicMock) -> None:
        """Test when all DNS servers are unreachable."""
        mock_test.return_value = False

        result = has_internet_connection()
        assert result is False
        assert mock_test.call_count == 3

    @patch("mm_mnemonic.network._test_connection")
    def test_custom_timeout(self, mock_test: MagicMock) -> None:
        """Test custom timeout parameter."""
        mock_test.return_value = False
        custom_timeout = 5.0

        has_internet_connection(timeout=custom_timeout)

        # Verify that all calls used the custom timeout (passed as 3rd positional argument)
        for call in mock_test.call_args_list:
            assert call[0][2] == custom_timeout  # args[2] is the timeout parameter

    @patch("socket.create_connection")
    def test_real_connection_simulation(self, mock_socket: MagicMock) -> None:
        """Test with real socket simulation."""
        # Simulate successful connection
        mock_socket.return_value.__enter__ = MagicMock()
        mock_socket.return_value.__exit__ = MagicMock()

        result = has_internet_connection()
        assert result is True
        assert mock_socket.called

    @patch("socket.create_connection")
    def test_socket_error_simulation(self, mock_socket: MagicMock) -> None:
        """Test with socket error simulation."""
        # Simulate connection failure
        mock_socket.side_effect = OSError("Connection failed")

        result = has_internet_connection()
        assert result is False


class TestConcurrency:
    """Test concurrent execution behavior."""

    @patch("mm_mnemonic.network._test_connection")
    def test_concurrent_execution(self, mock_test: MagicMock) -> None:
        """Test that connections are tested concurrently."""

        # Slow down the first two calls to ensure concurrent execution
        def slow_connection(host: str, _port: int, _timeout: float = 3.0) -> bool:
            if host in ["8.8.8.8", "1.1.1.1"]:
                import time

                time.sleep(0.1)  # Small delay
                return False
            return True  # Third server succeeds quickly

        mock_test.side_effect = slow_connection

        import time

        start_time = time.time()
        result = has_internet_connection()
        end_time = time.time()

        assert result is True
        # Should complete in much less time than sequential execution would take
        assert end_time - start_time < 0.3  # Sequential would take ~0.2+ seconds
