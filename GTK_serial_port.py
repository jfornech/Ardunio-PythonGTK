# coding: utf8
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


import serial
from serial import SerialException
from serial.tools import list_ports
from struct import unpack
from binascii import unhexlify
import traceback

class ConnectSerial(Gtk.Window):
    def __init__(self ):

        self.timeout, self.writeTimeout =  10, 5

        # initialisation du port série SANS configuration
        self.portSerial = serial.Serial(timeout=self.timeout, writeTimeout=self.writeTimeout)
  


        # Fenetre de configuration
        Gtk.Window.__init__(self, title="Connection série Arduino")
        self.set_border_width(10)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # frame de la fenetre de configuration
        box = Gtk.Box(spacing=6)


        # Nom du port série
        hbox = Gtk.Box(spacing=6)
        portList = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
        portName_store = Gtk.ListStore(str)
        

        for portName in portList:
            portName_store.append([portName])

        portName_combo = Gtk.ComboBox.new_with_model(portName_store)
        portName_combo.connect("changed",   self.on_portName_combo_changed)
        renderer_text = Gtk.CellRendererText()
        portName_combo.pack_start(renderer_text, True)
        portName_combo.add_attribute(renderer_text, "text", 0)
        vbox.pack_start(portName_combo, False, False, True)

        # Vitesse port série

        baudRate_list =["300","1200","2400","4800","9600","19200","28800","38400","57600","115200","230400"]
        baudRate_store = Gtk.ListStore(str)

        for baudRate in baudRate_list:
            baudRate_store.append([baudRate])

        baudRate_combo = Gtk.ComboBox.new_with_model(baudRate_store)
        baudRate_combo.connect("changed", self.on_baudRate_combo_changed)
        renderer_text = Gtk.CellRendererText()
        baudRate_combo.pack_start(renderer_text, True)
        baudRate_combo.add_attribute(renderer_text, "text", 0)
        vbox.pack_start(baudRate_combo, False, False, True)

    # Bouton de connection
        button = Gtk.Button.new_with_label("Connecter")
        button.connect("clicked", self.on_connect_clicked)
        vbox.pack_start(button, True, True, 0)

    # Bouton de connection
        button_disconect = Gtk.Button.new_with_label("Déconnecter")
        button_disconect.connect("clicked", self.on_disconnect_clicked)
        vbox.pack_start(button_disconect, True, True, 0)

      # Label de connection

        self.label1 = Gtk.Label("", xalign=0)
        self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
        vbox.pack_start(self.label1, True, True, 0)
        self.add(vbox)

    def on_portName_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            portName = model[tree_iter][0]
            print("Selected: portName=%s" % portName)
            self.conf_nom_port(portName)
        
    def on_baudRate_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            baudRate = model[tree_iter][0]
            print("Selected: baudRate=%s" % baudRate)
            self.conf_baudrate(baudRate)

    def on_connect_clicked(self, button):
        print("\"Click me\" button was clicked")
        self.open()

    def on_disconnect_clicked(self, button):
        print("\"Click me\" button was clicked")
        self.close()
                                   

    #################################
    ##     CONIGURATION DU PORT     #
    #################################
    def conf_baudrate(self, baudrate):
        '''configuation de la vitesse du port série'''
        self.baudrate = baudrate
        self.portSerial.baudrate = self.baudrate

    def conf_nom_port(self, nom_port):
        '''Configuration du nom de l'interface série'''
        self.nom_port = nom_port
        self.portSerial.port = self.nom_port


    def conf_timeout(self, timeout):
        '''Configuration du conf_ série'''
        self.timeout = timeout
        self.portSerial.timeout = self.timeout

    def conf_writeTimeout(self, writeTimeout):
        '''Configuration du writeTimeout érie'''
        self.writeTimeout = writeTimeout
        self.portSerial.writetimeout = self.writeTimeout

    def open(self):
        ''' Ouverture du port série.'''

        if (self.portSerial.isOpen() == 0):
            print("Port        : " + str( self.portSerial.port))
            print("Baurate     : " + str(self.portSerial.baudrate))
            print("Timeout     : " + str(self.portSerial.timeout))
            print('writeTimeout: ' + str(self.portSerial.writeTimeout))
            print('bytesize    : ' + str(self.portSerial.bytesize))
            print('parity      : ' + str(self.portSerial.parity))
            print('stopbits    : ' + str(self.portSerial.stopbits))
            print('xonxoff     : ' + str(self.portSerial.xonxoff))
            print('rtscts      : ' + str(self.portSerial.rtscts))
            print('dsrdtr      : ' + str(self.portSerial.dsrdtr))

            self.portSerial.port= self.portSerial.port
            self.portSerial.baudrate =self.portSerial.baudrate
            self.portSerial.open()
            self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
            print('connection : ' + str(self.portSerial.isOpen()))

        else:
            val= "Configurer le port avant de l'ouvrir"
            print(val)
        print (self.portSerial)

    def close(self):
        ''' Fermeture du port série.'''
        if (self.portSerial.isOpen() == 1):
            self.portSerial.close()
            self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
        else:
            pass
        print (self.portSerial)
     
    def send(self, msg):
        '''Envoie de données sur le port série '''
        self.portSerial.write(msg)

    def decode_float(self, s):
        '''Décode les données HEX reçues sur le port série en float '''
        return unpack('<f', unhexlify(s))[0]

    def recv(self):
        '''reception de données depuis le port série
        Attention le timeout est à modifier si il n'y
        a pas de donées lisible sur le port . Un delai peut etre nécessaire à l'initialisation
        de la carte Arduino et à l'établissement de la connection.
        '''

        # reception de 10 paquets
        for a in range(10):
            value = self.portSerial.readline()
            data = self.decode_float(value[2:10])
            print("{0} : {1} : {2}".format(a ,value , data))

    # Ne marche pas
    def show_error(self, *args):
        err = traceback.format_exception(*args)
        messagebox.showerror('Exception', err)


if __name__ == '__main__':
    win = ConnectSerial()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
