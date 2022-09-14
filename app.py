from flask import Flask, flash
from flask import render_template, request, redirect, url_for
import mariadb
app = Flask(__name__)
app.config['SECRET_KEY'] = "my super"

## mariadb configs
DB_HOST="'127.0.0.1'"
DB_PORT=3306
DB_USER="'root'"
DB_DATABASE="'tese1'"
DB_PASSWORD="''"
DB_CONNECTION_STRING = "\n host=%s,\n port=%s,\n user=%s,\n password=%s,\n database=%s" % (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE)

#conn = mariadb.connect(DB_CONNECTION_STRING)
#cur = conn.cursor()

########################################################
#
# Name: home
#
# Objective: View the login page
#
# Input Parameters:
#   nil
#
# Return value and output parameters:
#   name - name of the user
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        user = request.form['nm']                #user - login user
        chave = request.form['pass']             #chave - login pass
        cur.execute("SELECT name FROM user WHERE name = ?",(user,))
        db_name = cur.fetchone()                 #db_name - database name
        cur.execute("SELECT pass FROM user WHERE pass = ? AND name = ?",(chave,user,))
        db_chave = cur.fetchone()                #db_chave - database pass
        cur.execute("SELECT admin FROM user WHERE pass = ? AND name = ?",(chave,user,))
        db_admin = cur.fetchone()
        if not(db_name):
            flash('Nome inválido')
            return redirect(url_for('home'))        
        elif not(db_chave):
            flash('Chave inválida')
            return redirect(url_for('home'))
        elif db_admin[0] != 1: 
            return redirect(url_for('menu',name = user))
        else:
            return redirect(url_for('adminmenu'))


    elif request.method == 'GET':
        return render_template('index.html')
    
########################################################
#
# Name: menu
#
# Objective: View the processes of the employee
#
# Input Parameters:
#   name - name of the employee
#
# Return value and output parameters:
#   nProcess - Number of the process
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/menu/<name>', methods=['GET', 'POST'])
def menu(name):
    if request.method == 'POST':
        if request.form["x"] == "Log Out":
            return redirect(url_for('home'))     #return to previous page
        if request.form["x"] == "Definições":
            return redirect(url_for('defi',name=name))
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',                           
         database='tese1')
        cur = conn.cursor()
        x = request.form["x"]                    #label of the button
        x = x[8:]
        cur.execute("SELECT nUser FROM user WHERE name = ?",(name,))
        db_id = cur.fetchone()
        if request.form["x"] == "Adicionar novo processo":
            return redirect(url_for('insertprocess',nUser=db_id[0]))
        cur.execute("SELECT nProcess FROM process WHERE nUser = %s ORDER BY startDate DESC",(db_id[0],))
        db_process = cur.fetchall()
        nProcess = db_process[int(x)]           #unique id of the process selected 
        if request.form["x"][1] == "l":         # "l" = erase
            cur.execute("SELECT * FROM recit WHERE nProcess = %s",(nProcess[0],))
            dados = cur.fetchall()
            if dados:                           #if the process has data dont erase
                return redirect(url_for('menu',name=name))
            cur.execute("DELETE FROM process WHERE nProcess = %s",(nProcess[0],))
            conn.commit()
            return redirect(url_for('menu',name=name))
        return redirect(url_for('process',nProcess=nProcess[0]))
    elif request.method == 'GET':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT nUser FROM user WHERE name = ?",(name,))
        db_id = cur.fetchone()                  #id in the database of the user
        #cur.execute("SELECT SUM(price) FROM recit WHERE ;")
        cur.execute("SELECT project,startDate,endDate,description,status,priceTotal FROM process WHERE nUser = %s ORDER BY startDate DESC",(db_id[0],))
        db_process = cur.fetchall()
        project=[]
        date1=[]
        date2=[]
        descricao=[]
        status=[]
        priceTotal=[]
        n=len(db_process)
        for x in range(len(db_process)):         #cycle trough every process
            project.append(db_process[x][0])     #save every data in its palce
            cur.execute("SELECT project FROM project WHERE idProject = %s",(project[x],))
            project[x] = cur.fetchone()
            date1.append(db_process[x][1])
            date2.append(db_process[x][2])
            descricao.append(db_process[x][3])
            status.append(db_process[x][4])
            cur.execute("SELECT status FROM status WHERE idStatus = %s",(status[x],))
            status[x] = cur.fetchone()
            priceTotal.append(db_process[x][5])

        return render_template('menu.html', project=project, date1=date1, date2=date2, descricao=descricao, status=status, priceTotal=priceTotal, n=n, name=name)

########################################################
#
# Name: process
#
# Objective: View the receipts of the employee
#
# Input Parameters:
#   nProcess - Number of the process
#
# Return value and output parameters:
#   nProcess - Number of the process
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/process/<nProcess>', methods=['GET', 'POST'])
def process(nProcess):
    if request.method == 'POST':
        conn = mariadb.connect(
            host='127.0.0.1',
            port= 3306,
            user='root',
            password='',
            database='tese1')
        cur = conn.cursor()
        if request.form["botao"] == "Adicionar nova despesa":
            return redirect(url_for('insertrecit',nProcess=nProcess))
        elif request.form["botao"] == "Voltar":
            cur.execute("SELECT nUser FROM process WHERE nProcess = ?",(nProcess,))
            db_n = cur.fetchone()               #id of user
            cur.execute("SELECT name FROM user WHERE nUser = ?",(db_n[0],))
            db_m = cur.fetchone()               #name of user
            return redirect(url_for('menu',name=db_m[0]))
        editar = request.form["botao"]          #label of the button
        editar = editar[8:]
        cur.execute("SELECT nRecit FROM Recit WHERE nProcess = %s ORDER BY day DESC",(nProcess,))
        db_recit2 = cur.fetchall()
        recit = db_recit2[int(editar)]         #recit=id of recit to edit/erase
        if request.form["botao"][1] == "l":     #l = erase
            cur.execute("SELECT price FROM Recit WHERE nRecit = %s",(recit[0],))
            valorNeg = cur.fetchone()
            cur.execute("DELETE FROM recit WHERE nRecit = %s",(recit[0],))
            conn.commit()
            cur.execute("UPDATE process SET priceTotal = priceTotal-%s WHERE nProcess = %s", (valorNeg[0],nProcess))
            conn.commit()
            return redirect(url_for('process',nProcess=nProcess))
        return redirect(url_for('editrecit',recit=recit[0]))
    elif request.method == 'GET':
        
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT day,type,price,merchant,paymentMethod,description,photo,approved FROM Recit WHERE nProcess = %s ORDER BY day DESC",(nProcess,))
        db_recit = cur.fetchall()
        day=[]
        type1=[]
        price=[]
        merchant=[]
        paymentMethod=[]
        description=[]
        photo=[]
        approved=[]
        disabled=[]
        n=len(db_recit)
        for x in range(len(db_recit)):          #cycle trough every data from receipt
            day.append(db_recit[x][0])          #save every data in its palce
            type1.append(db_recit[x][1])
            cur.execute("SELECT type FROM type WHERE idType = %s",(type1[x],))
            type1[x] = cur.fetchone()
            price.append(round(db_recit[x][2],2))
            merchant.append(db_recit[x][3])
            paymentMethod.append(db_recit[x][4])
            cur.execute("SELECT payMethod FROM paymentMethod WHERE idPay = %s",(paymentMethod[x],))
            paymentMethod[x] = cur.fetchone()
            description.append(db_recit[x][5])
            photo.append(db_recit[x][6])
            approved.append(db_recit[x][7])
            if approved[x] != 0:                #if the recit is approved
                approved[x] = "Aceite"          #disble its action
                disabled.append("disabled")
            else: 
                approved[x] = "Pendente"
                disabled.append("")
        cur.execute("SELECT project,startDate,endDate,description,status,priceTotal FROM process WHERE nProcess = %s",(nProcess,))
        db_process = cur.fetchone()
        return render_template('list_recit.html', db_process=db_process,day=day,type1=type1,price=price,merchant=merchant,paymentMethod=paymentMethod,description=description,photo=photo,approved=approved,n=n,nProcess=nProcess,disabled=disabled)
        
########################################################
#
# Name: insertrecit
#
# Objective: Insert a new receipt
#
# Input Parameters:
#   nProcess - Number of the process
#
# Return value and output parameters:
#   nProcess - Number of the process
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/insertrecit/<nProcess>', methods=['GET', 'POST'])
def insertrecit(nProcess):
    if request.method == 'POST':
        if request.form["botao"] == "Voltar":
            return redirect(url_for('process',nProcess=nProcess))
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()                 
        tipo = request.form["tipo"]             #extract the data of the recit    
        valor = request.form["valor"]
        date = request.form["date"]
        descricao = request.form["descricao"]
        merchant = request.form["empresa"]
        paymentMethod = request.form["pay"]
        photo = "www.photo.com"
        approved = 0
        if not(tipo) or not(valor) or not(date) or not(descricao) or not(merchant) or not(paymentMethod):
            print ("empty")
            flash('Dados Incompletos')
            return redirect(url_for('insertrecit',nProcess=nProcess))
        cur.execute("INSERT INTO recit(nProcess,day,type,price,merchant,paymentMethod,description,photo,approved) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (nProcess,date,tipo,valor,merchant,paymentMethod,descricao,photo,approved))
        conn.commit()
        cur.execute("UPDATE process SET priceTotal = priceTotal+%s WHERE nProcess = %s", (valor,nProcess))
        conn.commit()
        return redirect(url_for('process',nProcess=nProcess))

    elif request.method == 'GET':
        return render_template('insert_recit.html',nProcess=nProcess)

########################################################
#
# Name: editrecit
#
# Objective: Edit the receipt chosen
#
# Input Parameters:
#   recit - Receipt of the employee to be edited
#
# Return value and output parameters:
#   nProcess - Number of the process
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/editrecit/<recit>', methods=['GET', 'POST'])
def editrecit(recit):
    if request.method == 'POST':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        tipo = request.form["tipo"]
        valor = request.form["valor"]
        date = request.form["date"]
        empresa = request.form["empresa"]
        payM = request.form["pay"]
        descricao = request.form["descricao"]
        cur.execute("SELECT price FROM Recit WHERE nRecit = %s",(recit,))
        valorNeg = cur.fetchone()              #Value to subtract to pricetotal
        cur.execute("SELECT nProcess FROM Recit WHERE nRecit = %s",(recit,))
        nProcess = cur.fetchone()
        if not(tipo) or not(valor) or not(date) or not(descricao) or not(empresa) or not(payM):
            print ("empty")
            flash('Dados Incompletos')
            return redirect(url_for('editrecit',recit=recit))
        cur.execute("UPDATE recit SET nProcess = %s, day = %s, type = %s, price = %s, merchant = %s, paymentMethod = %s, description = %s WHERE nRecit = %s", (nProcess[0],date,tipo,valor,empresa,payM,descricao,recit))
        conn.commit()
        cur.execute("UPDATE process SET priceTotal = priceTotal-%s+%s WHERE nProcess = %s", (valorNeg[0],valor,nProcess[0]))
        conn.commit()

        return redirect(url_for('process',nProcess=nProcess[0]))
    elif request.method == 'GET':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT day,type,price,merchant,paymentMethod,description,photo FROM Recit WHERE nRecit = %s",(recit,))
        db_recit3 = cur.fetchone()
        tipo1 = None 
        tipo2 = None 
        tipo3 = None 
        tipo4 = None 
        if db_recit3[1] == 1:           #type of recit
            tipo1 = "checked"
        if db_recit3[1] == 2:
            tipo2 = "checked"
        if db_recit3[1] == 3:
            tipo3 = "checked"
        if db_recit3[1] == 4:
            tipo4 = "checked"
        m1 = None                           
        m2 = None 
        m3 = None 
        m4 = None 
        if db_recit3[4] == 1:           #payMethod of recit
            m1 = "checked"
        if db_recit3[4] == 2:
            m2 = "checked"
        if db_recit3[4] == 3:
            m3 = "checked"
        if db_recit3[4] == 4:
            m4 = "checked"
        return render_template('edit_recit.html', day=db_recit3[0],tipo4=tipo4,tipo3=tipo3,tipo2=tipo2,tipo1=tipo1,price=round(db_recit3[2],2),m1=m1,m2=m2,m3=m3,m4=m4,merchant=db_recit3[3],description=db_recit3[5],photo=db_recit3[6],recit=recit)

########################################################
#
# Name: insertprocess
#
# Objective: Insert a new process
#
# Input Parameters:
#   nUser - ID number of the employee
#
# Return value and output parameters:
#   name - Name of the employee
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/insertprocess/<nUser>', methods=['GET', 'POST'])
def insertprocess(nUser):
    if request.method == 'POST':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT name FROM user WHERE nUser = ?",(nUser,))
        db_name = cur.fetchone()
        if request.form["botao"] == "Voltar":
            return redirect(url_for('menu',name=db_name[0]))
        date1 = request.form["date1"]
        date2 = request.form["date2"]
        proj = request.form["projects"]
        desc = request.form["descricao"]
        stat = 1                                #State of process starts at one
        priceT = 0                              #price total starts at 0
        if not(date1) or not(date2) or not(proj) or not(desc):
            print ("empty")
            flash('Dados Incompletos')
            return redirect(url_for('insertprocess',nUser=nUser))
        cur.execute("INSERT INTO process(nUser,project,startDate,endDate,description,status,priceTotal) VALUES (%s,%s,%s,%s,%s,%s,%s)", (nUser,proj,date1,date2,desc,stat,priceT))
        conn.commit()
        return redirect(url_for('menu',name=db_name[0]))

    elif request.method == 'GET':                               
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT project FROM project ")        # get projects
        db_proj = cur.fetchall()
        n=len(db_proj)                                      
        return render_template('insert_process.html',nUser=nUser,db_proj=db_proj,n=n)

########################################################
#
# Name: AdminMenu
#
# Objective: View the employees and their info
#
# Input Parameters:
#   nil
#
# Return value and output parameters:
#   numb - ID number of the employee
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/adminmenu', methods=['GET', 'POST'])
def adminmenu():
    if request.method == 'POST':
        if request.form["botao"] == "Log Out":
            return redirect(url_for('home'))
        if request.form["botao"] == "Definições":
            return redirect(url_for('admindef'))
        botao = request.form["botao"]                   #botao - Label of the button 
        botao = botao[:-17]                             #Erase the last 17 letters
        numb = int(botao[0])
        return redirect(url_for('adminlist',numb=numb)) #Go to the list of procces from one user
    elif request.method == 'GET':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT name,mail,NIF,IBAN,morada,nUser FROM user WHERE admin = 0 ORDER BY nUser DESC")
        db_users = cur.fetchall()
        n = len(db_users)                       #number of users existing
        return render_template('admin_menu.html',db_users=db_users, n=n)

########################################################
#
# Name: AdminList
#
# Objective: View the receipts of a given employee
#
# Input Parameters:
#   NUMB - ID number of the employee
#
# Return value and output parameters:
#   nil
#
# Obs:
#   nil
#
# Version 1.0, 28/08/2022, by David Lobo
#########################################################
@app.route('/adminlist/<numb>', methods=['GET', 'POST'])
def adminlist(numb):
    if request.method == 'POST':
        if request.form["botao"] == "Voltar":
            return redirect(url_for('adminmenu'))
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        botao = request.form["botao"]
        if botao[0] == "D":                     # Option D=> Disapprove 
            botao = botao[10:]
            cur.execute("UPDATE recit SET approved = false WHERE nRecit = %s", (botao,))
            conn.commit()
        elif botao[0] == "A":                   # Option A=> Approve
            botao = botao[7:] 
            cur.execute("UPDATE recit SET approved = true WHERE nRecit = %s", (botao,))
            conn.commit()
        elif botao[0] == "S":                   # Option S=> Status of process
            botao = botao[8:] 
            status = request.form["status"]
            cur.execute("UPDATE process SET status = %s WHERE nProcess = %s", (status,botao,))
            conn.commit()
        return redirect(url_for('adminlist',numb=numb))
    elif request.method == 'GET':
        project = []
        status = []
        db_recit4 = []
        n2 = []
        preco = []
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT nUser FROM user WHERE admin = 0")
        db_users = cur.fetchall()               #all users none admin
        nUser = db_users[int(numb)]
        cur.execute("SELECT nProcess,project,startDate,endDate,description,status,priceTotal FROM process WHERE nUser = %s ORDER BY startDate DESC",(nUser[0],))
        db_process = cur.fetchall()
        n = len(db_process)                     #nº of users
        for i in range(n):
            cur.execute("SELECT project FROM project WHERE idProject = %s",(db_process[i][1],))
            project.append(cur.fetchone())
            cur.execute("SELECT status FROM status WHERE idStatus = %s",(db_process[i][5],))
            status.append(cur.fetchone())
            cur.execute("SELECT Recit.day,Type.type,Recit.price,Recit.merchant,PaymentMethod.payMethod,Recit.description,Recit.photo,Recit.approved,Recit.nRecit FROM Recit INNER JOIN Type ON Recit.type=Type.idType INNER JOIN PaymentMethod ON Recit.paymentMethod=PaymentMethod.idPay WHERE nProcess = %s ORDER BY day DESC",(db_process[i][0],))
            tuplerecit = cur.fetchall()
            db_recit4.append(tuplerecit)
            n2.append(len(db_recit4[i]))
        return render_template('admin_list.html', n=n, n2=n2, db_process=db_process,db_recit4=db_recit4,numb=numb,project=project,status=status)

########################################################
#
# Name: AdminDef
#
# Objective: Definitions of the Admin
#
# Input Parameters:
#   nil
#
# Return value and output parameters:
#   nil
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/admindef', methods=['GET', 'POST'])
def admindef():
    if request.method == 'POST':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        if request.form["botao"] == "Voltar":       #go back last page
            return redirect(url_for('adminmenu'))
        elif request.form["botao"] == "Criar":      #create a new project
            newproj = request.form["newproject"]
            cur.execute("INSERT INTO project(project) VALUES (%s)", (newproj,))
            conn.commit()
            return redirect(url_for('admindef'))
        elif request.form["botao"] == "Criar Utilizador":   #create new user
            name = request.form["name"]
            pass1 = request.form["pass"]
            email = request.form["email"]
            iban = request.form["iban"]
            nif = request.form["nif"]
            morada = request.form["morada"]
            admin = 0
            cur.execute("INSERT INTO user(name,pass,admin,mail,IBAN,NIF,morada) VALUES (%s,%s,%s,%s,%s,%s,%s)", (name,pass1,admin,email,iban,nif,morada))
            conn.commit()
            return redirect(url_for('adminmenu'))


    elif request.method == 'GET':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT project FROM project ")
        db_proj = cur.fetchall()                #all the projects   
        n=len(db_proj)                          #n of projects
        return render_template('admin_def.html',db_proj=db_proj,n=n)#, n=n, n2=n2, db_process=db_process,db_recit4=db_recit4,numb=numb,status=status)

########################################################
#
# Name: Defi
#
# Objective: Definitions of the employee
#
# Input Parameters:
#   name - name of the employee
#
# Return value and output parameters:
#   name - name of the employee
#
# Obs:
#   nil
#
# Version 1.0, 02/09/2022, by David Lobo
#########################################################
@app.route('/defi/<name>', methods=['GET', 'POST'])
def defi(name):
    if request.method == 'POST':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        if request.form["botao"] == "Voltar":
            return redirect(url_for('menu',name=name))
    elif request.method == 'GET':
        conn = mariadb.connect(
         host='127.0.0.1',
         port= 3306,
         user='root',
         password='',
         database='tese1')
        cur = conn.cursor()
        cur.execute("SELECT pass,mail,NIF,IBAN,morada FROM user WHERE name = ?", (name,))
        db_user = cur.fetchone()

        return render_template('def.html', name=name,db_user=db_user)