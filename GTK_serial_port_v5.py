# coding: utf8
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import serial
from serial.tools import list_ports
from struct import unpack
from binascii import unhexlify
from multiprocessing import Process
import time

from arduino import arduino


class ConnectSerial(Gtk.Window):
    def __init__(self):

        self.timeout, self.writeTimeout, self.rxdata_byte , self.txdata_byte , self.txData , self.rxData = 10, 5, 0 ,0 , None , None

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

        # liste des ports série disponible
        portList = []
        for port in list_ports.comports():
            portList.append(port.device)

        portName_store = Gtk.ListStore(str)

        for portName in portList:
            portName_store.append([portName])

        portName_combo = Gtk.ComboBox.new_with_model(portName_store)
        portName_combo.connect("changed", self.on_portName_combo_changed)
        renderer_text = Gtk.CellRendererText()
        portName_combo.pack_start(renderer_text, True)
        portName_combo.add_attribute(renderer_text, "text", 0)
        portName_combo.set_active(0)
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
        baudRate_combo.set_active(4)
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
        self.button_led = Gtk.ToggleButton("Led ON/OFF")
        self.button_led.connect("clicked", self.on_button_led_clicked)
        vbox.pack_start(self.button_led, True, True, 0)

        ########################
        #         BOUTON       #
        #         read         #
        ########################
        self.button_read = Gtk.ToggleButton("Lecture ON/OFF")
        self.button_read.connect("clicked", self.on_button_read_clicked)
        vbox.pack_start(self.button_read, True, True, 0)

        ########################
        #         LABEL        #
        #        Status        #
        ########################
        self.label1 = Gtk.Label("", xalign=0)
        self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
        vbox.pack_start(self.label1, True, True, 0)
        self.add(vbox)


        ########################
        #         LABEL        #
        #        RX/TX         #
        ########################
        self.labelrx = Gtk.Label()
        vbox.pack_start(self.labelrx, True, True, 0)
        self.add(vbox)

        self.button_led.set_sensitive(False)
        self.button_read.set_sensitive(False)

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
        if button.get_active() == True:
            self.process_connect = Process(target=self.open)
            self.process_connect.start()

            print('Démarrage :' + self.process_connect.name  + ' ' + str(self.process_connect.pid))
            """"
            Ouverture du port série.
            """
            if self.portSerial.isOpen() == False:
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
                self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))  # Vérifie que le thread_connect est bien lancé
                if self.process_connect.is_alive():
                    ctx.add_class('connect')
                    button.set_label("Connecter")
                    self.button_led.set_sensitive(True)
                    self.button_read.set_sensitive(True)
                    #self.send(b'off')

                else:
                    button.set_active(False)

            else:
                val = "Configurer le port avant de l'ouvrir"
                print(val)

        if button.get_active() == False:
            print('Arrêt :' + self.process_connect.name + ' ' + str(self.process_connect.pid))
            ctx.remove_class('connect')
            self.close()
            self.process_connect.terminate()
            self.button_led.set_sensitive(False)
            self.button_read.set_sensitive(False)

    def on_button_read_clicked(self, button):
        if button.get_active()==True:
            self.process_read = Process(target=self.read_from_port, args=(self.portSerial,))
            self.process_read.start()
            print('Start : ' + str(self.process_read.name) + ': ' + str(self.process_read.ident))
        if button.get_active() == False:
            print('Stop : ' + str(self.process_read.name) + ': ' + str(self.process_read.ident))
            self.process_read.terminate()

    def on_button_led_clicked(self, button):
        if button.get_active():
            self.setHigh(9)
        else:
            self.setLow(9)


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
        print ("Ouverture du port série")

        if self.portSerial.isOpen() == False:
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
            #self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
            #print('connection : ' + str(self.portSerial.isOpen()))
            #self.send(b'off')



        else:
            val = "Configurer le port avant de l'ouvrir"
            print(val)

    def close(self):
        """ Fermeture du port série."""

        if self.portSerial.isOpen() == 1:
            self.send(b'off')
            self.portSerial.close()
            self.label1.set_text('Connection: ' + str(self.portSerial.isOpen()))
        else:
            pass
        print(self.portSerial)

    def decode_float(self, s):
        """Décode les données HEX reçues sur le port série en float """
        return unpack('<f', unhexlify(s))[0]

    def handle_data(self, data):
        print(data)
        self.label1.set_text("TTTTTT")
        self.labelrx.set_text('Connection: ' + str(self.portSerial.isOpen()))  # Vérifie que le thread_connect est bien lancé

    def read_byteIN(self ,data ):
        test = self.portSerial.inWaiting()
        self.rxdata_byte =  self.rxdata_byte + int(data)
        print ("IN byte: " + str(self.rxdata_byte))
        win.labelrx.set_text(str(self.rxdata_byte))


    def read_from_port(self,data):
        """reception de données depuis le port série
        Attention le timeout est à modifier si il n'y
        a pas de donées lisible sur le port . Un delai peut etre nécessaire à l'initialisation
        de la carte Arduino et à l'établissement de la connection.
        """
        while self.portSerial.isOpen():
            #self.portSerial.flushInput()
            reading = self.portSerial.readline().decode('utf-8')
            self.handle_data(reading)

            test = self.portSerial.inWaiting()
            self.read_byteIN(data=str(test))

    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def sendData(self, serial_data):
        #global txdata_byte
        """Envoie de données sur le port série """

       # written = self.portSerial.write(serial_data)

        #while (self.getData()[0] != "w"):
        #    pass

        serial_data = str(serial_data).encode()
        self.portSerial.write(serial_data)

    def getData(self):
        input_string = self.portSerial.readline()
        input_string = input_string.decode('utf-8')
        return input_string.rstrip('\n')

    def setLow(self, pin):
        self.sendData(b'0')
        self.sendData(pin)
        return True

    def setHigh(self, pin):
        self.sendData(b'1')
        self.sendData(pin)
        return True


if __name__ == '__main__':
    win = ConnectSerial()
    win.connect("delete-event", Gtk.main_quit)

    win.show_all()
    Gtk.main()
