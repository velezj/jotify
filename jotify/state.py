import collections
import copy
import datetime
import json
import logging
import threading
from typing import Dict, Optional

## ========================================================================

class State( object ):

    def __init__(self,
                 max_hist: int = 10 ):
        self.lock = threading.Lock()
        self.stats = {}
        self.max_hist = max_hist


    def schema( self,
                id: str,
                min: Optional[float],
                max: Optional[float] ) -> None:
        with self.lock:
            if id not in self.stats:
                self.stats[ id ] = self._scaffold()
            self.stats[ id ][ 'min' ] = min
            self.stats[ id ][ 'max' ] = max
            

    def add( self,
             id: str,
             count: float ) -> None:
        with self.lock:
            if id not in self.stats:
                self.stats[ id ] = self._scaffold()
            self.stats[ id ]['count'] += count
            self.stats[ id ]['timehist'].append( datetime.datetime.now() )


    def representation(self) -> bytes:
        with self.lock:
            rep = json.dumps( podify( self.stats ) ).encode( 'utf-8' )
            if len(rep) % 2 == 0:
                return rep + b" "
            return rep


    def load( self, rep: bytes ) -> None:
        new_state = State(self.max_hist)
        new_state.stats = json.loads( rep.decode('utf-8').strip() )
        self.merge( new_state )
        

    def merge( self, state ) -> None:
        with self.lock:
            with state.lock:
                self.stats.update( state.stats )

    def clone(self) -> 'State':
        with self.lock:
            s = State( self.max_hist)
            s.stats = copy.deepcopy( self.stats )
            return s


    def _scaffold(self) -> Dict:
        return { 'count' : 0.0,
                 'min' : None,
                 'max' : None,
                 'timehist' : collections.deque([],self.max_hist) }
        

## ========================================================================

def podify( x ):
    if x is None:
        return x
    if isinstance( x, ( str, int, float ) ):
        return x
    if isinstance( x, collections.deque ):
        return podify( list( x ) )
    if isinstance( x, (list,tuple) ):
        return list(map(podify,x))
    if isinstance( x, dict ):
        return dict(map(podify,x.items()))
    return str( x )

## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
