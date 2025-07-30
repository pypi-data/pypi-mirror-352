from unittest.mock import MagicMock

import pytest

from vlcishared.flow.flow import SUCCESS_EXEC, FlowControl


@pytest.fixture
def mock_flow_control_patch(monkeypatch):
    """
    Fixture que mockea la clase FlowControl para evitar salidas abruptas durante tests.

    Características:
    - Mockea el método sys.exit dentro de FlowControl.
    - Requiere la ruta del import de FlowControl para hacer el monkeypatch.

    Uso:
        def test_xxx(mock_flow_control_patch):
            mock_flow = mock_flow_control_patch("paquete.modulo.FlowControl", sys_exit_side_effect=None)
    """

    def _patch(ruta_importacion: str):
        mock_sys_exit = MagicMock()
        monkeypatch.setattr("vlcishared.flow.flow.sys.exit", mock_sys_exit)

        mock_flow = MagicMock()

        def real_end_exec():
            return FlowControl.end_exec(mock_flow)

        mock_flow.end_exec.side_effect = real_end_exec

        def real_handle_error(cause, fatal=False):
            return FlowControl.handle_error(mock_flow, cause, fatal)

        mock_flow.handle_error.side_effect = real_handle_error

        mock_flow.flow_state = SUCCESS_EXEC

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: mock_flow)
        return mock_flow, mock_sys_exit

    return _patch
