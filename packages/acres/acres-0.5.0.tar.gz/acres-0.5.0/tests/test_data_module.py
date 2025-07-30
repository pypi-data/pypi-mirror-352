from pathlib import Path
import acres.typ as at
from acres import Loader

from .data import load_resource


def test_acres() -> None:
    assert isinstance(load_resource, Loader)

    text_resource = load_resource.readable('text_file')
    assert isinstance(text_resource, at.Traversable)
    assert text_resource.read_text() == 'A file with some text.\n'
    # New object is created
    assert load_resource.readable('text_file') is not text_resource

    with load_resource.as_path('text_file') as path:
        assert isinstance(path, Path)
        assert path.read_text() == 'A file with some text.\n'
        # New object is created
        assert path is not text_resource

    cached_text_resource = load_resource.cached('text_file')
    assert isinstance(path, Path)
    assert path.read_text() == 'A file with some text.\n'
    # New object is created
    assert path is not text_resource
    # Cached responses are exactly the same objects
    assert load_resource.cached('text_file') is cached_text_resource

    # load_resource() is the same as load_resource.cached()
    assert load_resource('text_file') is cached_text_resource

    # load_resource.readable() does not check the cache
    assert load_resource.readable('text_file') is not cached_text_resource


def test_acres_docstring() -> None:
    assert load_resource.__doc__
    assert 'text_file' in load_resource.__doc__

    throwaway = Loader('tests.data')
    assert isinstance(throwaway.__doc__, str)
    assert 'text_file' not in throwaway.__doc__
    assert throwaway.readable('text_file').is_file()

    throwaway = Loader('tests.data', list_contents=True)
    assert isinstance(throwaway.__doc__, str)
    assert 'text_file' in throwaway.__doc__
    assert throwaway.readable('text_file').is_file()
