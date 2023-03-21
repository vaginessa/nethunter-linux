# Author Shubham Vishwakarma
# git/twitter: ShubhamVis98

import gi, subprocess, psutil, random
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gio, Notify
from bin import ducky


class Functions:
    def get_output(self, cmd):
        run = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        run.wait()
        output = str(run.communicate()[0].decode())
        returncode = run.poll()
        return [output, returncode]
    
    def notification(self, msg):
        try:
            msg = Notify.Notification.new(msg)
            msg.show()
        except:
            pass

class Arsenal(Functions):
    def __init__(self, builder):
        self.builder = builder
        self.usbarsenal = './bin/usbarsenal'
        self.function = self.builder.get_object('function')
        self.idVen = self.builder.get_object('idVen')
        self.idProd = self.builder.get_object('idProd')
        self.manufact = self.builder.get_object('manufact')
        self.prod = self.builder.get_object('prod')
        self.serialno = self.builder.get_object('serialno')
        self.btnEn = self.builder.get_object('enable')
        self.btnDis = self.builder.get_object('disable')
        self.status = self.builder.get_object('status')

        self.btnEn.connect('clicked', self.enable)
        self.btnDis.connect('clicked', self.disable)

        self.status_buffer = self.status.get_buffer()
        self.setDefault()
    
    def getMassStoragePath(self):
        self.filechooser = self.builder.get_object('filechooser')
        return self.filechooser.get_filename()

    def setStatus(self, stsTxt):
        self.status_buffer.set_text(stsTxt)
    
    def getStatus(self):
        startIter, endIter = self.status_buffer.get_bounds()
        return(self.status_buffer.get_text(startIter, endIter, False))
    
    def setDefault(self):
        self.idVen.set_text('0x1D6B')
        self.idProd.set_text('0x0104')
        self.manufact.set_text('fossfrog')
        self.prod.set_text('HID Gadget')
        with open('/etc/machine-id', 'r')as macid:
            self.serialno.set_text(macid.read()[:-1])
        
        self.setStatus(self.get_output(f'{self.usbarsenal} -s')[0])

    def enable(self, btn):
        data = {
            'function': self.function.get_active_id(),
            'idvendor': self.idVen.get_text(),
            'idproduct': self.idProd.get_text(),
            'manufacturer': self.manufact.get_text(),
            'product': self.prod.get_text().replace(' ','_'),
            'serialno': self.serialno.get_text()
        }

        self.setStatus('')
        if data['function'] == 'null':
            self.setStatus('[?]Select Function First\n')
        elif '' in data.values():
            self.setStatus('[?]Fill Missing Details\n')
        else:
            if data['function'] == 'hid':
                self.setStatus(self.get_output(f'{self.usbarsenal} -h')[0])
            elif data['function'] == 'teth':
                self.setStatus(self.get_output(f'{self.usbarsenal} -t')[0])
            elif data['function'] == 'mass':
                self.setStatus(self.get_output(f'{self.usbarsenal} -m {self.getMassStoragePath()}')[0])
            data.pop('function')
            ARGS = ''
            for k, v in data.items():
                ARGS = f'{ARGS} --{k} "{v}"'
                self.setStatus(self.getStatus() + f'{k}: {"null" if v == "" else v}' + '\n')
            
            TMP = ARGS.split()
            ARGS = ''
            for i in range(len(TMP)):
                try:
                    TMP[i] = eval(TMP[i].replace('"',''))
                    ARGS = ARGS + ' ' + str(TMP[i])
                except:
                    ARGS = ARGS + ' ' + str(TMP[i])
            self.get_output(f'{self.usbarsenal} {ARGS}')[0]

    def disable(self, btn):
        self.setStatus(self.get_output(f'{self.usbarsenal} -d')[0])

class Ducky(Functions):
    def __init__(self, builder):
        self.builder = builder
        self.editor = self.builder.get_object('editor')
        self.btnOpen = self.builder.get_object('open')
        self.btnClear = self.builder.get_object('clear')
        self.btnSave = self.builder.get_object('save')
        self.btnInject = self.builder.get_object('inject')

        self.btnOpen.connect('clicked', self.openInEditor)
        self.btnClear.connect('clicked', self.clearEditor)
        self.btnSave.connect('clicked', self.save)
        self.btnInject.connect('clicked', self.inject)

        self.editor_buffer = self.editor.get_buffer()

    def clearEditor(self, btn):
        self.editor_buffer.set_text('')

    def inject(self, btn):
        startIter, endIter = self.editor_buffer.get_bounds()
        TMP = self.editor_buffer.get_text(startIter, endIter, False)
        ducky.inject_raw(TMP)
    
    def openInEditor(self, btn):
        filechooser = Gtk.FileChooserDialog(title="Open Ducky", parent=None, action=Gtk.FileChooserAction.OPEN)
        filechooser.add_buttons("_Open", Gtk.ResponseType.OK)
        filechooser.add_buttons("_Cancel", Gtk.ResponseType.CANCEL)
        filechooser.set_default_response(Gtk.ResponseType.OK)
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            try:
                with open(filechooser.get_filename()) as f:
                    self.editor_buffer.set_text(f.read())
            except TypeError:
                buffer.set_text('Select File First...')
        filechooser.destroy()
    
    def save(self, btn):
        startIter, endIter = self.editor_buffer.get_bounds()
        TMP = self.editor_buffer.get_text(startIter, endIter, False)
        if TMP == '':
            self.notification('Editor is empty')
            return

        filechooser = Gtk.FileChooserDialog(title="Open Ducky", parent=None, action=Gtk.FileChooserAction.SAVE)
        filechooser.add_buttons("_Save", Gtk.ResponseType.OK)
        filechooser.add_buttons("_Cancel", Gtk.ResponseType.CANCEL)
        filechooser.set_default_response(Gtk.ResponseType.OK)
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            try:
                with open(filechooser.get_filename(), 'w') as f:
                    f.write(TMP)
                    self.notification('File Saved')
            except PermissionError:
                self.notification('File Not Saved, !!!Access Denied!!!')
        filechooser.destroy()

class MACChanger(Functions):
    def __init__(self, builder):
        self.builder = builder
        self.maciface = self.builder.get_object('maciface')
        self.currentmac = self.builder.get_object('currentmac')
        self.newmac = self.builder.get_object('newmac')
        self.btnranmac = self.builder.get_object('btn_ranmac')
        self.btnchmac = self.builder.get_object('btn_chmac')
        self.btnrstmac = self.builder.get_object('btn_rstmac')

        self.maciface.connect('changed', self.on_iface_change)
        self.btnranmac.connect('clicked', self.gen_random_mac)
        self.btnchmac.connect('clicked', self.chmac)
        self.btnrstmac.connect('clicked', self.reset_mac)
        self.getifaces()

    def getifaces(self):
        tmp = psutil.net_if_addrs()
        iface_list = list(tmp.keys())
        ifindex = 0 if 'wlan0' not in iface_list else iface_list.index('wlan0')
        for iface in range(len(iface_list)):
            self.maciface.append_text(iface_list[iface])
        self.maciface.set_active(ifindex)
    
    def getmac(self, iface):
        tmp = psutil.net_if_addrs()
        for i in range(len(tmp[iface])):
            if 'AddressFamily.AF_PACKET' in str(tmp[iface][i]):
                return tmp[iface][i][1]

    def on_iface_change(self, iface):
        curmac = self.getmac(iface.get_active_text())
        self.currentmac.set_text(curmac)
    
    def gen_random_mac(self, btn):
        mac = ':'.join((f'0{(hex(i)[2:])}' if i<16 else hex(i)[2:]) for i in [random.randint(0, 255) for i in range(6)])
        self.newmac.set_text(mac)
    
    def chmac(self, btn):
        ifname = self.maciface.get_active_text()
        newmac = self.newmac.get_text()
        if len(newmac) == 17:
            self.get_output(f'ip link set {ifname} down')
            out = self.get_output(f'macchanger -m {newmac} {ifname}')
            self.get_output(f'ip link set {ifname} up')
            if out[1] == 0:
                self.notification('*MAC CHANGED: *')
            else:
                self.notification('!!! MAC NOT CHANGED !!!')
        self.on_iface_change(self.maciface)

    def reset_mac(self, btn):
        ifname = self.maciface.get_active_text()
        self.get_output(f'ip link set {ifname} down')
        out = self.get_output(f'macchanger -p {ifname}')
        self.get_output(f'ip link set {ifname} up')
        if out[1] == 0:
            self.notification('*MAC RESET DONE: *')
        else:
            self.notification('!!! MAC NOT CHANGED !!!')
        self.on_iface_change(self.maciface)

class NHGUI(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="in.fossfrog.nh")

    def do_activate(self):
        appname = 'NetHunter'
        builder = Gtk.Builder()
        builder.add_from_file("nethunter.ui")

        # Initialize Functions
        Arsenal(builder)
        Ducky(builder)
        MACChanger(builder)

        # Get The main window from the glade file
        window = builder.get_object("nh_main")
        window.set_title(appname)
        Notify.init(appname)

        # Show the window
        window.connect("destroy", Gtk.main_quit)
        window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)


nh = NHGUI().run(None)
Gtk.main()
