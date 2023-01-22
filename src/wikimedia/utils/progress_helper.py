import progressbar as pb # type: ignore
import typing as t

T = t.TypeVar('T')

def progress_overlay(items: t.Iterator[T], title: str) -> t.Iterator[T]:
    bar_i = 0
    widgets = [title, ' ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for item in items:
            bar_i = bar_i + 1
            bar.update(bar_i) # type: ignore
            yield item
