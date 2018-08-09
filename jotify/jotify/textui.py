import datetime
import logging

from .state_ui import UI, State

import dateutil.parser
import blessings

## ========================================================================

def _log():
    return logging.getLogger( __name__ )

## ========================================================================

def _show_state( s: State,
                 term ) -> None:
    with term.fullscreen():
        with term.location( 0, 0 ):
            print( term.green( "Jotify Text UI \U0001F618" ) )
            for k in sorted(s.stats.keys()):
                last = None
                td = None
                try:
                    if len(s.stats[k]['timehist']) > 0:
                        last = s.stats[k]['timehist'][-1]
                        last = dateutil.parser.parse(last)
                    if last is not None:
                        td = datetime.datetime.now() - last
                    print( "{key} : {count}  ({td} ago)".format(
                        key = k.ljust(80),
                        count = str(s.stats[k]['count']).rjust(10),
                        td = td ) )
                except:
                    _log().exception( "ERROR: " )
                    print( term.red( "stats = {0}".format( s.stats ) ) )
            

## ========================================================================


if __name__ == "__main__":

    term = blessings.Terminal()

    ui = UI( 5.0 )
    ui.add_state_listener(lambda s: _show_state(s,term) )
    ui.start()
    
