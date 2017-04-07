# coding: utf8
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import serial
from struct import unpack
from binascii import unhexlify
import threading
import time


class ConnectSerial(Gtk.Window):
    def __init__(self):

        self.timeout, self.writeTimeout = 10, 5
        # initialisation du port série SANS configuration
        self.portSerial = serial.Serial(timeout=self.timeout, writeTimeout=self.writeTimeout)

        ########################
        #        WINDOWS       #
        ########################
        Gtk.Window.__init__(self, title="Connection série Arduino")
        self.set_border_width(10)
        self.set_border_width(10)
        self.set_default_size(300, 250)
        header = Gtk.HeaderBar(title="Connection Arduino")
        header.set_subtitle("configuration port série ")
        header.props.show_close_button = True
        self.set_titlebar(header)


        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        ########################
        #        COMBOBOX      #
        #   Nom du port série  #
        ########################
        portList = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
        portName_store = Gtk.ListStore(str)

        for portName in portList:
            portName_store.append([portName])

        portName_combo = Gtk.ComboBox.new_with_model(portName_store)
        portName_combo.connect("changed", self.on_portName_combo_changed)
        renderer_text = Gtk.CellRendererText()
        portName_combo.pack_start(renderer_text, True)
        portName_combo.add_attribute(renderer_text, "text", 0)
        vbox.pack_start(portName_combo, False, False, True)

        ########################
        #        COMBOBOX      #
        #        Baudrate      #
        ########################
        baudRate_list = ["300", "1200", "2400", "4800", "9600", "19200", "28800", "38400", "57600", "115200", "230400"]
        baudRate_store = Gtk.ListStore(str)

        for baudRate in baudRate_list:
            baudRate_store.append([baudRate])

        baudRate_combo = Gtk.ComboBox.new_with_model(baudRate_store)
        baudRate_combo.connect("changed", self.on_baudRate_combo_changed)
        renderer_text = Gtk.CellRendererText()
        baudRate_combo.pack_start(renderer_text, True)
        baudRate_combo.add_attribute(renderer_text, "text", 0)
        vbox.pack_start(baudRate_combo, False, False, True)

        ########################
        #         BOUTON       #
        #       Connection     #
        ########################
        button_connect = Gtk.ToggleButton("Connecter", name ='button_connect')
        button_connect.set_label("Connection")
        button_connect.connect("toggled", self.on_connect_clicked)
        vbox.pack_start(button_connect, True, True, 0)

        ########################
        #         BOUTON       #
        #          Led         #
        ########################
        button_led = Gtk.ToggleButton("Led ON/OFF")
        button_led.connect("clicked", self.on_button_led_clicked)
        vbox.pack_start(button_led, True, True, 0)

        ########################
        #         LABEL        #
        #        Status        #
        ########################
        self.label1 = Gtk.Label("", xalign=0)
        self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
        vbox.pack_start(self.label1, True, True, 0)
        self.add(vbox)

        #self.radioStatus = Gtk.RadioButon( , xalign=0)


    ########################
    #      SIGNAUX GTK     #
    ########################
    def on_portName_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            portName = model[tree_iter][0]
            print("Selected: portName=%s" % portName)
            self.conf_nom_port(portName)

    def on_baudRate_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            baudRate = model[tree_iter][0]
            print("Selected: baudRate=%s" % baudRate)
            self.conf_baudrate(baudRate)

    def on_connect_clicked(self, button):
        ctx = button.get_style_context()
        if button.get_active():

            # Vérifie que la configuration du port série
            if self.portSerial.portstr  != None:
                self.thread_connect = threading.Thread(target=self.open)
                self.thread_read = threading.Thread(target=self.read_from_port, args=(self.portSerial,))
                self.thread_connect.start()


                # Vérifie que le thread_connect est bien lancé
                if self.thread_connect.isAlive:
                    ctx.add_class('connect')
                    button.set_label("Connecter")

                    # lance la lecture sur le port série
                    self.thread_read.start()
                    print ("Lecture du port série")
                    print ('Lecture : ' + str(self.thread_read.name))
                else:
                    button.set_active(False)

            # Vérifie que la configuration du baudrate
            elif self.portSerial.BAUDRATES == None:
                button.set_label("Connection")
                button.set_active(False)

            else:
                button.set_label("Connection")
                button.set_active(False)

        else:
            ctx.remove_class('connect')
            self.close()
            self.thread_connect.join(0)
            self.thread_read.join(0)


    def on_button_led_clicked(self, button):
        if button.get_active():
            self.send(b'on')
        else:
            self.send(b'off')

    #################################
    ##           METHODES          ##
    ##     CONIGURATION DU PORT    ##
    ##           Pyserial          ##
    #################################
    def conf_baudrate(self, baudrate):
        """configuation de la vitesse du port série"""
        self.baudrate = baudrate
        self.portSerial.baudrate = self.baudrate

    def conf_nom_port(self, nom_port):
        """Configuration du nom de l'interface série"""
        self.nom_port = nom_port
        self.portSerial.port = self.nom_port

    def conf_timeout(self, timeout):
        """Configuration du conf_ série"""
        self.timeout = timeout
        self.portSerial.timeout = self.timeout

    def conf_writeTimeout(self, writeTimeout):
        """Configuration du writeTimeout érie"""
        self.writeTimeout = writeTimeout
        self.portSerial.writetimeout = self.writeTimeout

    def open(self):
        """ Ouverture du port série."""

        if self.portSerial.isOpen() == 0:
            #print("Port        : " + str(self.portSerial.port))
            #print("Baurate     : " + str(self.portSerial.baudrate))
            #print("Timeout     : " + str(self.portSerial.timeout))
            #print('writeTimeout: ' + str(self.portSerial.writeTimeout))
            #print('bytesize    : ' + str(self.portSerial.bytesize))
            #print('parity      : ' + str(self.portSerial.parity))
            #print('stopbits    : ' + str(self.portSerial.stopbits))
            #print('xonxoff     : ' + str(self.portSerial.xonxoff))
            #print('rtscts      : ' + str(self.portSerial.rtscts))
            #print('dsrdtr      : ' + str(self.portSerial.dsrdtr))

            self.portSerial.port = self.portSerial.port
            self.portSerial.baudrate = self.portSerial.baudrate
            self.portSerial.open()
            self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
            #print('connection : ' + str(self.portSerial.isOpen()))
            self.send(b'off')

        else:
            val = "Configurer le port avant de l'ouvrir"
            print(val)

        #print(self.portSerial)

    def close(self):
        """ Fermeture du port série."""

        if self.portSerial.isOpen() == 1:
            self.send(b'off')
            self.portSerial.close()
            self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
        else:
            pass
        print(self.portSerial)

    def send(self, msg):
        """Envoie de données sur le port série """
        self.portSerial.write(msg)

    def decode_float(self, s):
        """Décode les données HEX reçues sur le port série en float """
        return unpack('<f', unhexlify(s))[0]

    def handle_data(self, data):
        print(data)

    def read_from_port(self):
        """reception de données depuis le port série
        Attention le timeout est à modifier si il n'y
        a pas de donées lisible sur le port . Un delai peut etre nécessaire à l'initialisation
        de la carte Arduino et à l'établissement de la connection.
        """
        time.sleep(1)
        while self.portSerial.isOpen():
            reading = self.portSerial.readline().decode()
            print(reading)

    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)


if __name__ == '__main__':
    win = ConnectSerial()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
