import os
import shutil
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_sftp_patch(monkeypatch):
    """
    Fixture reutilizable que mockea la clase SFTPClient para evitar conexiones reales con SFTP.

    - Reutilizable en distintos módulos donde se importe SFTPClient.
    - Mockea los métodos: list, list_sorted_date_modification, download (con shutil.copyfile), move, upload, delete y sftp.rename para evitar efectos reales.
    - Devuelve una función que permite especificar el path del import y el retorno de list().
    - Requiere pasar la ruta donde se usa SFTPClient (para monkeypatching dinámico).

    Uso:
        def test_xxx(mock_sftp_patch):
            mock_sftp = mock_sftp_patch("modulo.donde.importa.SFTPClient", list_return=["file1.csv"], ...)
    """

    def _patch(
        ruta_importacion: str,
        list_return=[],
        list_sorted_date_modification_return=[],
        download_side_effect=patch_download_side_effect,
        move_side_effect=None,
        upload_side_effect=None,
        delete_side_effect=None,
        sftp_rename_side_effect=None,
    ):
        sftp = MagicMock()

        sftp.connect.return_value = None
        sftp.close.return_value = None

        sftp.list.return_value = list_return
        sftp.list_sorted_date_modification.return_value = list_sorted_date_modification_return
        sftp.download.side_effect = download_side_effect
        sftp.move.side_effect = move_side_effect
        sftp.upload.side_effect = upload_side_effect
        sftp.delete.side_effect = delete_side_effect
        sftp.sftp.rename.side_effect = sftp_rename_side_effect

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: sftp)
        return sftp

    return _patch


def patch_download_side_effect(origen, tmp_folder, archivo):
    """
    Simula la descarga de un archivo SFTP copiándolo desde 'origen' a 'tmp_folder'.
    """
    shutil.copyfile(os.path.join(origen, archivo), os.path.join(tmp_folder, archivo))
