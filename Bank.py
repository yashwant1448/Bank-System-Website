import math
import random
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

F = "Segoe UI"
BLUE, GREEN, RED, MINT = "#2878D0", "#16A36A", "#E05252", "#58E6A5"
T = {
    "light": dict(bg="#F1F5F9", card="#FFFFFF", fg="#0F172A", mute="#64748B", bd="#E2E8F0", side="#142D4E", chip="#E5F0FF"),
    "dark": dict(bg="#0B1220", card="#131C2E", fg="#E6EDF7", mute="#8A9BB5", bd="#22304A", side="#0D1830", chip="#1B2A47"),
}


def mix(a, b, t):
    x, y = [[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in (a, b)]
    return "#%02x%02x%02x" % tuple(round(p + (q - p) * t) for p, q in zip(x, y))


def inr(x):
    return f"₹ {x:,.2f}"


def val(e):
    return "" if e.empty else e.get().strip()


class Btn(tk.Canvas):
    """Rounded canvas button with a smooth hover fade."""

    def __init__(s, p, text, cmd, bg, fg="white", hov=None, w=100, h=42, r=12, left=False):
        super().__init__(p, width=w, height=h, bg=p.cget("bg"), highlightthickness=0, cursor="hand2")
        s.txt, s.fg, s.r, s.left, s.job = text, fg, r, left, None
        s.base, s.hov, s.cur = bg, hov or mix(bg, "#000000", .18), bg
        s.bind("<Configure>", lambda e: s.draw())
        s.bind("<Enter>", lambda e: s.fade(s.hov))
        s.bind("<Leave>", lambda e: s.fade(s.base))
        s.bind("<Button-1>", lambda e: cmd())

    def draw(s):
        s.delete("all")
        w, h, r = s.winfo_width(), s.winfo_height(), s.r
        pts = [1 + r, 1, w - 1 - r, 1, w - 1, 1, w - 1, 1 + r, w - 1, h - 1 - r, w - 1, h - 1, w - 1 - r, h - 1,
               1 + r, h - 1, 1, h - 1, 1, h - 1 - r, 1, 1 + r, 1, 1]
        s.create_polygon(pts, smooth=True, fill=s.cur, outline=s.cur)
        s.create_text(20 if s.left else w / 2, h / 2, text=s.txt, fill=s.fg, font=(F, 10, "bold"),
                      anchor="w" if s.left else "center")

    def fade(s, to):
        if s.job:
            s.after_cancel(s.job)
        a = s.cur

        def tick(i=1):
            if not s.winfo_exists():
                return
            s.cur = mix(a, to, i / 6)
            s.draw()
            s.job = s.after(15, tick, i + 1) if i < 6 else None
        tick()

    def set(s, bg, fg=None):
        s.base, s.hov = bg, mix(bg, "#000000", .18)
        s.fg = fg or s.fg
        s.fade(bg)


class App:
    def __init__(s, root):
        s.root, s.mode, s.page, s.flt = root, "light", "home", "All"
        s.name, s.acc, s.bal, s.shown, s.tx = None, "", 0.0, 0.0, []
        s.hide, s.fx, s.tint = False, False, MINT
        root.title("Smart Bank")
        root.geometry("1100x760")
        root.minsize(960, 700)
        s.build()

    c = property(lambda s: T[s.mode])

    # ---------- layout ----------
    def build(s):
        c = s.c
        for w in s.root.winfo_children():
            w.destroy()
        s.root.configure(bg=c["bg"])
        side = tk.Frame(s.root, bg=c["side"], width=215)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="◆ SMART BANK", bg=c["side"], fg="white", font=(F, 16, "bold")).pack(pady=(28, 20))
        av = tk.Canvas(side, width=76, height=76, bg=c["side"], highlightthickness=0)
        av.pack()
        av.create_oval(3, 3, 73, 73, fill=BLUE, outline="#6FB0FF", width=2)
        av.create_text(38, 38, text=(s.name or "?")[0].upper(), fill="white", font=(F, 28, "bold"))
        tk.Label(side, text=s.name or "Guest", bg=c["side"], fg="white", font=(F, 12, "bold")).pack(pady=(8, 0))
        tk.Label(side, text="Savings Account" if s.name else "No account yet", bg=c["side"], fg="#8FB4E0",
                 font=(F, 9)).pack(pady=(0, 22))
        for key, text in (("home", "⌂    Dashboard"), ("hist", "⇄    Transactions")):
            on = s.page == key
            Btn(side, text, lambda k=key: s.go(k), BLUE if on else c["side"], hov=BLUE if on else mix(c["side"], BLUE, .4),
                left=True, h=44).pack(fill="x", padx=14, pady=3)
        clk = tk.Label(side, bg=c["side"], fg="#A9D6FF", font=(F, 10, "bold"))
        clk.pack(side="bottom", pady=18)
        Btn(side, "☀    Light mode" if s.mode == "dark" else "☾    Dark mode", s.flip, c["side"],
            hov=mix(c["side"], BLUE, .4), left=True, h=44).pack(side="bottom", fill="x", padx=14)

        def tick():
            if clk.winfo_exists():
                clk.config(text=datetime.now().strftime("%d %b %Y\n%I:%M:%S %p"))
                s.root.after(1000, tick)
        tick()
        s.main = tk.Frame(s.root, bg=c["bg"])
        s.main.pack(side="left", fill="both", expand=True, padx=30, pady=24)
        getattr(s, s.page)()

    def go(s, page):
        s.page = page
        s.build()

    def flip(s):
        s.mode = "dark" if s.mode == "light" else "light"
        s.build()

    # ---------- helpers ----------
    def card(s, p):
        return tk.Frame(p, bg=s.c["card"], highlightbackground=s.c["bd"], highlightthickness=1)

    def ent(s, p, ph):
        c = s.c
        e = tk.Entry(p, font=(F, 12), bg=c["bg"], fg=c["mute"], relief="flat", insertbackground=c["fg"],
                     highlightthickness=2, highlightbackground=c["bd"], highlightcolor=BLUE)
        e.insert(0, ph)
        e.empty = True

        def fin(_):
            if e.empty:
                e.delete(0, "end")
                e.config(fg=c["fg"])
                e.empty = False

        def fout(_):
            if not e.get():
                e.insert(0, ph)
                e.config(fg=c["mute"])
                e.empty = True
        e.bind("<FocusIn>", fin)
        e.bind("<FocusOut>", fout)
        return e

    def bad(s, e, msg):
        s.toast(msg, RED, "✖")
        e.config(highlightbackground=RED, highlightcolor=RED)
        s.root.after(800, lambda: e.winfo_exists() and e.config(highlightbackground=s.c["bd"], highlightcolor=BLUE))

    def toast(s, msg, color=GREEN, icon="✔"):
        l = tk.Label(s.root, text=f"{icon}   {msg}", bg=color, fg="white", font=(F, 11, "bold"), padx=20, pady=12)

        def slide(i=0):
            if not l.winfo_exists():
                return
            l.place(relx=1, rely=1, x=-24, y=70 - 94 * (1 - (1 - i / 8) ** 3), anchor="se")
            l.lift()
            if i < 8:
                s.root.after(16, slide, i + 1)
            else:
                s.root.after(2400, l.destroy)
        slide()

    def amount(s, e, zero=False):
        try:
            v = round(float(val(e).replace(",", "")), 2)
            if not math.isfinite(v) or v < 0 or (v == 0 and not zero) or v > 1e9:
                raise ValueError
            return v
        except ValueError:
            s.bad(e, "Enter a valid amount")

    def countup(s, lbl, target, fmt):
        def f(i=1):
            if lbl.winfo_exists():
                lbl.config(text=fmt(target * (1 - (1 - i / 20) ** 3)))
                if i < 20:
                    s.root.after(25, f, i + 1)
        f()

    def confetti(s, cv):
        if not cv.winfo_exists():
            return
        w = cv.winfo_width()
        ps = [[random.uniform(0, w), random.uniform(-30, 0), random.uniform(-2, 2), random.uniform(1, 4),
               cv.create_rectangle(0, 0, 7, 7, outline="", fill=random.choice(["#58E6A5", "#FFD166", "#FF7B9C", "#7CC4FF", "#FFFFFF"]))]
              for _ in range(70)]

        def step(n=0):
            if not cv.winfo_exists():
                return
            for p in ps:
                p[0] += p[2]
                p[1] += p[3]
                p[3] += .3
                cv.coords(p[4], p[0], p[1], p[0] + 7, p[1] + 7)
            if n < 50:
                s.root.after(25, step, n + 1)
            else:
                [cv.delete(p[4]) for p in ps]
        step()

    # ---------- actions ----------
    def log(s, action, v, sign):
        s.tx.append((action, v, sign, s.bal, datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")))

    def create(s):
        n = val(s.name_e)
        if len(n) < 2:
            return s.bad(s.name_e, "Enter a valid name")
        v = s.amount(s.amt_e, True)
        if v is None:
            return
        s.name, s.bal, s.shown, s.fx, s.tint = n.title(), v, 0.0, True, MINT
        s.acc = str(random.randint(1000, 9999))
        s.log("Account Created", v, 1)
        s.go("home")
        s.toast(f"Welcome {s.name}! Your account is ready")

    def move(s, sign):
        v = s.amount(s.amt_e)
        if v is None:
            return
        if sign < 0 and v > s.bal:
            return s.bad(s.amt_e, "Insufficient balance")
        word = "Deposit" if sign > 0 else "Withdraw"
        if not messagebox.askyesno(f"Confirm {word}", f"{word} {inr(v)}?"):
            return
        s.bal = round(s.bal + sign * v, 2)
        s.log("Deposit" if sign > 0 else "Withdrawal", v, sign)
        s.fx, s.tint = sign > 0, MINT if sign > 0 else "#FF9B9B"
        s.go("home")
        s.toast(f"{'Deposited' if sign > 0 else 'Withdrew'} {inr(v)}", GREEN if sign > 0 else RED)

    # ---------- pages ----------
    def home(s):
        c, m = s.c, s.main
        h = datetime.now().hour
        g = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"
        tk.Label(m, text=f"{g}, {s.name.split()[0]}" if s.name else "Welcome to Smart Bank",
                 font=(F, 23, "bold"), bg=c["bg"], fg=c["fg"]).pack(anchor="w")
        tk.Label(m, text="Here is your financial overview" if s.name else "Open an account below to get started",
                 font=(F, 10), bg=c["bg"], fg=c["mute"]).pack(anchor="w")

        # --- gradient balance card
        cv = tk.Canvas(m, height=160, highlightthickness=0, bg=c["bg"])
        cv.pack(fill="x", pady=16)
        cv.create_text(30, 34, anchor="w", text="AVAILABLE BALANCE", fill="#BBD9FF", font=(F, 11, "bold"))
        tid = cv.create_text(30, 90, anchor="w", text="", fill=s.tint, font=(F, 34, "bold"))
        cv.create_text(30, 134, anchor="w", fill="#BBD9FF", font=(F, 10),
                       text=f"SAVINGS   ••••  {s.acc}" if s.name else "Create an account to begin")
        eye = cv.create_text(0, 34, anchor="e", fill="#BBD9FF", font=(F, 10, "bold"), text="Show" if s.hide else "Hide")
        show = lambda v: cv.itemconfig(tid, text="₹ ••••••" if s.hide else inr(v))

        def toggle(_):
            s.hide = not s.hide
            cv.itemconfig(eye, text="Show" if s.hide else "Hide")
            show(s.shown)
        cv.tag_bind(eye, "<Button-1>", toggle)
        cv.tag_bind(eye, "<Enter>", lambda e: cv.config(cursor="hand2"))
        cv.tag_bind(eye, "<Leave>", lambda e: cv.config(cursor=""))

        def paint(e):
            w, hh = e.width, e.height
            cv.delete("bg")
            for i in range(48):
                cv.create_rectangle(w * i / 48, 0, w * (i + 1) / 48 + 1, hh, fill=mix("#142D4E", BLUE, i / 47), outline="", tags="bg")
            cv.create_oval(w - 210, -90, w + 60, 180, fill=mix(BLUE, "#FFFFFF", .08), outline="", tags="bg")
            cv.create_oval(w - 130, 50, w + 100, 270, fill=mix(BLUE, "#FFFFFF", .13), outline="", tags="bg")
            pts = [t[3] for t in s.tx]
            if len(pts) > 1:  # sparkline of balance history
                x0, x1, y0, y1 = w * .5, w - 34, 70, hh - 24
                lo, span = min(pts), (max(pts) - min(pts)) or 1
                xy = [(x0 + (x1 - x0) * i / (len(pts) - 1), y1 - (y1 - y0) * (p - lo) / span) for i, p in enumerate(pts)]
                flat = [k for q in xy for k in q]
                cv.create_polygon([x0, y1] + flat + [x1, y1], fill=mix(BLUE, "#FFFFFF", .2), outline="", tags="bg")
                cv.create_line(flat, fill="#D6E8FF", width=3, smooth=True, tags="bg")
                cv.create_oval(x1 - 5, xy[-1][1] - 5, x1 + 5, xy[-1][1] + 5, fill="white", outline="", tags="bg")
            cv.tag_lower("bg")
            cv.coords(eye, w - 30, 34)
        cv.bind("<Configure>", paint)

        a0 = s.shown

        def count(i=1):
            if not cv.winfo_exists():
                return
            s.shown = a0 + (s.bal - a0) * (1 - (1 - i / 26) ** 3)
            show(s.shown)
            if i < 26:
                s.root.after(20, count, i + 1)
            else:
                cv.itemconfig(tid, fill=MINT)
        count()
        if s.fx:
            s.fx = False
            s.root.after(250, lambda: s.confetti(cv))

        # --- stat cards
        dep = sum(t[1] for t in s.tx if t[2] > 0)
        wd = sum(t[1] for t in s.tx if t[2] < 0)
        row = tk.Frame(m, bg=c["bg"])
        row.pack(fill="x")
        for i, (t, v, col, fmt) in enumerate([("DEPOSITS", dep, GREEN, inr), ("WITHDRAWALS", wd, RED, inr),
                                              ("TRANSACTIONS", len(s.tx), BLUE, lambda x: str(round(x)))]):
            row.columnconfigure(i, weight=1, uniform="a")
            f = s.card(row)
            f.grid(row=0, column=i, sticky="ew", padx=6)
            tk.Frame(f, bg=col, height=4).pack(fill="x")
            tk.Label(f, text=t, bg=c["card"], fg=c["mute"], font=(F, 9, "bold")).pack(pady=(12, 0))
            lbl = tk.Label(f, text=fmt(0), bg=c["card"], fg=col, font=(F, 16, "bold"))
            lbl.pack(pady=(0, 14))
            s.countup(lbl, v, fmt)

        # --- form + activity
        low = tk.Frame(m, bg=c["bg"])
        low.pack(fill="both", expand=True, pady=16)
        form, rec = s.card(low), s.card(low)
        form.pack(side="left", fill="both", expand=True, padx=(6, 8))
        rec.pack(side="left", fill="both", expand=True, padx=(8, 6))

        f = tk.Frame(form, bg=c["card"])
        f.pack(fill="x", padx=22, pady=18)
        tk.Label(f, text="BANKING OPERATIONS" if s.name else "OPEN YOUR ACCOUNT", bg=c["card"], fg=c["fg"],
                 font=(F, 12, "bold")).pack(anchor="w", pady=(0, 12))
        if not s.name:
            s.name_e = s.ent(f, "Customer name")
            s.name_e.pack(fill="x", ipady=9, pady=(0, 10))
        s.amt_e = s.ent(f, "Amount (₹)")
        s.amt_e.pack(fill="x", ipady=9)
        s.amt_e.bind("<Return>", lambda e: s.move(1) if s.name else s.create())
        chips = tk.Frame(f, bg=c["card"])
        chips.pack(anchor="w", pady=14)

        def pick(a):
            s.amt_e.delete(0, "end")
            s.amt_e.insert(0, str(a))
            s.amt_e.config(fg=c["fg"])
            s.amt_e.empty = False
        for a in (500, 1000, 2000, 5000):
            Btn(chips, f"₹{a}", lambda a=a: pick(a), c["chip"], fg=BLUE, w=68, h=32, r=16).pack(side="left", padx=(0, 8))
        if s.name:
            b = tk.Frame(f, bg=c["card"])
            b.pack(fill="x")
            Btn(b, "↓   DEPOSIT", lambda: s.move(1), GREEN).pack(side="left", expand=True, fill="x", padx=(0, 5))
            Btn(b, "↑   WITHDRAW", lambda: s.move(-1), RED).pack(side="left", expand=True, fill="x", padx=(5, 0))
        else:
            Btn(f, "CREATE ACCOUNT", s.create, BLUE).pack(fill="x")

        tk.Label(rec, text="RECENT ACTIVITY", bg=c["card"], fg=c["fg"], font=(F, 12, "bold")).pack(anchor="w", padx=22, pady=(18, 6))
        if not s.tx:
            tk.Label(rec, text="◇\nNo transactions yet", bg=c["card"], fg=c["mute"], font=(F, 11)).pack(pady=36)
        for a, v, sg, b, tm in s.tx[-6:][::-1]:
            col = GREEN if sg > 0 else RED
            r = tk.Frame(rec, bg=c["card"])
            r.pack(fill="x", padx=22, pady=5)
            tk.Label(r, text="↓" if sg > 0 else "↑", width=3, fg=col, bg=mix(col, c["card"], .82), font=(F, 12, "bold")).pack(side="left", ipady=5)
            tk.Label(r, text=f"{a}\n{tm}", justify="left", bg=c["card"], fg=c["fg"], font=(F, 9)).pack(side="left", padx=10)
            tk.Label(r, text=("+ " if sg > 0 else "− ") + inr(v), bg=c["card"], fg=col, font=(F, 10, "bold")).pack(side="right")

    def hist(s):
        c, m = s.c, s.main
        tk.Label(m, text="Transaction History", font=(F, 23, "bold"), bg=c["bg"], fg=c["fg"]).pack(anchor="w")
        tk.Label(m, text="Filter by type or search by amount and date", font=(F, 10), bg=c["bg"], fg=c["mute"]).pack(anchor="w")
        bar = tk.Frame(m, bg=c["bg"])
        bar.pack(fill="x", pady=16)
        pills = {}

        def setf(k):
            s.flt = k
            for n, p in pills.items():
                p.set(BLUE if n == k else c["chip"], "white" if n == k else BLUE)
            fill()
        for k in ("All", "Deposits", "Withdrawals"):
            on = s.flt == k
            pills[k] = Btn(bar, k, lambda k=k: setf(k), BLUE if on else c["chip"], fg="white" if on else BLUE, w=112, h=36, r=18)
            pills[k].pack(side="left", padx=(0, 8))
        q = s.ent(bar, "Search…")
        q.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=7)

        st = ttk.Style()
        st.theme_use("clam")
        st.configure("Treeview", background=c["card"], fieldbackground=c["card"], foreground=c["fg"], rowheight=36, borderwidth=0, font=(F, 10))
        st.configure("Treeview.Heading", background=c["side"], foreground="white", font=(F, 10, "bold"), padding=9, relief="flat")
        st.map("Treeview", background=[("selected", BLUE)])
        cols = ("Type", "Amount", "Balance After", "Date & Time")
        tr = ttk.Treeview(m, columns=cols, show="headings")
        for k in cols:
            tr.heading(k, text=k)
            tr.column(k, anchor="center")
        tr.tag_configure("1", foreground=GREEN)
        tr.tag_configure("-1", foreground=RED)
        info = tk.Label(m, bg=c["bg"], fg=c["mute"], font=(F, 9))
        info.pack(side="bottom", anchor="e", pady=(8, 0))

        def fill(*_):
            tr.delete(*tr.get_children())
            t, n = val(q).lower(), 0
            for a, v, sg, b, tm in reversed(s.tx):
                if (s.flt == "Deposits" and sg < 0) or (s.flt == "Withdrawals" and sg > 0):
                    continue
                if t in f"{a} {v:.2f} {tm}".lower():
                    tr.insert("", "end", tags=(str(sg),), values=(a, ("+ " if sg > 0 else "− ") + inr(v), inr(b), tm))
                    n += 1
            info.config(text=f"Showing {n} of {len(s.tx)} transactions")
        q.bind("<KeyRelease>", fill)
        fill()
        tr.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
