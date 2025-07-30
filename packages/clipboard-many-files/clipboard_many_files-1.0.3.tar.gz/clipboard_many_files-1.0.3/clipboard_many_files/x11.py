# Taken from
# https://stackoverflow.com/questions/3902263/how-can-python-access-the-x11-clipboard

from Xlib import X, display as Xdisplay

def property2str(display, prop):
    if prop.property_type == display.get_atom("STRING"):
        return prop.value.decode('ISO-8859-1')
    elif prop.property_type == display.get_atom("UTF8_STRING"):
        return prop.value.decode('UTF-8')
    else:
        return "".join(str(c) for c in prop.value)

def get_selection(display, window, bufname, typename):
    bufid = display.get_atom(bufname)
    typeid = display.get_atom(typename)
    propid = display.get_atom('XSEL_DATA')
    incrid = display.get_atom('INCR')

    window.change_attributes(event_mask = X.PropertyChangeMask)
    window.convert_selection(bufid, typeid, propid, X.CurrentTime)
    while True:
        ev = display.next_event()
        if ev.type == X.SelectionNotify and ev.selection == bufid:
            break

    if ev.property == X.NONE:
        return None # request failed, e.g. owner can't convert to target format type
    else:
        prop = window.get_property(propid, X.AnyPropertyType, 0, 2**31-1, 1)

        if prop.property_type == incrid:
            result = ""
            while True:
                while True:
                    ev = display.next_event()
                    if ev.type == X.PropertyNotify and ev.atom == propid and ev.state == X.PropertyNewValue:
                        break

                prop = window.get_property(propid, X.AnyPropertyType, 0, 2**31-1, 1)
                if len(prop.value) == 0:
                    break

                result += property2str(display, prop)
            return result
        else:
            return property2str(display, prop)

class X11Clipboard:
    def __init__(self, ):
        display = Xdisplay.Display()
        window = display.screen().root.create_window(0,0, 1,1, 0, X.CopyFromParent)

    def
print( get_selection(display, window, "CLIPBOARD", "UTF8_STRING") or \
       get_selection(display, window, "CLIPBOARD", "STRING") )
