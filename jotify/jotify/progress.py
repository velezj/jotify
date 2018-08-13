import inspect
import logging
import pathlib
from typing import Iterable, Any, Optional

from .batch_sender import BatchSender, DEFAULT_BATCH_SENDER


## ========================================================================

def _log():
    return logging.getLogger( __name__ )

## ========================================================================

def track(
        x: Iterable[Any],
        name: Optional[str] = None,
        sender: BatchSender = DEFAULT_BATCH_SENDER ) -> Iterable[Any]:
    if name is None:
        name = _guess_name()
    _try_set_schema( x, name, sender )
    sender.state.set( name, 0 )
    for i, element in enumerate(x):
        sender.state.add( name, 1 )
        yield element
        

## ========================================================================

def _guess_name() -> Optional[str]:
    stack = inspect.stack()
    name = None
    stack_up_index = 2
    try:
        while name is None and len(stack) > stack_up_index:
            caller_info = stack[ stack_up_index ]
            stack_up_index += 1
            filename = pathlib.Path( caller_info.filename ).stem
            if filename == 'progress':
                continue
            name = "{filename}.{function}.{lineno}".format(
                filename = filename,
                function = caller_info.function,
                lineno = caller_info.lineno )
    finally:
        del stack
    return None

## ========================================================================

def _try_set_schema( x: Iterable[Any],
                     name: str,
                     sender: BatchSender ) -> None:
    """
    """
    try:
        n = len(x)
        sender.state.schema( name, 0, n-1 )
    except:
        pass
    

## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
