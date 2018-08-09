import datetime
import json
import logging
import socket
import struct
import threading
from typing import Callable, Any

from .state import State

## ========================================================================

def _log():
    return logging.getLogger( __name__ )

## ========================================================================

class UI( object ):
    """
    """

    def __init__( self,
                  refresh_interval_seconds: float,
                  receive_sleep_seconds: float = 1.0,
                  bind_ip: str = '',
                  multicast_ip: str = '224.0.0.1',
                  multicast_port: int = 10000,
                  max_buffer_size: int = 1024 * 16 ) -> None:
        """
        """
        self.refresh_interval_seconds = refresh_interval_seconds
        self.receive_sleep_seconds = receive_sleep_seconds
        self.bind_ip = bind_ip
        self.multicast_group = ( multicast_ip, multicast_port )
        self.max_buffer_size = max_buffer_size
        self.state = State()
        self.incremental_state = State()
        self.sync_thread = None
        self.receive_thread = None
        self.running = False
        self.socket = None
        self.state_listeners = []
        self.lock = threading.Lock()
        self.buff = bytearray( 1024 )


    def __del__(self) -> None:
        self.running = False


    def pause(self) -> None:
        _log().info( "paused UI called..." )
        self.running = False
        if self.sync_thread is not None:
            self.sync_thread.join()
            del self.sync_thread
            self.sync_thread = None
            _log().info( "  UI joined sync thread" )
        if self.receive_thread is not None:
            self.receive_thread.join()
            del self.receive_thread
            self.receive_thread = None
            _log().info( "  UI joined receive thread" )
        if self.socket is not None:
            self.socket.close()
            _log().info( "  UI closed socket" )
        _log().info( "UI paused!" )


    def start(self) -> None:
        _log().info( "start UI called..." )
        self.running = True
        self.sync_thread = threading.Thread(
            target=self._sync_loop,
            args=(self.refresh_interval_seconds, self._sync_state) )
        self.receive_thread = threading.Thread(
            target=self._receive_loop,
            args=(self.receive_sleep_seconds, self._receive) )
        self._open_socket()
        self.sync_thread.start()
        self.receive_thread.start()
        _log().info( "UI started!" )


    def add_state_listener( self,
                            c: Callable[[State],None] ) -> None:
        self.state_listeners.append( c )


    def remove_state_listener( self,
                               c: Callable[[State],None] ) -> None:
        self.state_listeners.remove( c )

        
    def _open_socket(self) -> None:
        server_address = ( self.bind_ip, self.multicast_group[1] )
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        group = socket.inet_aton( self.multicast_group[0] )
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
             mreq)
        self.socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1 )
        self.socket.settimeout( self.receive_sleep_seconds )
        self.socket.bind( server_address )
        _log().info( "Opened socket for receiving" )


    def _sync_state(self) -> None:
        self.state.merge( self.incremental_state )
        with self.lock:
            s = self.state.clone()
            self.incremental_state = State()
        _log().debug( "syncing state..." )
        for c in self.state_listeners:
            c(s)
        _log().debug( "synced state..." )

    def _sync_loop(self, interval_seconds, F) -> None:
        """
        """
        start_time = datetime.datetime.now()
        last_send_time = start_time
        _log().info( "  sync loop start at {0}".format( start_time ) )
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


    def _receive(self ) -> State:
        """
        """
        have_data = False
        try:
            _log().debug( "  receive starting..." )
            n = self.socket.recv_into( self.buff )
            _log().debug( "  have data ({0})".format( n ) ) 
            have_data = True
            more_data = ( n >= len(self.buff) )
            while more_data:

                # increase the buffer size and keep receiving bytes.
                # variable "n" holds information across the loop so
                # that tracks where to keep filling the buffer,
                # make sure it's not update in a wrong order
                new_n = n * 2
                if new_n > self.max_buffer_size:
                    raise RuntimeError( "Maximum receive buffer size of '{0}' reached!".format( self.max_buffer_size ) )
                _log().info( "  increasing receive buffer to {0}".format(
                    new_n ) )
                self.buff = self.buff + bytearray(n)

                recv_n = self.socket.recv_into( self.buff[n:] )
                more_data = ( recv_n + n >= new_n )
                n = new_n

            # ok, finally got some data in, decode and de-jsonify
            _log().debug( "  received {0} bytes".format( n ) )
            _log().debug( "  buff={0}".format( self.buff[:n] ) )
            s = State()
            s.load( self.buff[:n] )
            _log().debug( "  decoded {0}".format( s ) )
            return s
                
                
        except socket.timeout:
            if not have_data:
                _log().debug( "  nothign to receive" )
                return None
            raise RuntimeError( "timeout *after* we had read some data!" )

        
    def _receive_loop(self, sleep_seconds, F) -> None:
        """
        """
        start_time = datetime.datetime.now()
        last_receive_time = start_time
        _log().debug( "  receive loop start at {0}".format( start_time ) )
        while self.running:
            try:
                s = F()
                if s is not None:
                    self.incremental_state.merge( s )
            except:
                _log().exception( "error receiving: " )
                continue
            
                  

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
## ========================================================================
## ========================================================================
## ========================================================================
## ========================================================================
