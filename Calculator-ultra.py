import customtkinter as ctk
import tkinter as tk
import math, json, threading, urllib.request
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG    = "#1c1c1c"
S1    = "#2d2d2d"
S1H   = "#3d3d3d"
S2    = "#333333"
S2H   = "#434343"
S3    = "#666666"
S3H   = "#787878"
EQ    = "#4a9eff"
EQH   = "#5ab0ff"
ACC   = "#4a9eff"
TEXT  = "#ffffff"
TEXT2 = "#a0a0a0"
BRD   = "#3a3a3a"

CURRENCIES = ["USD","EUR","GBP","JPY","BDT","CAD","AUD","CHF","CNY","INR",
              "SGD","AED","SAR","MYR","THB","KRW","BRL","MXN","ZAR","HKD","TRY","NZD"]
FALLBACK = {"USD":1,"EUR":0.92,"GBP":0.79,"JPY":149.5,"BDT":110,"CAD":1.36,
            "AUD":1.53,"CHF":0.89,"CNY":7.24,"INR":83.1,"SGD":1.34,"AED":3.67,
            "SAR":3.75,"MYR":4.7,"THB":35.6,"KRW":1325,"BRL":5.0,"MXN":17.2,
            "ZAR":18.6,"HKD":7.82,"TRY":32.1,"NZD":1.63}

UNITS = {
    "Length":  {"u":["mm","cm","m","km","inch","ft","yard","mile"],
                "f":{"mm":0.001,"cm":0.01,"m":1,"km":1000,"inch":0.0254,"ft":0.3048,"yard":0.9144,"mile":1609.344}},
    "Weight":  {"u":["mg","g","kg","oz","lb"],
                "f":{"mg":1e-6,"g":0.001,"kg":1,"oz":0.0283495,"lb":0.453592}},
    "Temp":    {"u":["C","F","K"],"special":True},
    "Area":    {"u":["cm2","m2","km2","ft2","acre"],
                "f":{"cm2":0.0001,"m2":1,"km2":1e6,"ft2":0.092903,"acre":4046.86}},
    "Speed":   {"u":["m/s","km/h","mph","knot"],
                "f":{"m/s":1,"km/h":1/3.6,"mph":0.44704,"knot":0.514444}},
    "Data":    {"u":["byte","KB","MB","GB","TB"],
                "f":{"byte":1,"KB":1024,"MB":1048576,"GB":1073741824,"TB":1099511627776}},
}

def uconv(val, frm, to, cat):
    d = UNITS[cat]
    if d.get("special"):
        k = val+273.15 if frm=="C" else (val-32)*5/9+273.15 if frm=="F" else val
        return k-273.15 if to=="C" else (k-273.15)*9/5+32 if to=="F" else k
    return val * d["f"][frm] / d["f"][to]


class Engine:
    def __init__(self):
        self.disp="0"; self.op=None; self.prev=None; self.new=True
        self.expr=""; self.mem=0.0; self.deg=True; self.hist=[]

    def fmt(self, n):
        if math.isnan(n): return "Error"
        if math.isinf(n): return "Infinity"
        r = float("{:.12g}".format(n))
        if r == int(r) and abs(r) < 1e15: return str(int(r))
        return str(r)

    def push(self, expr, res):
        self.hist.insert(0,{"e":expr,"r":res,"t":datetime.now().strftime("%H:%M")})
        if len(self.hist)>80: self.hist.pop()

    def press(self, v):
        SYM={"+":"+","-":"-","*":"x","/":"/"+":",  "^":"^"}
        SYM={"+":"+","-":"-","*":"x","/":"div","^":"^"}
        n=0.0
        try: n=float(self.disp)
        except: pass

        if v=="C":
            self.disp="0";self.op=None;self.prev=None;self.new=True;self.expr=""
        elif v=="CE":
            self.disp="0";self.new=True
        elif v=="back":
            if not self.new and self.disp not in("Error","Infinity"):
                self.disp=self.disp[:-1] or "0"
        elif v=="sign":
            try: self.disp=self.fmt(-float(self.disp))
            except: pass
        elif v=="%":
            if self.prev and self.op in("+","-"):
                self.disp=self.fmt(float(self.prev)*n/100)
            else:
                self.disp=self.fmt(n/100)
        elif v=="=":
            if self.op and self.prev is not None:
                a=float(self.prev); b=n
                sym={"+":" + ","-":" - ","*":" x ","/":"  /  ","^":"^"}
                ex=self.prev+(sym.get(self.op," ? "))+self.disp
                try:
                    if self.op=="+": r=a+b
                    elif self.op=="-": r=a-b
                    elif self.op=="*": r=a*b
                    elif self.op=="/": r=a/b if b else float("nan")
                    elif self.op=="^": r=a**b
                    else: r=float("nan")
                except: r=float("nan")
                self.disp=self.fmt(r)
                self.push(ex,self.disp)
                self.op=None;self.prev=None;self.new=True
                self.expr=ex+" ="
        elif v in("+","-","*","/","^"):
            if self.op and self.prev is not None and not self.new:
                a=float(self.prev); b=n
                try:
                    if self.op=="+": r=a+b
                    elif self.op=="-": r=a-b
                    elif self.op=="*": r=a*b
                    elif self.op=="/": r=a/b if b else float("nan")
                    elif self.op=="^": r=a**b
                    else: r=float("nan")
                except: r=float("nan")
                self.disp=self.fmt(r)
            sym={"+":" + ","-":" - ","*":" x ","/":"  /  ","^":"^"}
            self.op=v; self.prev=self.disp; self.new=True
            self.expr=self.disp+(sym.get(v," "))
        elif v==".":
            if self.new: self.disp="0."; self.new=False
            elif "." not in self.disp: self.disp+="."
        elif v in("MC","MR","M+","M-","MS"):
            if v=="MC": self.mem=0.0
            elif v=="MR": self.disp=self.fmt(self.mem); self.new=False
            elif v=="M+": self.mem+=n
            elif v=="M-": self.mem-=n
            elif v=="MS": self.mem=n
        else:
            tr=lambda x: x*math.pi/180 if self.deg else x
            ta=lambda x: x*180/math.pi if self.deg else x
            sci={
                "sin":lambda:self.fmt(math.sin(tr(n))),
                "cos":lambda:self.fmt(math.cos(tr(n))),
                "tan":lambda:(self.fmt(math.tan(tr(n))) if abs(math.cos(tr(n)))>1e-12 else "Error"),
                "asin":lambda:self.fmt(ta(math.asin(max(-1,min(1,n))))),
                "acos":lambda:self.fmt(ta(math.acos(max(-1,min(1,n))))),
                "atan":lambda:self.fmt(ta(math.atan(n))),
                "log":lambda:(self.fmt(math.log10(n)) if n>0 else "Error"),
                "ln":lambda:(self.fmt(math.log(n)) if n>0 else "Error"),
                "sqrt":lambda:(self.fmt(math.sqrt(n)) if n>=0 else "Error"),
                "cbrt":lambda:self.fmt(math.copysign(abs(n)**(1/3),n)),
                "x2":lambda:self.fmt(n*n),
                "x3":lambda:self.fmt(n*n*n),
                "inv":lambda:(self.fmt(1/n) if n!=0 else "Error"),
                "fact":lambda:(self.fmt(float(math.factorial(int(abs(n))))) if 0<=n<=170 else "Overflow"),
                "ex":lambda:self.fmt(math.exp(n)),
                "10x":lambda:self.fmt(10**n),
                "pi":lambda:"PI",
                "ec":lambda:"EC",
            }
            if v in sci:
                r=sci[v]()
                if r=="PI": self.disp=self.fmt(math.pi); self.new=False
                elif r=="EC": self.disp=self.fmt(math.e); self.new=False
                else: self.disp=r; self.new=True
            elif v.isdigit():
                if self.new: self.disp=v; self.new=False
                elif self.disp=="0": self.disp=v
                else: self.disp+=v


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("322x502")
        self.minsize(322,502)
        self.maxsize(600,900)
        self.configure(fg_color=BG)
        self.resizable(True,True)
        self.eng=Engine()
        self.rates=FALLBACK.copy()
        self._cur="n"
        self._build()
        self.bind("<Key>",self._key)
        threading.Thread(target=self._fetch,daemon=True).start()

    def _b(self, parent, label, cmd, bg, hv, fg=TEXT, fs=17):
        b=ctk.CTkButton(parent,text=label,command=cmd,
                        fg_color=bg,hover_color=hv,text_color=fg,
                        font=ctk.CTkFont("Segoe UI",fs,"bold"),
                        corner_radius=3,border_width=0,height=1)
        return b

    def _g(self,w,r,c,rs=1,cs=1):
        w.grid(row=r,column=c,rowspan=rs,columnspan=cs,sticky="nsew",padx=1,pady=1)

    def _nb(self,p,t,v): return self._b(p,t,lambda:self._press(v),S1,S1H)
    def _ob(self,p,t,v): return self._b(p,t,lambda:self._press(v),S2,S2H,ACC)
    def _ub(self,p,t,v): return self._b(p,t,lambda:self._press(v),S3,S3H)
    def _sb(self,p,t,v): return self._b(p,t,lambda:self._press(v),S2,S2H,"#06d6a0",12)
    def _mb(self,p,t,v): return self._b(p,t,lambda:self._press(v),S1,S1H,"#b0a0ee",11)
    def _eb(self,p):     return self._b(p,"=",lambda:self._press("="),EQ,EQH,TEXT,20)

    def _build(self):
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)

        # tab bar
        tb=ctk.CTkFrame(self,fg_color="#141414",height=34,corner_radius=0)
        tb.grid(row=0,column=0,sticky="ew")
        for i in range(5): tb.grid_columnconfigure(i,weight=1)
        self._tabs={}
        for i,(lbl,key) in enumerate([("Normal","n"),("Scientific","s"),
                                       ("Currency","c"),("Units","u"),("History","h")]):
            b=ctk.CTkButton(tb,text=lbl,fg_color="transparent",hover_color="#2a2a2a",
                            text_color=TEXT2,font=ctk.CTkFont("Segoe UI",10,"bold"),
                            corner_radius=0,height=34,command=lambda k=key:self._tab(k))
            b.grid(row=0,column=i,sticky="nsew")
            self._tabs[key]=b

        self._disp_lbls={}   # key -> (elbl, mlbl, memlbl)
        self._panels={}
        self._panels["n"]=self._pnormal()
        self._panels["s"]=self._psci()
        self._panels["c"]=self._pcurr()
        self._panels["u"]=self._punits()
        self._panels["h"]=self._phist()
        self._tab("n")

    def _tab(self,key):
        self._cur=key
        for k,p in self._panels.items():
            if k==key: p.grid(row=1,column=0,sticky="nsew")
            else: p.grid_remove()
        for k,b in self._tabs.items():
            b.configure(fg_color=(S2 if k==key else "transparent"),
                        text_color=(TEXT if k==key else TEXT2))
        if key=="h": self._rhist()
        if key in("n","s"): self._upd()

    def _mkdisp(self, parent):
        """Build display area and return (expr_lbl, main_lbl, mem_lbl) for that panel."""
        df=ctk.CTkFrame(parent,fg_color=BG,corner_radius=0)
        df.pack(fill="x",padx=0,pady=0)
        elbl=ctk.CTkLabel(df,text="",text_color=TEXT2,
                           font=ctk.CTkFont("Segoe UI",12),anchor="e",height=20)
        elbl.pack(fill="x",padx=14,pady=(12,0))
        mlbl=ctk.CTkLabel(df,text="0",text_color=TEXT,
                           font=ctk.CTkFont("Segoe UI",46,"normal"),anchor="e",height=56)
        mlbl.pack(fill="x",padx=14,pady=(0,2))
        memlbl=ctk.CTkLabel(df,text="",text_color=TEXT2,
                             font=ctk.CTkFont("Segoe UI",10),anchor="w",height=14)
        memlbl.pack(fill="x",padx=14,pady=(0,6))
        return elbl, mlbl, memlbl

    def _upd(self):
        d=self.eng.disp
        fs=46 if len(d)<=10 else (34 if len(d)<=15 else 22)
        # update whichever panel is currently active
        lbls=self._disp_lbls.get(self._cur)
        if not lbls: return
        elbl,mlbl,memlbl=lbls
        mlbl.configure(text=d,font=ctk.CTkFont("Segoe UI",fs,"normal"))
        elbl.configure(text=self.eng.expr)
        memlbl.configure(text=("M = "+self.eng.fmt(self.eng.mem)) if self.eng.mem else "")

    def _press(self,v):
        self.eng.press(v); self._upd()

    # ── Normal ─────────────────────────────────────────────────────────────────
    def _pnormal(self):
        f=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        f.grid_columnconfigure(0,weight=1)
        f.grid_rowconfigure(1,weight=1)
        self._disp_lbls["n"]=self._mkdisp(f)
        g=ctk.CTkFrame(f,fg_color=BG,corner_radius=0)
        g.pack(fill="both",expand=True,padx=2,pady=(0,2))
        for c in range(4): g.grid_columnconfigure(c,weight=1)
        for r in range(6): g.grid_rowconfigure(r,weight=1)

        # row 0 memory
        for c,(t,v) in enumerate([("MC","MC"),("MR","MR"),("M+","M+"),("M-","M-")]):
            self._g(self._mb(g,t,v),0,c)
        # row 1
        self._g(self._ub(g,"AC","C"),1,0)
        self._g(self._ub(g,"+/-","sign"),1,1)
        self._g(self._ub(g,"%","%"),1,2)
        self._g(self._ob(g,"/","/"),1,3)
        # rows 2-4
        nums=[[("7","7"),("8","8"),("9","9"),("x","*")],
              [("4","4"),("5","5"),("6","6"),("-","-")],
              [("1","1"),("2","2"),("3","3"),("+","+")]]
        for r,row in enumerate(nums):
            for c,(t,v) in enumerate(row):
                w=self._ob(g,t,v) if c==3 else self._nb(g,t,v)
                self._g(w,r+2,c)
        # row 5
        self._g(self._nb(g,"0","0"),5,0,cs=2)
        self._g(self._nb(g,".","." ),5,2)
        self._g(self._eb(g),5,3)
        return f

    # ── Scientific ─────────────────────────────────────────────────────────────
    def _psci(self):
        f=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        f.grid_columnconfigure(0,weight=1)
        f.grid_rowconfigure(1,weight=1)
        self._disp_lbls["s"]=self._mkdisp(f)
        g=ctk.CTkFrame(f,fg_color=BG,corner_radius=0)
        g.pack(fill="both",expand=True,padx=2,pady=(0,2))
        for c in range(5): g.grid_columnconfigure(c,weight=1)
        for r in range(10): g.grid_rowconfigure(r,weight=1)

        # row 0 memory
        for c,(t,v) in enumerate([("MC","MC"),("MR","MR"),("M+","M+"),("M-","M-"),("MS","MS")]):
            self._g(self._mb(g,t,v),0,c)
        # row 1-2 trig
        for c,(t,v) in enumerate([("sin","sin"),("cos","cos"),("tan","tan"),("log","log"),("ln","ln")]):
            self._g(self._sb(g,t,v),1,c)
        for c,(t,v) in enumerate([("sin-1","asin"),("cos-1","acos"),("tan-1","atan"),("Sqrt","sqrt"),("Cbrt","cbrt")]):
            self._g(self._sb(g,t,v),2,c)
        # row 3
        for c,(t,v) in enumerate([("x^2","x2"),("x^3","x3"),("x^n","^"),("1/x","inv"),("n!","fact")]):
            self._g(self._sb(g,t,v),3,c)
        # row 4
        for c,(t,v) in enumerate([("pi","pi"),("e","ec"),("e^x","ex"),("10^x","10x")]):
            self._g(self._sb(g,t,v),4,c)
        self._degbtn=self._b(g,"DEG",self._togdeg,"#252510","#353520","#ffcc00",11)
        self._g(self._degbtn,4,4)

        # row 5: AC CE % / Backspace
        self._g(self._ub(g,"AC","C"),5,0)
        self._g(self._ub(g,"CE","CE"),5,1)
        self._g(self._ub(g,"%","%"),5,2)
        self._g(self._ob(g,"/","/"),5,3)
        self._g(self._ub(g,"<-","back"),5,4)

        # rows 6-7: 7-8-9-x-  /  4-5-6-+-(blank)
        for c,(t,v) in enumerate([("7","7"),("8","8"),("9","9"),("x","*"),("-","-")]):
            w=self._ob(g,t,v) if c>=3 else self._nb(g,t,v)
            self._g(w,6,c)
        for c,(t,v) in enumerate([("4","4"),("5","5"),("6","6"),("+","+")]):
            w=self._ob(g,t,v) if c==3 else self._nb(g,t,v)
            self._g(w,7,c)
        # row 7 col 4 blank
        # rows 8-9: 1-2-3-= / 0(wide)-.-
        for c,(t,v) in enumerate([("1","1"),("2","2"),("3","3")]):
            self._g(self._nb(g,t,v),8,c)
        self._g(self._eb(g),8,3,rs=2,cs=2)
        self._g(self._nb(g,"0","0"),9,0,cs=2)
        self._g(self._nb(g,".","." ),9,2)
        return f

    def _togdeg(self):
        self.eng.deg=not self.eng.deg
        self._degbtn.configure(text="DEG" if self.eng.deg else "RAD")

    # ── Currency ───────────────────────────────────────────────────────────────
    def _pcurr(self):
        f=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        top=ctk.CTkFrame(f,fg_color=S1,corner_radius=6)
        top.pack(fill="x",padx=8,pady=(10,4))
        top.grid_columnconfigure(0,weight=1)

        def row(parent, eattr, sattr, defsel, ro=False):
            r=ctk.CTkFrame(parent,fg_color="transparent")
            r.pack(fill="x",padx=8,pady=4)
            r.grid_columnconfigure(0,weight=1)
            kw={"state":"readonly"} if ro else {}
            e=ctk.CTkEntry(r,fg_color=S2,border_color=BRD,text_color=(ACC if ro else TEXT),
                           font=ctk.CTkFont("Segoe UI",18,"bold"),height=38,**kw)
            e.pack(side="left",fill="x",expand=True,padx=(0,6))
            if not ro:
                e.insert(0,"1")
                e.bind("<KeyRelease>",lambda ev:self._dcurr())
            setattr(self,eattr,e)
            s=ctk.CTkComboBox(r,values=CURRENCIES,width=88,
                               fg_color=S2,border_color=BRD,button_color=S2,
                               text_color=TEXT,font=ctk.CTkFont("Segoe UI",11,"bold"),
                               command=lambda ev:self._dcurr())
            s.set(defsel); s.pack(side="left")
            setattr(self,sattr,s)

        row(top,"_cfe","_cfs","USD")
        ctk.CTkLabel(top,text="=",text_color=TEXT2,font=ctk.CTkFont("Segoe UI",14)).pack()
        row(top,"_cte","_cts","BDT",ro=True)

        self._ratelbl=ctk.CTkLabel(f,text="Loading...",text_color=TEXT2,
                                    font=ctk.CTkFont("Segoe UI",10))
        self._ratelbl.pack(pady=2)

        g=ctk.CTkFrame(f,fg_color=BG,corner_radius=0)
        g.pack(fill="both",expand=True,padx=2,pady=(0,2))
        for c in range(4): g.grid_columnconfigure(c,weight=1)
        for r in range(4): g.grid_rowconfigure(r,weight=1)

        pad=[
            [("7","7","n"),("8","8","n"),("9","9","n"),("AC","cc","u")],
            [("4","4","n"),("5","5","n"),("6","6","n"),("Swap","sw","o")],
            [("1","1","n"),("2","2","n"),("3","3","n"),("<-","bc","u")],
            [("0","0","n",2),(".",".", "n")],
        ]
        for ri,row in enumerate(pad):
            ci=0
            for item in row:
                t,v,s=item[0],item[1],item[2]; cs_=item[3] if len(item)>3 else 1
                cmd=lambda val=v:self._cnum(val)
                if s=="n": w=self._b(g,t,cmd,S1,S1H)
                elif s=="o": w=self._b(g,t,cmd,S2,S2H,ACC)
                else: w=self._b(g,t,cmd,S3,S3H)
                self._g(w,ri,ci,cs=cs_); ci+=cs_
        return f

    def _dcurr(self):
        try:
            amt=float(self._cfe.get() or "0")
            frm,to=self._cfs.get(),self._cts.get()
            if frm in self.rates and to in self.rates:
                res=amt*self.rates[to]/self.rates[frm]
                self._cte.configure(state="normal")
                self._cte.delete(0,"end"); self._cte.insert(0,"{:.4f}".format(res))
                self._cte.configure(state="readonly")
                rate=self.rates[to]/self.rates[frm]
                self._ratelbl.configure(text="1 {}  =  {:.6f} {}".format(frm,rate,to))
        except: pass

    def _cnum(self,v):
        e=self._cfe; cur=e.get()
        if v=="cc": e.delete(0,"end")
        elif v=="bc": e.delete(len(cur)-1,"end")
        elif v=="sw":
            f,t=self._cfs.get(),self._cts.get()
            self._cfs.set(t); self._cts.set(f)
            val=self._cte.get(); e.delete(0,"end"); e.insert(0,val)
        elif v=="." and "." in cur: return
        else: e.insert("end",v)
        self._dcurr()

    def _fetch(self):
        try:
            with urllib.request.urlopen("https://api.exchangerate-api.com/v4/latest/USD",timeout=5) as r:
                self.rates=json.loads(r.read())["rates"]
            self.after(0,lambda:self._ratelbl.configure(text="Live rates loaded"))
            self.after(0,self._dcurr)
        except:
            self.after(0,lambda:self._ratelbl.configure(text="Offline rates"))

    # ── Units ──────────────────────────────────────────────────────────────────
    def _punits(self):
        f=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        cats=list(UNITS.keys())
        seg=ctk.CTkSegmentedButton(f,values=cats,fg_color=S1,
                                    selected_color=EQ,selected_hover_color=EQH,
                                    unselected_color=S1,unselected_hover_color=S2,
                                    text_color=TEXT2,font=ctk.CTkFont("Segoe UI",10,"bold"),
                                    command=self._ucat)
        seg.pack(fill="x",padx=8,pady=(10,4)); seg.set(cats[0])
        self._useg=seg

        card=ctk.CTkFrame(f,fg_color=S1,corner_radius=6)
        card.pack(fill="x",padx=8,pady=4)
        card.grid_columnconfigure(0,weight=1)

        def urow(parent, eattr, sattr, defsel, ro=False):
            r=ctk.CTkFrame(parent,fg_color="transparent")
            r.pack(fill="x",padx=8,pady=4)
            r.grid_columnconfigure(0,weight=1)
            kw={"state":"readonly"} if ro else {}
            e=ctk.CTkEntry(r,fg_color=S2,border_color=BRD,text_color=(ACC if ro else TEXT),
                           font=ctk.CTkFont("Segoe UI",18,"bold"),height=38,**kw)
            e.pack(side="left",fill="x",expand=True,padx=(0,6))
            if not ro:
                e.insert(0,"1")
                e.bind("<KeyRelease>",lambda ev:self._dunit())
            setattr(self,eattr,e)
            u0=UNITS[cats[0]]["u"]
            s=ctk.CTkComboBox(r,values=u0,width=90,
                               fg_color=S2,border_color=BRD,button_color=S2,
                               text_color=TEXT,font=ctk.CTkFont("Segoe UI",11,"bold"),
                               command=lambda ev:self._dunit())
            s.set(u0[0 if not ro else 1]); s.pack(side="left")
            setattr(self,sattr,s)

        urow(card,"_ufe","_ufs","m")
        ctk.CTkLabel(card,text="=",text_color=TEXT2,font=ctk.CTkFont("Segoe UI",14)).pack()
        urow(card,"_ute","_uts","km",ro=True)

        g=ctk.CTkFrame(f,fg_color=BG,corner_radius=0)
        g.pack(fill="both",expand=True,padx=2,pady=(0,2))
        for c in range(4): g.grid_columnconfigure(c,weight=1)
        for r in range(4): g.grid_rowconfigure(r,weight=1)
        pad=[
            [("7","7","n"),("8","8","n"),("9","9","n"),("AC","cu","u")],
            [("4","4","n"),("5","5","n"),("6","6","n"),("Swap","su","o")],
            [("1","1","n"),("2","2","n"),("3","3","n"),("<-","bu","u")],
            [("0","0","n",2),(".",".", "n")],
        ]
        for ri,row in enumerate(pad):
            ci=0
            for item in row:
                t,v,s=item[0],item[1],item[2]; cs_=item[3] if len(item)>3 else 1
                cmd=lambda val=v:self._unum(val)
                if s=="n": w=self._b(g,t,cmd,S1,S1H)
                elif s=="o": w=self._b(g,t,cmd,S2,S2H,ACC)
                else: w=self._b(g,t,cmd,S3,S3H)
                self._g(w,ri,ci,cs=cs_); ci+=cs_
        return f

    def _ucat(self,cat):
        us=UNITS[cat]["u"]
        self._ufs.configure(values=us); self._ufs.set(us[0])
        self._uts.configure(values=us); self._uts.set(us[1] if len(us)>1 else us[0])
        self._dunit()

    def _dunit(self):
        try:
            amt=float(self._ufe.get() or "0")
            frm,to=self._ufs.get(),self._uts.get()
            cat=self._useg.get()
            res=uconv(amt,frm,to,cat)
            disp=("{:.6e}".format(res) if (abs(res)<0.0001 and res!=0) or abs(res)>1e10
                  else str(float("{:.10g}".format(res))))
            self._ute.configure(state="normal")
            self._ute.delete(0,"end"); self._ute.insert(0,disp)
            self._ute.configure(state="readonly")
        except: pass

    def _unum(self,v):
        e=self._ufe; cur=e.get()
        if v=="cu": e.delete(0,"end")
        elif v=="bu": e.delete(len(cur)-1,"end")
        elif v=="su":
            f,t=self._ufs.get(),self._uts.get()
            self._ufs.set(t); self._uts.set(f)
            val=self._ute.get(); e.delete(0,"end"); e.insert(0,val)
        elif v=="." and "." in cur: return
        else: e.insert("end",v)
        self._dunit()

    # ── History ────────────────────────────────────────────────────────────────
    def _phist(self):
        f=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        hdr=ctk.CTkFrame(f,fg_color="transparent")
        hdr.pack(fill="x",padx=12,pady=(10,4))
        ctk.CTkLabel(hdr,text="History",text_color=TEXT,
                     font=ctk.CTkFont("Segoe UI",13,"bold")).pack(side="left")
        ctk.CTkButton(hdr,text="Clear",fg_color=S3,hover_color=S3H,text_color=TEXT,
                      font=ctk.CTkFont("Segoe UI",10,"bold"),corner_radius=4,width=60,
                      height=26,command=self._clrhist).pack(side="right")
        self._hscroll=ctk.CTkScrollableFrame(f,fg_color=S1,corner_radius=8,
                                              scrollbar_button_color=S2)
        self._hscroll.pack(fill="both",expand=True,padx=12,pady=(0,10))
        self._hscroll.grid_columnconfigure(0,weight=1)
        return f

    def _rhist(self):
        for w in self._hscroll.winfo_children(): w.destroy()
        if not self.eng.hist:
            ctk.CTkLabel(self._hscroll,text="No history yet",text_color=TEXT2,
                          font=ctk.CTkFont("Segoe UI",12)).pack(pady=20)
            return
        for item in self.eng.hist:
            row=ctk.CTkFrame(self._hscroll,fg_color=S2,corner_radius=6)
            row.pack(fill="x",pady=2,padx=4)
            row.grid_columnconfigure(0,weight=1)
            ctk.CTkLabel(row,text=item["e"],text_color=TEXT2,
                          font=ctk.CTkFont("Segoe UI",11),anchor="e").grid(
                          row=0,column=0,sticky="ew",padx=10,pady=(6,1))
            ctk.CTkLabel(row,text=item["r"],text_color=TEXT,
                          font=ctk.CTkFont("Segoe UI",18,"bold"),anchor="e").grid(
                          row=1,column=0,sticky="ew",padx=10,pady=(0,6))
            def use(val=item["r"]):
                self.eng.disp=val; self.eng.new=True
                self._tab("n"); self._upd()
            row.bind("<Button-1>",lambda e,fn=use:fn())
            for c in row.winfo_children():
                c.bind("<Button-1>",lambda e,fn=use:fn())

    def _clrhist(self):
        self.eng.hist.clear(); self._rhist()

    # ── Keyboard ───────────────────────────────────────────────────────────────
    def _key(self,e):
        if self._cur not in("n","s"): return
        k,c=e.keysym,e.char
        if c in "0123456789": self._press(c)
        elif c in "+-*/": self._press(c)
        elif c==".": self._press(".")
        elif c in("=","\r") or k=="Return": self._press("=")
        elif k=="BackSpace": self._press("back")
        elif k=="Escape": self._press("C")
        elif c=="%": self._press("%")


if __name__=="__main__":
    App().mainloop()