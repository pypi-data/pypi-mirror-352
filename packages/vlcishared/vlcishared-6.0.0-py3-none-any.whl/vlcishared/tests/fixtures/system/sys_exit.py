from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_sys_exit(monkeypatch):
    """
    Fixture que mockea la función sys.exit para evitar que termine el proceso durante la ejecución de tests.

    - Reemplaza sys.exit por un MagicMock, permitiendo verificar si fue llamado sin detener el test.

    Uso:
        def test_mi_funcion(mock_sys_exit):
            ...
            mock_sys_exit.assert_called_once_with(0)
    """
    mock_sys_exit = MagicMock()
    monkeypatch.setattr("sys.exit", mock_sys_exit)
    return mock_sys_exit
