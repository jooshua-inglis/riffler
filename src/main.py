# Made by Jooshua :)

from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from PIL import ImageTk, Image, ImageFile
import PIL
from os.path import basename, join, splitext, realpath, dirname
import subprocess
import math
import os
import logging
import PyPDF2
import shutil


from pdf2image import convert_from_path

logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s = %(levelname)s  %(message)s')
ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(join(ROOT_DIR, os.path.pardir))

ICON_DIR = join(ROOT_DIR, "resources", "icons")


class InvalidFileException(Exception):
    pass


class Page:
    def __init__(self, page_number=None, pdf_file=None, path=None, pdf_page=None):
        self.pageNumber = page_number
        self.pdfFile = pdf_file
        self.path = path
        self.pdfPage = pdf_page

        if path:
            load = Image.open(join(ICON_DIR, path))
            width = 150
            height = int(width * math.sqrt(2))
            load = load.resize((width, height), Image.ANTIALIAS)
            self.render = ImageTk.PhotoImage(load)


class PdfFile:
    def __init__(self, path, name):
        self.path = path  # imputed path to pdf file
        self.fileName = name  # name of the pdf file without path or exertion
        self.pdfObj = PyPDF2.PdfFileReader(path)

    def get_images(self):
        # relative path folder of images of our pdf file
        directory = join(ICON_DIR, self.fileName)
        for file in os.listdir(directory):
            # returns file relative to the imgs folder
            yield join(self.fileName, file)



class Main:
    def __init__(self, *args, **kwargs):
        self.pages = []  # List of paths to the icons
        self.files = {}  # List
        self.icons = {}
        self.currentlySelected = Page()

    def hylight(self, page):
        # Called when an icon is clicked, heights the clicked icon,
        # event is a Page object.

        self.currentlySelected = page

    def export(self):
        create_pdf(self.pages)

    def delete_all_pages(self):
        for i in self.icons.keys():
            self.icons[i].destroy()
        self.icons.clear()

    def left(self):
        # Called when the left key is pressed, moves the selected icon to the left
        index = self.pages.index(self.currentlySelected)
        if index == 0:
            return
        self.pages[index] = self.pages[index - 1]
        self.pages[index - 1] = self.currentlySelected
        self.hylight(self.currentlySelected)

    def right(self):
        # Called when the right key is pressed, moves the selected icon to the right
        index = self.pages.index(self.currentlySelected)
        if index == len(self.pages) - 1:
            return
        self.pages[index] = self.pages[index + 1]
        self.pages[index + 1] = self.currentlySelected
        self.hylight(self.currentlySelected)

    def delete(self):
        if self.currentlySelected.path:
            self.pages.remove(self.currentlySelected)
        self.currentlySelected = Page()

    def import_file(self, path: str):
        # Called after the user selects desired pdf file.
        # Takes in a pdf file from inputPath


        if not path.endswith('.pdf'):
            raise InvalidFileException("Invlaid File")
        pdf_file_location = realpath(path)

        # name of the pdf file without path or exertion.
        file_name = splitext(basename(path))[0]

        # Names the new file with -0, -1, -2...ect depending on the number of duplicates.
        go = True
        i = 0
        while go:
            if not file_name + '-%s' % i in self.files.keys():
                file_name = file_name + '-%s' % i
                go = False
            i += 1
        image_location = join(ICON_DIR, file_name)

        print('saving file to ' + image_location)
        try:
            os.mkdir(image_location)
        except FileExistsError:
            pass

        convert_from_path(
            pdf_path=pdf_file_location,
            dpi=50,
            output_folder=image_location,
            output_file="page",
            fmt="png"
        )

        self.files[file_name] = PdfFile(pdf_file_location, file_name)
        logging.debug('importing %s' % path)
        for i, image in enumerate(self.files[file_name].get_images()):
            self.pages.append(
                Page(page_number=i,
                path=image,
                pdf_file=self.files[file_name],
                pdf_page=self.files[file_name].pdfObj.getPage(i))
            )


class Window(Frame):
    def __init__(self, main: Main, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.main = main

        self.master.title("Riffler")
        icon_dir = join(ROOT_DIR, "resources", "icon.gif")
        root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=icon_dir))

        # Creating the Frames that the icons go in and the scrollbar, the grid is in a frame, which is in a canvas.
        # This is the only way for it to work.
        self.canvas = Canvas(self.master)
        self.iconGrid = Frame(self.canvas)
        self.scrollbar = Scrollbar(
            self.master, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.canvas.create_window(
            (0, 0), window=self.iconGrid, anchor="nw", tags="self.iconGrid")

        self.master.bind("<Left>", self.left)
        self.master.bind("<Right>", self.right)
        self.master.bind("<Delete>", self.delete)
        self.iconGrid.bind("<Configure>", self.on_frame_config)

        # Creating The Menus
        menubar = Menu(self.master)
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.file_ask)
        file_menu.add_command(label="Save as...", command=self.main.export)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit")
        edit_menu.add_command(label="Delete")

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help Index")
        help_menu.add_command(label="About...") 

        self.master.config(menu=menubar)

    def on_frame_config(self, event):
        # This executes when the frame is updated, so the scrolling can work
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def file_ask(self):
        # Called when open menu item is selected, allows user to select desired pdf
        file = askopenfilename()  # show "Open" dialog box and return the path to selected file
        if file:
            try:
                self.main.import_file(file)
                self.render_pages()
            except InvalidFileException as err:
                messagebox.showwarning("Warning", err)


    def render_pages(self):
        self.main.delete_all_pages()
        var = None
        for i, _page in enumerate(self.main.pages):
            page = _page.path
            width = 150
            height = int(width * math.sqrt(2))
            self.main.icons[page] = Radiobutton(
                self.iconGrid,
                command=lambda _page=_page: self.main.hylight(
                    _page),
                image=_page.render,
                text="test",
                height=height + 50,
                width=width + 50, 
                bd=0, 
                variable=var,
                value=_page.path,
                indicatoron=0,
                selectcolor="blue",
                fg="black"             
            )

            self.main.icons[page].grid(row=i//4, column=i % 4, sticky='')

    def left(self, event):
        self.main.left()
        self.render_pages()

    def right(self, event):
        self.main.right()
        self.render_pages()

    def delete(self, event):
        self.main.delete()
        self.render_pages()  

        

def create_pdf(pages):
    output = PyPDF2.PdfFileMerger()
    for page in pages:
        logging.debug(str(type(page.pdfFile.path)) + page.pdfFile.path)
        output.append(page.pdfFile.path, pages=(
            page.pageNumber - 1, page.pageNumber))

    try:
        file = asksaveasfilename(
            defaultextension='pdf',
            filetypes=[('PDF File', '.pdf')]
        )
        if file:
            output.write(file)
    except FileNotFoundError:
        pass
    output.close()


def clean():
    for root_dir, dirs, files in os.walk(ICON_DIR):
        for d in dirs:
            shutil.rmtree(join(root_dir, d))


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    root = Tk()
    root.geometry("800x500")
    main = Main()
    app = Window(main, root)
    mainloop()
    clean()
