import tkinter as tk
from tkinter import messagebox
import os
from synthesis import synthesis as synth
import idlelib.colorizer as ic
import idlelib.percolator as ip
import re


def run():
    root = tk.Tk()
    root.title("pysynth")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, padx=5, pady=2, sticky="news")
    frame.rowconfigure(4, weight=1)
    frame.columnconfigure(0, weight=1)

    implementation = tk.Entry(frame, width=50)
    implementation.insert(0, "write your specifications")
    implementation.grid(row=0, column=0, sticky="news", pady=2)

    example = tk.Entry(frame)
    example.insert(0, "examples/")
    example.grid(row=1, column=0, sticky="news")

    synthesiseResult = tk.StringVar()


    def clicked():
        try:
            lines = synth.import_from(example.get())
        except IOError:
            messagebox.showerror('pysynth error', "No file or directory for example code.")
            return
        if len(lines) == 0:
            for (dirpath, dirnames, filenames) in os.walk(example.get()):
                for file in filenames:
                    path = os.path.join(dirpath, file)
                    if "venv" not in path:
                        lines += synth.import_from(path)
        if len(lines) == 0:
            messagebox.showerror('pysynth error', 'No example code found.')
            return
        try:
            code = synth.synthesize(implementation.get(), lines, 1,
                                    verbose=False,
                                    show_known=False,
                                    single_output=False,
                                    rename_after_each_step=True,
                                    show_remaining=True)[0]
        except Exception as e:
            messagebox.showerror('pysynth error', str(e))
            return
        #code = code.replace("def solution", "def solution")
        text.delete('1.0', tk.END)
        text.insert(tk.END, code)


    tk.Button(frame, text= "Synthesize", command=clicked).grid(row=2, column=0, sticky="news", pady=5)

    resultFrame = tk.Frame(frame, pady=5)
    resultFrame.grid(row=3, column=0, sticky="news")
    resultFrame.rowconfigure(0, weight=1)
    resultFrame.columnconfigure(2, weight=1)

    # Add a Scrollbar(horizontal)
    scroll = tk.Scrollbar(resultFrame, orient='vertical')
    scroll.grid(row=0, column=1, sticky="news")

    # Add a text widget
    text = tk.Text(resultFrame, yscrollcommand=scroll.set)
    cdg = ic.ColorDelegator()
    cdg.prog = re.compile(r'\b(?P<MYGROUP>tkinter)\b|' + ic.make_pat(), re.S)
    cdg.idprog = re.compile(r'\s+(\w+)', re.S)

    cdg.tagdefs['MYGROUP'] = {'foreground': '#7F7F7F', 'background': '#FFFFFF'}

    # These five lines are optional. If omitted, default colours are used.
    cdg.tagdefs['COMMENT'] = {'foreground': '#FF0000', 'background': '#FFFFFF'}
    cdg.tagdefs['KEYWORD'] = {'foreground': '#007F00', 'background': '#FFFFFF'}
    cdg.tagdefs['BUILTIN'] = {'foreground': '#7F7F00', 'background': '#FFFFFF'}
    cdg.tagdefs['STRING'] = {'foreground': '#7F3F00', 'background': '#FFFFFF'}
    cdg.tagdefs['DEFINITION'] = {'foreground': '#007F7F', 'background': '#FFFFFF'}

    ip.Percolator(text).insertfilter(cdg)

    scroll.config(command=text.yview)
    text.grid(row=0, column=0, sticky="news")

    root.mainloop()


if __name__ == "main":
    run()
