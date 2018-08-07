import atexit
import datetime
import logging
import socket
import struct
import threading
import time
from typing import Optional

from .state import State

## ========================================================================

def _log():
    return logging.getLogger( __name__ )

## ========================================================================

class BatchSender( object ):

    def __init__( self,
                  send_interval_seconds: float,
                  multicast_ip: str = '224.0.0.1',
                  multicast_port: int = 10000,
                  num_retries: int = 3) -> None:
        """
        """
        self.send_interval_seconds = send_interval_seconds
        self.state = State()
        self.timer_thread = None
        self.running = False
        self.multicast_group = ( multicast_ip, multicast_port )
        self.socket = None
        self.num_retries = num_retries


    def __del__(self):
        self.state = None
        self.running = False

    def _stop(self):
        self.state = None
        self.running = False

    def pause(self) -> None:
        _log().info( "paused called..." )
        self.running = False
        if self.timer_thread is not None:
            self.timer_thread.join()
            del self.timer_thread
            self.timer_thread = None
            _log().info( "  joined timer thread" )
        if self.socket is not None:
            self.socket.close()
            _log().info( "  closed socket" )
        _log().info( "paused!" )


    def start(self) -> None:
        _log().info( "start called..." )
        self.running = True
        self.timer_thread = threading.Thread(
            target=self._timer_loop,
            args=(self.send_interval_seconds, self._send_state) )
        self._open_socket()
        self.timer_thread.start()
        _log().info( "started!" )

        
    def _open_socket(self) -> None:
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socket.setsockopt( socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                                struct.pack( 'b', 0 ) )
        _log().info( "Opened multicast socket" )


    def _send_state(self) -> None:
        """
        """
        state_rep = self.state.representation() + b"\n"
        for i in range(self.num_retries):
            try:
                sent = _fully_send( self.socket,
                                    self.multicast_group,
                                    state_rep )
                _log().debug( "sent {0}".format( sent ) )
                if sent is not None:
                    return
            except:
                pass
        _log().warning( "Unable to send state after retries!" )
            

    def _timer_loop(self, interval_seconds, F) -> None:
        """
        """
        start_time = datetime.datetime.now()
        last_send_time = start_time
        _log().info( "  loop start at {0}".format( start_time ) )
        while self.running:

            now = datetime.datetime.now()
            if ( now - last_send_time ).total_seconds() >= interval_seconds:
                try:
                    last_send_time = now
                    F()
                except Exception:
                    raise

            # sleep
            try:
                dt = interval_seconds - ( now - last_send_time ).total_seconds()
                if dt > 0:
                    time.sleep( dt )
            except Exception:
                pass
        
                  

## ========================================================================

def _fully_send( socket,
                 address,
                 rep: bytes ) -> Optional[int]:
    """
    """
    total_n = len(rep)
    sent_n = 0
    try:
        while sent_n < total_n:
            this_sent = socket.sendto( rep[ sent_n: ],
                                       address )
            sent_n += this_sent
        return sent_n
    except:
        _log().exception( "error sending socket data: " )
        return None

## ========================================================================

DEFAULT_BATCH_SENDER = BatchSender( 10.0 )
DEFAULT_BATCH_SENDER.start()
atexit.register(lambda: DEFAULT_BATCH_SENDER._stop() )

## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
