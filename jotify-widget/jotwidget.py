import signal

from jotify.state_ui import UI

import gi
gi.require_version( 'Gtk', '3.0' )
gi.require_version( 'AppIndicator3', '0.1' )

from gi.repository import Gtk as gtk
from gi.repository import GLib
from gi.repository import AppIndicator3 as appindicator

APPINDICATOR_ID = 'jotify-widget'

LABEL_GUIDE = '-'*20

def _quit(source):
    gtk.main_quit()


def _show_jotify_state( indicator, state ):
    label = ""
    if state is not None:
        label += " "
        for k in sorted(state.stats.keys()):
            label += " " + str(int(state.stats[k]['count'])) + " |"
    else:
        label = "\U0001F618"
    GLib.idle_add( _update_label, indicator, label )
    #print( label )


def _update_label( indicator, label ):
    indicator.set_label( label, LABEL_GUIDE )
    return False


def build_menu():
    menu = gtk.Menu()
    item_quit = gtk.MenuItem("Quit")
    item_quit.connect( 'activate', _quit )
    menu.append( item_quit )
    menu.show_all()
    return menu


def main():

    # make sure we can quit from terminal :)
    signal.signal( signal.SIGINT, signal.SIG_DFL )

    # create the GTK app
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, "info", appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu( build_menu() )
    indicator.set_label( "*", LABEL_GUIDE )

    # attach to the jotify UI
    jui = UI( 5.0 )
    jui.add_state_listener( lambda s: _show_jotify_state( indicator, s ) )
    _show_jotify_state( indicator, None )
    jui.start()

    # inifninte GTK loop!
    gtk.main()

if __name__ == "__main__":
    main()
    
