import subprocess;
import json;
import urllib;
import urllib.request;
import sys;
import dbus;
from multiprocessing.pool import ThreadPool
from PyQt4 import QtGui, QtCore;

def main():
    #lyrics = getlyrics()
    app = QtGui.QApplication(sys.argv);
    q = Window();
    app.exec_();

def getlyrics():
    try:
        info = getdbusinfo();
        artist = info[0];
        track = info[1];
    except:
        print("Could not get song info.");
        return None;

    try:
        track = track.split("(")[0];
        track = track.split("[")[0];
        track = ''.join([i for i in track if (i.isalnum())]).lower();
        artist = ''.join([i for i in artist if (i.isalnum())]).lower();
        newurl = "http://www.azlyrics.com/lyrics/" + artist + "/" + track + ".html";
        lyrics = getLyricsFromPage(newurl);
    except:
        print("Could not get Lyrics for {0} by {1}.".format(track, artist));
        return None;

    return lyrics;
#def getinfo(): #depricated
#    proc = subprocess.Popen(["wmctrl -lp | grep \"$(pgrep spotify)\""], stdout=subprocess.PIPE, shell=True)
#    (out, err) = proc.communicate()
#    out = out.decode('utf-8');
#    out = out.strip();
#    out = out.split(" ");
#    out = out[8:len(out)];
#    out = " ".join(out);
#    out = out.split(" - ", 1);
#    return out;
def getdbusinfo():
    bus        = dbus.SessionBus()
    dbusobject = bus.get_object('org.mpris.MediaPlayer2.spotify','/org/mpris/MediaPlayer2')
    promanager = dbus.Interface(dbusobject, 'org.freedesktop.DBus.Properties')
    metadata   = promanager.Get('org.mpris.MediaPlayer2.Player', 'Metadata')

    artist = metadata["xesam:title"];
    track = metadata["xesam:artist"][0];
    return [track, artist]
def getHTML(url):
    request = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
    html = urllib.request.urlopen(request).read();
    html = html.decode("utf-8");
    return html;
def getLyricsFromPage(url):
    html = getHTML(url);
    text = html.split("<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->", 1)[1];
    text = text.split("<!-- MxM banner -->", 1)[0];
    return text;


class Window(QtGui.QWidget):
    lbl_lyrics = None;
    lbl_title = None;
    lbl_artist = None;

    btn_exit = None;
    btn_maximize = None;

    gradtop = None;
    gradbot = None;

    scroll = None;
    repoint = None;
    timer = None;

    lastinfo = ["", ""];

    threadresult = None;

    def __init__(self):
        super(Window, self).__init__();
        #self.resizeEvent = onResize
        self.setStyleSheet("background-color: #0A050A;");
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint);
        self.spawn();
        self.resize(1000, 700);

        self.timer = QtCore.QTimer();
        self.timer.timeout.connect(self.tick)
        self.timer.start(500);

        self.setWindowOpacity(0.8);

        #self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True);
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground);

        self.show();

    def spawn(self):
        self.lbl_lyrics = QtGui.QLabel(self);
        self.lbl_lyrics.setFont(QtGui.QFont("Helvetica", 15));
        self.lbl_lyrics.setStyleSheet("color : #DDDDDD;");
        self.lbl_lyrics.setAlignment(QtCore.Qt.AlignCenter);

        self.lbl_title = QtGui.QLabel(self);
        self.lbl_title.setFont(QtGui.QFont("Helvetica", 30));
        self.lbl_title.setStyleSheet("color : #FF6633;");
        self.lbl_title.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom);

        self.lbl_artist = QtGui.QLabel(self);
        self.lbl_artist.setFont(QtGui.QFont("Helvetica", 12));
        self.lbl_artist.setStyleSheet("color : #AAAAAA;");
        self.lbl_artist.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter);

        self.gradtop = QtGui.QLabel(self);
        self.gradtop.setStyleSheet("background: qlineargradient(x1: 0, y1: 1, x2: 0, y2: 0, stop: 0 rgba(0, 0, 0, 0%), stop: 1.0 #0A050A);");
        self.gradtop.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents);
        self.gradtop.raise_();

        self.gradbot = QtGui.QLabel(self);
        self.gradbot.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgba(0, 0, 0, 0%), stop: 1.0 #0A050A);");
        self.gradbot.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents);
        self.gradbot.raise_();


        self.scroll = QtGui.QScrollArea(self);
        self.scroll.setWidget(self.lbl_lyrics)
        self.scroll.setFrameShape(QtGui.QFrame.NoFrame);
        self.scroll.horizontalScrollBar().hide();
        self.scroll.verticalScrollBar().hide();
        #self.scroll.setBackgroundRole(QtGui.QPalette);
        self.scroll.setWidgetResizable(True)


        self.btn_exit = QtGui.QPushButton("X", self);
        self.btn_exit.clicked.connect(QtCore.QCoreApplication.instance().quit);
        self.btn_maximize = QtGui.QPushButton("□", self);
        self.btn_maximize.clicked.connect(self.dynamicFullScreen);

    def dynamicFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_maximize.setText("□");
        else:
            self.showFullScreen()
            self.btn_maximize.setText("_");

    def mousePressEvent(self, mousePressEvent):
        self.repoint = mousePressEvent.pos();

    def mouseMoveEvent(self, mouseMoveEvent):
        self.move(self.mapToGlobal(mouseMoveEvent.pos() - self.repoint));

    def resizeEvent(self, resizeEvent):
        self.scroll.setGeometry(0, 100, self.width(), self.height() - 100)
        self.lbl_title.setGeometry(50, 0, self.width() - 100, 60)
        self.lbl_artist.setGeometry(50, 60, self.width() - 100, 40)

        self.gradtop.setGeometry(0, 100, self.width(), 100);
        self.gradbot.setGeometry(0, self.height() - 100, self.width(), 100);
        self.gradtop.raise_();
        self.gradbot.raise_();

        self.btn_exit.setGeometry(self.width() - 50, 0, 50, 50)
        self.btn_maximize.setGeometry(self.width() - 100, 0, 50, 50)

    def tick(self):
        info = getdbusinfo();
        if (info[0] != self.lastinfo[0]) or (info[1] != self.lastinfo[1]):
            self.startThread();
            self.lbl_title.setText(info[1]);
            self.lbl_artist.setText(info[0].upper())
            self.lbl_lyrics.setText("Loading...");

        self.lastinfo = info;

        if self.threadresult.ready():
            lyrics = self.threadresult.get(1);
            if lyrics == "" or lyrics is None:
                lyrics = "Could not get lyrics ;_;"
            else:
                lyrics = ".\n\n\n\n\n" + lyrics + "\n\n\n\n\n.";
                lyrics = lyrics.replace("<br>", "").replace("</div>", "");
            self.lbl_lyrics.setText(lyrics);

    def startThread(self):
        pool = ThreadPool(processes=1)
        self.threadresult = pool.apply_async(getlyrics)

main();
