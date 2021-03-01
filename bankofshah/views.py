from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from pymongo import MongoClient
from datetime import datetime
from django.core.mail import send_mail


db_client = MongoClient('mongodb+srv://super_user:Vrajshah147@cluster0.q7xe6.mongodb.net/Bank?retryWrites=true&w=majority')
db = db_client['Bank']
col = db['bank_trans']
authCol = db['users']
global_user = db['global_user']


# # Create your views here.
def contact(request):
        return render(request, 'contact.html')

def frontpage(request):
    return render(request, 'frontpage.html')

def home(request):
    data10 = list(global_user.find().sort('user', -1))
    logged_in_user = data10[0]['user']

    query = {"username": logged_in_user}
    # userquery = {"user"}

    data = list(authCol.find(query))
    print(data)
    return render(request, 'home.html',  {'data': data})

def table(request):
    data = list(global_user.find().sort('user', -1))
    logged_in_user = data[0]['user']


    query = {"username": logged_in_user}
    data = list(col.find(query).sort("date",-1))
    print(logged_in_user)
    print(data)
    return render(request, 'table.html', {'transactions': data})

def transfer(request):
    if request.method == "POST":
        receiver = request.POST['receiver']
        a = request.POST['amount']
        amount = float(a)

        data = list(global_user.find().sort('user', -1))
        logged_in_user = data[0]['user']

        query1 = {"username": logged_in_user}
        data1 = list(col.find(query1).sort("date", -1))
        print("1")
        print(data1)

        query2 = {"username": receiver}
        data2 = list(col.find(query2).sort("date", -1))
        print("2")
        print(data2)

        authentication_user = list(authCol.find(query2))


        #check if user exists
        if (len(authentication_user) > 0):

            # widthdraw from senders account
            try:
                previous_total_amount = (data1[0]['total_amount'])
                print("got the previous amount")
                if (amount <= previous_total_amount):
                    new_total_amount = previous_total_amount - amount

                    print("about to enter into db")

                    data3 = list(col.find().sort("id", -1))
                    try:
                        previous_id = (data3[0]['id'])
                        new_id = previous_id + 1
                    except:
                        new_id = 1

                    new_entry = {
                        "id": new_id,
                        "username": logged_in_user,
                        "deposit": "",
                        "withdraw": amount,
                        "total_amount": new_total_amount,
                        "date": datetime.now()
                    }
                    col.insert_one(new_entry)
                else:
                    messages.info(request, "Insufficient funds")
                    return redirect('transfer')
            except:
                messages.info(request, "No funds")
                return redirect('transfer')

            # deposit into recievers account
            try:
                previous_total_amount = (data2[0]['total_amount'])
            except:
                previous_total_amount = 0
            new_total_amount = amount + previous_total_amount

            data4 = list(col.find().sort("id", -1))
            try:
                previous_id = (data4[0]['id'])
                new_id = previous_id + 1
            except:
                new_id = 1

            new_entry = {
                "id": new_id,
                "username": receiver,
                "deposit": amount,
                "withdraw": "",
                "total_amount": new_total_amount,
                "date": datetime.now()
            }
            col.insert_one(new_entry)

            email()
            return redirect('table')
        else:
            messages.info(request, "User does not exist!")
            return redirect('transfer')

    else:
        return render(request, "transfer.html")


def deposit(request):
    if request.method == "POST":
        a = request.POST['amount']
        #print(type(a))
        amount = float(a)
        #print(type(amount))

        data10 = list(global_user.find().sort('user', -1))
        logged_in_user = data10[0]['user']


        query = {"username": logged_in_user}
        data = list(col.find(query).sort("date",-1))

        data2 = list(col.find().sort("id", -1))
        try:
            previous_id =(data2[0]['id'])
            new_id = previous_id + 1
        except:
            new_id = 1

        try:
            previous_total_amount = (data[0]['total_amount'])
        except:
            previous_total_amount = 0
        new_total_amount = amount + previous_total_amount


        new_entry = {
                     "id": new_id,
                     "username": logged_in_user,
                     "deposit": amount,
                     "withdraw": "",
                     "total_amount": new_total_amount,
                     "date": datetime.now()
                     }
        col.insert_one(new_entry)

        email()
        return redirect('table')

    else:
        return render(request, 'deposit.html')

def withdraw(request):
    if request.method == "POST":
        a = request.POST['amount']
        amount = float(a)

        data10 = list(global_user.find().sort('user', -1))
        logged_in_user = data10[0]['user']

        query = {"username": logged_in_user}
        data = list(col.find(query).sort("date",-1))

        data2 = list(col.find().sort("id", -1))
        try:
            previous_id = (data2[0]['id'])
            new_id = previous_id + 1
        except:
            new_id = 1

        try:
            previous_total_amount = (data[0]['total_amount'])
            if (amount <= previous_total_amount):
                new_total_amount = previous_total_amount - amount

                new_entry = {
                    "id": new_id,
                    "username": logged_in_user,
                    "deposit": "",
                    "withdraw": amount,
                    "total_amount": new_total_amount,
                    "date": datetime.now()
                }
                col.insert_one(new_entry)
                email()
                return redirect('table')
            else:
                messages.info(request, "Insufficient funds")
                return redirect('withdraw')
        except:
            messages.info(request, "No funds")
            return redirect('withdraw')

    else:
        return render(request, 'withdraw.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['user']
        password = request.POST['pass']

        print("got the user and pass")

        query = {"username": username, "password": password}
        data = list(authCol.find(query))
        if (len(data) > 0):
            print("verified user!")

            data = list(global_user.find().sort('user',-1))
            old_global = data[0]['user']

            old_entry = {'user': old_global}
            new_entry = { "$set": {'user': username}}
            global_user.update_one(old_entry, new_entry)

            print("updated the db for global user")

            return redirect('home')
        else:
            messages.info(request, "Incorrect Credentials")
            return redirect('login')

    else:
        return render(request, 'login.html')

def register(request):

    if request.method == 'POST':

        first_name = request.POST['fname']
        last_name = request.POST['lname']
        username = request.POST['user']
        password = request.POST['pass']
        email = request.POST['email']

        query = {"username":username, "email":email}
        data = list(authCol.find(query))
        if(len(data)>0):
            messages.info(request, "Username Taken")
            return redirect('/register')
        else:
            entry = {
                "first_name": first_name,
                "last_name": last_name,
                "username":username,
                "password": password,
                "email":email
                     }
            x = authCol.insert_one(entry)
            return redirect('login')

    else:
        return render(request, 'register.html')

def logout(request):
    return redirect('/')


def email():
    data10 = list(global_user.find().sort('user', -1))
    logged_in_user = data10[0]['user']

    query = {"username": logged_in_user}
    data = list(authCol.find(query))
    email = data[0]["email"]

    send_mail(
        'Trasaction Notice',
        'This is an automated message from Bank of Shah, a transaction has been made using this account.',
        'bankofshah@gmail.com',
        [email],
        fail_silently=False
    )


