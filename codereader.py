#
import tkinter as tk
from tkinter import *
from tkinter.ttk import Entry, Label, Treeview, Scrollbar
from tkinter import messagebox as mbox
from tkinter import BooleanVar,IntVar
from tkinter import Toplevel
import sqlite3
import os, os.path
import re


def controlCod(s=''):                       # Функция проверки контрольного разряда
    arr=[]
    for sim in s:
        arr.append(int(sim))

    if len(s) == 13:
        a = arr[11] + arr[9] + arr[7] + arr[5] + arr[3] + arr[1]
        b = arr[10] + arr[8] + arr[6] + arr[4] + arr[2] + arr[0]
        v = 12
    elif len(s) == 14:
        a = arr[12] + arr[10] + arr[8] + arr[6] + arr[4] + arr[2] + arr[0]
        b = arr[11] + arr[9] + arr[7] + arr[5] + arr[3] + arr[1]
        v=13
    else:
        return False

    c = 3*a + b
    d = 10 - int(str(c)[-1])
    if int(str(d)[-1]) == arr[v]:
        return True
    else:
        return False

def create_db():                            #Создание базы 
    global DB
    if not os.path.exists('DB'):
        os.mkdir('DB')
    DB=sqlite3.connect('DB/spr.db3')
    cur=DB.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS "codedict"
    ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "codes" varchar(14) NOT NULL,
    "title_1" varchar(255) NOT NULL,
    "title_2" varchar(255));
    """)
    DB.commit()
    cur.close()
    DB.close()

def first_start():                          # Первый старт: создание БД
    if not os.path.exists("DB"):
        os.mkdir("DB")
    create_db()

def ins_lines(DDD):                         # Вставка строки 
    DB=sqlite3.connect('DB/spr.db3')
    DB.executemany('INSERT INTO codedict(codes,title_1,title_2) SELECT ?,?,?;', (DDD))
    DB.commit()
    DB.close()


def load_file(fl):                          # Проверка и загрузка в базу CSV файла
    D=[]
    with open(fl,encoding='866') as fn:
        while True:
            line= fn.readline().rstrip('\n')
            if not line:
                break
            if line[0][0].isnumeric():
                aa=line.split(sep=';')
                D.append((aa[0],aa[1],aa[2]))
    fn.close()
    ins_lines(D)
    mbox.showinfo("Загрузка","Готово!")

def exit_(event):                           # Выход по Escape
    if event.keycode==27:
        w_root.destroy()

def update_tree():                          # Функция обновления treview
    tree.delete(*tree.get_children())
    DB=sqlite3.connect('DB/spr.db3')
    c=DB.cursor()
    sfq='select * from codedict order by codes'
    c.execute(sfq)   

    for idx,row in enumerate(c.fetchall()):
        if idx%2==0:
            tree.insert('','end',iid=row[0], text=str(idx+1), values=(row[1],row[2]), tags = ('odd',))
        else:
            tree.insert('','end',iid=row[0], text=str(idx+1), values=(row[1],row[2]), tags = ('even',))
    c.close()
    DB.close() 
    


def show_w_spr():                                   # Окно справочника
    global w_spr,tree,btn_del, btn_edit, btn_new, btn_esc
    global lbl_count0, lbl_count1, lbl_count2
    global boxcode, box_name1, box_name2
    global tree
    w_spr = Toplevel(w_root)
    
    w_spr.title("Справочник кодов")
    x = (w_spr.winfo_screenwidth() - 850)/2
    y = (w_spr.winfo_screenheight() - 500)/2
    w_spr.geometry('850x500+%d+%d' % (x,y))
    
    w_spr.resizable(0,0)
    w_spr.configure(padx=10,pady=10)
    pic = tk.PhotoImage(file='barcode-product.png')
    w_spr.iconphoto(False,pic)
    w_spr.columnconfigure(0,minsize=15,weight=1)

    style = tk.ttk.Style()

    style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 12)) # Modify the font of the body
    style.configure("mystyle.Treeview.Heading", font=('Calibri', 12,'bold'), background="grey", foreground="green", relief="flat") # Modify the font of the headings
    style.configure("mystyle.Treeview", relief="groove")
    style.map("mystyle.Treeview.Heading", relief=[('active','groove'),('pressed','sunken')])
    
    ### 
    tree = Treeview(w_spr, columns=("codes", "title_1", "title_2"), style="mystyle.Treeview", height=8,selectmode="browse", show="tree headings")
    tree.grid(column=0, row=1, sticky='nsew', columnspan=4,rowspan=8)
    
    tree.column("#0", width=50, minwidth=45, stretch=False)
    tree.column("codes", width=125, minwidth=120, stretch=False)
    tree.column("#2", width=1500, minwidth=400, stretch=True)

    tree.heading("#0", text="#")
    tree.heading("codes", text="Код", anchor="w")
    tree.heading("title_1", text="Наименование продукции", anchor="w")

    # attach a Horizontal (x) scrollbar to the frame
    treeXScroll = Scrollbar(w_spr, orient=tk.HORIZONTAL)
    treeXScroll.configure(command=tree.xview)
    tree.configure(xscrollcommand=treeXScroll.set)
    treeXScroll.grid(column=0, row=9, columnspan=4, sticky='we')
    # attach a Vertical (y) scrollbar to the frame
    treeYScroll = Scrollbar(w_spr, orient=tk.VERTICAL)
    treeYScroll.configure(command=tree.yview)
    tree.configure(yscrollcommand=treeYScroll.set)
    treeYScroll.grid(column=5, row=1, rowspan=8, sticky='ns')

    update_tree()

    tree.tag_configure("even", background='#FFFFFF')
    tree.tag_configure("odd", background='#F4F4F4')

    tree.bind('<Button-3>',b3)
    tree.bind('<Button-1>',b1)

    ###
    frm = tk.Frame(w_spr,relief='raised',border=2)
    frm.grid(row=11,column=0,columnspan=6,sticky='we',pady=5)
    #frm.columnconfigure(0,minsize=25,weight=1)
    frm.columnconfigure(1,minsize=15,weight=1)
    frm.columnconfigure(2,minsize=15,weight=1)
    frm.columnconfigure(3,minsize=15,weight=1)
    frm.columnconfigure(4,minsize=15,weight=1)
    frm.columnconfigure(5,minsize=15,weight=1)
    frm.columnconfigure(6,minsize=15,weight=1)
    frm.columnconfigure(7,minsize=5,weight=1)


    lbl_prod = Label(frm, text="Код:", font=('Calibri 11'))  
    lbl_prod.grid(column=0, row=1,padx=10, pady=5, sticky="w")

    boxcode = Entry(frm,width=15, font=('Calibri 12 bold'))                 # CODE
    boxcode.grid(column=1, row=1, padx=5,sticky='we')
    boxcode['state']='disabled'
    boxcode.bind('<KeyRelease>',code_check)

    lbl_count0 = Label(frm, text="0", font=('Calibri 10 bold'))              # simbolcount
    lbl_count0.grid(column=2, row=1,padx=2, pady=5, sticky="nw")

    lbl_title1 = Label(frm, text="Название 1:", font=('Calibri 11'))  
    lbl_title1.grid(column=0, row=2,padx=10, pady=5, sticky="nw")

    box_name1 = Text(frm,width=75,height=5, wrap=WORD)                  # NAME_1
    box_name1.grid(column=1, row=2, padx=5, pady=5, sticky='we', columnspan=6,rowspan=3)
    box_name1['state']='disabled'
    box_name1.bind('<KeyRelease>',update_1)

    lbl_count1 = Label(frm, text="0", font=('Calibri 10 bold'))              # simbolcount
    lbl_count1.grid(column=7, row=2,padx=2, pady=5, sticky="nw")

    lbl_title2 = Label(frm, text="Название 2:", font=('Calibri 11'))  
    lbl_title2.grid(column=0, row=5,padx=10, pady=5, sticky="nw")

    box_name2 = Text(frm,width=75,height=5, wrap=WORD)                  # NAME_2
    box_name2.grid(column=1, row=5, padx=5, pady=5, sticky='we', columnspan=6,rowspan=3)
    box_name2['state']='disabled'
    box_name2.bind('<KeyRelease>',update_2)

    lbl_count2 = Label(frm, text="0", font=('Calibri 10 bold'))              # simbolcount
    lbl_count2.grid(column=7, row=5,padx=2, pady=5, sticky="nw")

    btn_new = tk.Button(frm, text="Новый", width=15,font=('Calibri 11 bold'), foreground="blue")               # btn_new
    btn_new.grid(column=3, row=8, padx=5, pady=8, sticky="we")
    btn_new.bind('<ButtonRelease-1>', new_code)

    btn_edit = tk.Button(frm, text="Редактировать", width=15,font=('Calibri 11 bold'))      # btn_edit
    btn_edit.grid(column=4, row=8, padx=5, pady=8, sticky="we")
    btn_edit.bind('<ButtonRelease-1>', edit_code)
    btn_edit['state']='disabled'
    
    btn_del = tk.Button(frm, text="Удалить", command=lambda:del_code('<ButtonRelease-1>'), width=15,font=('Calibri 11 bold'))             #btn_del
    btn_del.grid(column=5, row=8, padx=5, pady=8, sticky="we")
    btn_del['state']='disabled'

    btn_esc = tk.Button(frm, text="Выход",  width=10,font=('Calibri 11 bold'))    #btn_close
    btn_esc.grid(column=6, row=8, padx=5, pady=8, sticky="we")
    btn_esc.bind('<ButtonRelease-1>',esc_spr)
    ###
    w_spr.transient(w_root)
    w_spr.grab_set()
    w_spr.focus_set()
    w_spr.wait_window()


def esc_spr(event):                         # Закрытие окна справочника
    w_spr.destroy()

def cancel(event):                          # Отмена создания/редактирования
    rez(event)

def update_1(event):                        # Счетчик длины поля 1
    txt1 = box_name1.get("1.0",tk.END).rstrip('\n')
    dl = len(txt1)
    
    if 240 < dl < 253:
        lbl_count1.config(foreground="darkorange")
    elif 252 < dl < 255:
        lbl_count1.config(foreground="red")
    else:
        lbl_count1.config(foreground="black")

    if dl >= 255:
        box_name1.delete("1.254",tk.END)
    lbl_count1.config(text=str(dl))

def update_2(event):                        # Счетчик длины поля 2
    txt1 = box_name2.get("1.0",tk.END).rstrip('\n')
    dl = len(txt1)
    
    if 240 < dl < 253:
        lbl_count2.config(foreground="darkorange")
    elif 252 < dl < 255:
        lbl_count2.config(foreground="red")
    else:
        lbl_count2.config(foreground="black")

    if dl >= 255:
        box_name2.delete("1.254",tk.END)
    lbl_count2.config(text=str(dl))

def code_check(event):                  # Проверка длины и контрольной суммы цифрового ввода
    txt = boxcode.get()
    txt = re.sub(r'\D','',txt)
    boxcode.delete(0,tk.END)
    boxcode.insert(0,txt)
    dl = len(txt)
    lbl_count0.config(text=str(dl))
    if dl > 14:
        boxcode.delete(14,tk.END)
    if dl == 13 or dl == 14:
        if controlCod(txt) == True:
            boxcode.config(foreground = "green")
        else:
            boxcode.config(foreground = "red")
    else:
        boxcode.config(foreground = "black")

def b1(event):                          # реакция на левую кнопку мыши на списке
    btn_edit['state']='normal'
    btn_del['state']='normal'
    btn_new['state']='disabled'
    btn_edit.config(foreground='green')
    btn_del.config(foreground='red')

def new_code(event):                        # Создание новой записи
    btn_new.config(text='Сохранить')
    btn_new.unbind('<ButtonRelease-1>')
    rez2('<KeyPress>')
    btn_new.bind('<ButtonRelease-1>',save_new)
    btn_del['state']='disabled'
    btn_edit['state']='disabled'
    
def save_new(event):                        # Проверка и сохранение новой записи 
    data2 = ''
    data3 = ''
    data1 = boxcode.get()
    data2 = box_name1.get("1.0",tk.END).rstrip()
    data2= data2.replace('"', chr(34))
    data2= data2.replace("'", chr(34))
    data3 = box_name2.get("1.0",tk.END).rstrip()
    if controlCod(data1)==True:
        # проверка кода на наличие
        DB=sqlite3.connect('DB/spr.db3')
        c=DB.cursor()
        c.execute('select count(*) from codedict where codes=?',(data1,))  # 
        row = tuple(c.fetchone())
        c.close()
        if row[0] != 0:
            mbox.showwarning('Ошибка записи!',' В справочнике уже присутствует такой код!')
        else:
            if data2!='':
                DB=sqlite3.connect('DB/spr.db3')
                DB.execute("insert into codedict(codes,title_1,title_2) select {0},'{1}','{2}'".format(data1,data2,data3))
                DB.commit()
                DB.close()
                btn_new.config(text='Новый')
                btn_new.unbind('<ButtonRelease-1>')
                btn_new.bind('<ButtonRelease-1>', new_code)
                rez('<KeyPress>')
                update_tree()
                mbox.showinfo('Добавление новой записи в справочник кодов','Запись добавлена!') 
            else:
                mbox.showwarning('Ошибка!','Название не должно быть пустым!')
                box_name1.focus()
    else:
        mbox.showwarning('Ошибка!', 'Проверьте вводимый код.\nОн должен быть длинной 13 или 14 цифр.\nПоследняя цифра должна быть равна контрольной сумме.')
        boxcode.focus()

def edit_code(event):                        # Редактирование
    global row_id
    btn_edit.config(text='Сохранить')
    btn_edit.unbind('<ButtonRelease-1>')
    btn_edit.bind('<ButtonRelease-1>',save_edit)
    btn_esc.bind('<ButtonRelease-1>', rez)
    rez2('<ButtonRelease-1>')
    try:
        row_id = int(tree.focus())
    except:
        return
    DB=sqlite3.connect('DB/spr.db3')
    c=DB.cursor()
    c.execute('select * from codedict where id=?',(row_id,))
    rows = c.fetchone()
    c.close() 
        
    boxcode.insert(0,rows[1])
    box_name1.insert('1.0',rows[2].rstrip())
    box_name2.insert('1.0',rows[3].rstrip())
    update_1('<KeyPress>')
    update_2('<KeyPress>')
    code_check('<KeyPress>')
    tree.state(("disabled",))
    btn_del['state']='disabled'
    btn_new['state']='disabled'
    


def del_code(event):                        # Удаление кода
    global row_id
    ask = mbox.askokcancel('Удаление записи в справочнике кодов','Вы уверены, что хотите удалить выбранный код?')
    if ask == True:
        try:
            row_id = int(tree.focus())
            txt_= tree.item(tree.selection()[0], option="values")[0]
        except:
            return
        DB=sqlite3.connect('DB/spr.db3')
        DB.execute('delete from codedict where id=?',(row_id,))
        DB.commit()
        DB.close()
        rez('<ButtonRelease-1>')
        update_tree()
        mbox.showinfo('Удаление записи в справочнике кодов','Запись с кодом "{0}" удалена'.format(txt_,))


def save_edit(event):                   # Сохранение редактированного
    
    data2 = ''
    data3 = ''
    data1 = boxcode.get()
    data2 = box_name1.get("1.0",tk.END).rstrip()
    data2= data2.replace('"', chr(34))
    data2= data2.replace("'", chr(34))
    data3 = box_name2.get("1.0",tk.END).rstrip()
    if controlCod(data1)==True:
        if data2!='':
            DB=sqlite3.connect('DB/spr.db3')
            sfq = '''update codedict set codes=\'{0}\', title_1=\'{1}\', title_2=\'{2}\' where id={3}'''.format(data1,data2,data3,row_id)
            sfq=sfq.replace("\n","")
            DB.execute(sfq)
            DB.commit()
            DB.close()
            btn_edit.config(text='Редактировать')
            btn_edit.unbind('<ButtonRelease-1>')
            btn_edit.bind('<ButtonRelease-1>',edit_code)
            rez(event)
            update_tree()
        else:
            mbox.showwarning('Ошибка!','Название не должно быть пустым!')
            box_name1.focus()
    else:
        mbox.showwarning('Ошибка!', 'Проверьте вводимый код.\nОн должен быть длинной 13 или 14 цифр.\nПоследняя цифра должна быть равна контрольной сумме.')
        boxcode.focus()


def b3(event):                          # реакция на правую кнопку мыши на списке
    try:
        row_id = int(tree.focus())
    except:
        return
    tree.selection_toggle(row_id)
    rez(event)

def rez(event):                             # сброс
    btn_edit['state']='disabled'
    btn_edit.config(text='Редактировать')
    btn_edit.unbind('<ButtonRelease-1>')
    btn_edit.bind('<ButtonRelease-1>', edit_code)
    btn_edit['state']='disabled'
    btn_new['state']='normal'
    btn_new.config(text='Новый')
    btn_new.unbind('<ButtonRelease-1>')
    btn_new.bind('<ButtonRelease-1>', new_code)
    btn_del['state']='disabled'
    boxcode['state']='normal'
    box_name1['state']='normal'
    box_name2['state']='normal'
    tree.state(("!disabled",))
    boxcode.delete(0,tk.END)
    box_name1.delete("1.0",tk.END)
    box_name2.delete("1.0",tk.END)
    lbl_count0['text']='0'
    lbl_count1['text']='0'
    lbl_count2['text']='0'
    boxcode['state']='disabled'
    box_name1['state']='disabled'
    box_name2['state']='disabled'
    btn_esc.config(text='Выход')
    btn_esc.unbind('<ButtonRelease-1>')
    btn_esc.bind('<ButtonRelease-1>', esc_spr)
    try:
        row_id = int(tree.focus())
    except:
        return
    tree.selection_set(row_id)
    tree.selection_toggle(row_id)

def rez2(event):                    # подготовка полей ввода в справочнике
    boxcode['state']='normal'
    box_name1['state']='normal'
    box_name2['state']='normal'
    boxcode.delete(0,tk.END)
    box_name1.delete("1.0",tk.END)
    box_name2.delete("1.0",tk.END)
    lbl_count0['text']='0'
    lbl_count1['text']='0'
    lbl_count2['text']='0'
    btn_esc.config(text='Отмена')
    btn_esc.unbind('<ButtonRelease-1>')
    btn_esc.bind('<ButtonRelease-1>', cancel)


def vvod(event):                            # Проверка вводимого кода со справочником
    s=incode.get()
    res=controlCod(s)
    row=[]
    if res==True:
        DB=sqlite3.connect('DB/spr.db3')
        c=DB.cursor()
        c.execute('select title_1,title_2 from codedict where codes=?',(s,))   
        row = c.fetchone()
        c.close()
        if row!=0 and row is not None:
            txt_title1.config(text=row[0], foreground="blue", font=('Calibri 14 normal'))
            txt_title2.config(text=row[1], foreground="blue", font=('Calibri 14 normal'))
        else:
            txt_title1.config(text='Код отсутствует в справочнике', foreground="red",font=('Calibri 14 bold'))
            txt_title2.config(text='Если код правильный, добавьте его в справочник', foreground="red",font=('Calibri 14 bold'))
            #incode.delete(0,tk.END)    
    else:
        txt_title1.config(text='Не совпадает контрольная сумма кода', foreground="red",font=('Calibri 14 bold'))
        txt_title2.config(text='---', foreground="red",font=('Calibri', 14, "bold"))
    incode.delete(0,tk.END)

def show_w_root():  #Главное окно
    global w_root,txt_title1,txt_title2,incode
    w_root = tk.Tk()
    w_root.title("Проверка штрихкодов")
    x = w_root.winfo_screenwidth() 
    y = w_root.winfo_screenheight()
    x1 = (x - 850)/2
    y1 = (y - 350)/2 - 50
    w_root.geometry('850x350+%d+%d' % (x1,y1))
    w_root.resizable(0,0)
    pic = tk.PhotoImage(file='barcode-product.png')
    w_root.iconphoto(False,pic)
    #w_root.configure(pady=1)
    w_root.bind('<Key>',exit_)
    
    menu = tk.Menu(w_root)
    gen_menu = tk.Menu(menu, tearoff=0)
    w_root.config(menu=gen_menu)
    gen_menu.add_command(label="Справочник", command=show_w_spr)
    gen_menu.add_command(label="Выйти", command=w_root.destroy)

    w_root.columnconfigure(0, minsize=15, weight=1)
    w_root.columnconfigure(1, minsize=700, weight=2)

    lbl_1 = Label(w_root, text="Штрихкод:",font=('Calibri 14 bold'))  
    lbl_1.grid(column=0, row=0,padx=5,pady=10,sticky="w")

    incode = Entry(w_root,width=15,font=('Calibri 16 normal'))
    incode.focus()
    incode.grid(column=1, row=0,padx=5,pady=10,sticky="w")
    w_root.bind('<Return>',vvod)
    
    lbl_title1 = Label(w_root, text="Название ЛС:", font=('Calibri 14'))  
    lbl_title1.grid(column=0, row=1,padx=5, pady=10, sticky="nw")

    txt_title1 = Label(w_root, text="", font=('Calibri 14 normal'), wraplength=700, foreground="blue") #, background="#fffffd", borderwidth=1, relief="solid")  
    txt_title1.grid(column=1, row=1,padx=5, pady=10, sticky="nw") #, ipady=10, ipadx=5)

    lbl_title2 = Label(w_root, text="Название 2:", font=('Calibri 14'))  
    lbl_title2.grid(column=0, row=2,padx=5, pady=10, sticky="nw")

    txt_title2 = Label(w_root, text="", font=('Calibri 14 normal'), wraplength=700, foreground="blue") #, background="#fffffd", borderwidth=1, relief="solid")  
    txt_title2.grid(column=1, row=2,padx=5, pady=10, sticky="nw") #, ipady=10, ipadx=5)
    w_root.mainloop()


##################################################################

# START PROG ->
if __name__ == '__main__':
    create_db()
    #load_file('EAN-13.csv')
    #load_file('ITF-14.csv')
    show_w_root()
