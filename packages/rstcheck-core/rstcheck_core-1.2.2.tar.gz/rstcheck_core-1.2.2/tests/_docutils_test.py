"""Tests for ``_docutils`` module."""

from __future__ import annotations

import docutils.parsers.rst.directives as docutils_directives
import docutils.parsers.rst.roles as docutils_roles
import pytest

from rstcheck_core import _docutils, _extras


class TestIgnoreDirectivesAndRoles:
    """Test ``ignore_directives_and_roles`` function."""

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_empty_lists() -> None:
        """Test with empty lists."""
        directives: list[str] = []
        roles: list[str] = []

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert not docutils_directives._directives  # type: ignore[attr-defined]
        assert not docutils_roles._roles  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_only_roles() -> None:
        """Test with only roles to add."""
        directives: list[str] = []
        roles = ["test_role"]

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert not docutils_directives._directives  # type: ignore[attr-defined]
        assert "test_role" in docutils_roles._roles  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_only_directives() -> None:
        """Test with only directives to add."""
        directives = ["test_directive"]
        roles: list[str] = []

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert "test_directive" in docutils_directives._directives  # type: ignore[attr-defined]
        assert not docutils_roles._roles  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_both() -> None:
        """Test with both."""
        directives = ["test_directive"]
        roles = ["test_role"]

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert "test_directive" in docutils_directives._directives  # type: ignore[attr-defined]
        assert "test_role" in docutils_roles._roles  # type: ignore[attr-defined]


class TestRegisterCodeRirective:
    """Test ``register_code_directive`` function."""

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_does_nothing_when_sphinx_installed() -> None:
        """Test function does nothing when sphinx is installed."""
        _docutils.register_code_directive()  # act

        assert "code" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "code-block" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "sourcecode" not in docutils_directives._directives  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_registers_all_when_sphinx_is_missing() -> None:
        """Test function registers all directives when sphinx is missing."""
        _docutils.register_code_directive()  # act

        assert "code" in docutils_directives._directives  # type: ignore[attr-defined]
        assert "code-block" in docutils_directives._directives  # type: ignore[attr-defined]
        assert "sourcecode" in docutils_directives._directives  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_does_nothing_when_sphinx_is_missing_and_all_ignored() -> None:
        """Test function does nothing when sphinx is missing, but all ignores are ``True``."""
        _docutils.register_code_directive(  # act
            ignore_code_directive=True,
            ignore_codeblock_directive=True,
            ignore_sourcecode_directive=True,
        )

        assert "code" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "code-block" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "sourcecode" not in docutils_directives._directives  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_code_when_others_are_ignored() -> None:
        """Test function installs only code directive when others are ignored."""
        _docutils.register_code_directive(  # act
            ignore_codeblock_directive=True, ignore_sourcecode_directive=True
        )

        assert "code" in docutils_directives._directives  # type: ignore[attr-defined]
        assert "code-block" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "sourcecode" not in docutils_directives._directives  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_code_block_when_others_are_ignored() -> None:
        """Test function installs only code-block directive when others are ignored."""
        _docutils.register_code_directive(  # act
            ignore_code_directive=True, ignore_sourcecode_directive=True
        )

        assert "code" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "code-block" in docutils_directives._directives  # type: ignore[attr-defined]
        assert "sourcecode" not in docutils_directives._directives  # type: ignore[attr-defined]

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_sourcecode_when_others_are_ignored() -> None:
        """Test function installs only sourcecode directive when others are ignored."""
        _docutils.register_code_directive(  # act
            ignore_code_directive=True, ignore_codeblock_directive=True
        )

        assert "code" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "code-block" not in docutils_directives._directives  # type: ignore[attr-defined]
        assert "sourcecode" in docutils_directives._directives  # type: ignore[attr-defined]
