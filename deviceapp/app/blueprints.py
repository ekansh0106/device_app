#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Apr 12, 2022 11:30:34

@author: ekansh
"""

# Standard Library
import datetime
from datetime import date
from sqlalchemy import func
from flask import send_file
from reportlab.lib import colors
from flask import request, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from flask_httpauth import HTTPBasicAuth
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph,Table,TableStyle
from flask import Blueprint,render_template,redirect,url_for,session
from werkzeug.security import generate_password_hash, check_password_hash


# User Defined Library
from .models import App
from .extensions import db
from .config import PDF_PATH


api_blueprint = Blueprint('main', __name__)
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("QWERT"),
    "demo": generate_password_hash("ZXCVB")
}

# The function decorated with the verify_password decorator receives the username
    # and password sent by the client. If the credentials belong to a user, then  
    # the function should return the user object. If the credentials are invalid  
    # the function can return None or False.
@auth.verify_password
def verify_password(username, password):
    try:
        
        # to allow authentication only when request has a content-type 
        if request.content_type != None:
            
            # to allow authentication only when request has content-type as json
            if (request.content_type=='application/json'):
                if username in users and \
                        check_password_hash(users.get(username), password):
                    return username
            
            # to authenticate only when request has content-type as form-encode
            elif(request.content_type=="application/x-www-form-urlencoded"):
                
                # on successful login render index.html along with options  
                        # for dropdown
                if username in users and \
                        check_password_hash(users.get(username), password):
                    return render_template('index.html',devices=set(db.session.query(App.deviceid)))
                
                # if username is invalid redirect to .verify with error message 
                elif not username in users:
                    # return redirect('/login')
                    messages = "Invalid Username"
                    session['messages'] = messages
                    return redirect(url_for('.verify'))
                
                # if password is invalid redirect to .verify with error message
                elif username in users and  not check_password_hash(users.get(username), password):
                    messages = "Invalid Password"
                    session['messages'] = messages
                    return redirect(url_for('.verify'))
        else:
            raise Exception("Unauthorised Access")
    except Exception as e:
        return str(e)
            

# class AppSchema(ma.Schema):
#         class meta:
#             model = App

@api_blueprint.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return response


# route to display login page when using UI to access apis
@api_blueprint.route("/login", methods=["POST","GET"])
def login():
    return render_template('login.html')

       
# for unsuccessful login attempt in UI user is redirected to this route 
    # displaying the error message for which the login attempt failed
@api_blueprint.route("/verify", methods=["POST","GET"])
def verify():
    messages = session['messages']
    return render_template('login.html',error=messages)


# this route clears the session for successful logout from UI
@api_blueprint.route("/logout", methods=["POST","GET"])
def logout():
    session.pop('messages', None)
    return redirect(url_for('.login'))


# this route redirects to verify_password func to check if the uname and pass 
    # entered by user in UI is valid ,if invalid redirects to login route
@api_blueprint.route("/dashboard", methods=["POST","GET"])
# @auth.login_required
def dashboard():
    try:
        username=request.form['username']
        password=request.form['password']
        return verify_password(username, password)
    except:
        return redirect('/login')


# this api endpoint can only be accessed if request has content-type as json
@api_blueprint.route("/add-data/", methods=["POST"])
@auth.login_required
def add_data():
    """
    Function is to add single or multiple records in database
        Each parameter data should be in json format in request body, 
        (ie. "key":"value" pairs) for every record which will then be enclosed
        inside a list 

        Parameters to pass in json request body
        --------------------------------------
        device_id : str
            DESCRIPTION:-
                Name/Id of the device
        data1 : str
            DESCRIPTION:-
                data value between -99999 and 99999
        data2 : str
            DESCRIPTION:-
                data value between -99999 and 99999
        data3 : str
            DESCRIPTION:-
                data value between -99999 and 99999
        data4 : str
            DESCRIPTION:-
                data value between -99999 and 99999
        data5 : str
            DESCRIPTION:-
                data value between -99999 and 99999
        dt_start : str
            DESCRIPTION:-
                date and time only in this format(Mar 14, 2021 19:35:49)

        Returns
        -------
        Success message if all parameters are entered correctly else raises an
        Exception
    """
    try:
        data = request.json
        try:
            for d in data:
                deviceid = d.get('deviceid')
                data1 = d.get('data1')
                data2 = d.get('data2')
                data3 = d.get('data3')
                data4 = d.get('data4')
                data5 = d.get('data5')
                dt_start = d.get('dt_start')
                dt_start = datetime.datetime.strptime(dt_start, '%b %d, %Y %H:%M:%S')
                if deviceid and data1 and data2 and data3 and data4 and data5:
                    if len(deviceid)<=9:
                        list1 = []
                        for x in [data1,data2,data3,data4,data5]:
                            x = int(x)
                            if len(str(abs(x)).split("."))==2:
                                if len(str(abs(x)).split(".")[0])<6 and len(str(abs(x)).split(".")[1])<4:
                                    list1.append(True)
                                else:
                                    list1.append(False)
                            elif len(str(abs(x)).split("."))==1:
                                if len(str(abs(x)).split(".")[0])<6:
                                    list1.append(True)
                                else:
                                    list1.append(False)
                            else:
                                list1.append(False)
                        if False not in list1:
                            a = App(deviceid=deviceid,data1=data1,data2=data2,data3=data3,data4=data4,data5=data5,dt_start=dt_start)
                            db.session.add(a)
                            db.session.commit()
                        else:
                            raise Exception("Out of range values")
                    else:
                        raise Exception("Deviceid should have 5 characters")
                else:
                    raise Exception("Values missing ")
            return "successfuly updated values in database"  
        except Exception as e:
            return str(e)
    except Exception as e:
        return str(e)
        


# this api endpoint can only be accessed if request has content-type as json or
    # form-encode
@api_blueprint.route("/search-by-deviceid", methods=["POST"])
@auth.login_required
def search_by_deviceid():
    """
    Function is to search records in database
        Each parameter data should be in json format in request body, 
        (ie. "key":"value" pairs) 

        Parameters to pass in json request body
        --------------------------------------
        device_id : str
            DESCRIPTION:-
                Name/Id of the device
        from : str
            DESCRIPTION:-
                (Optional parameter)
                date only in this format("yyyy-mm-dd")
               
        to : str
            DESCRIPTION:-
                (Optional parameter)
                date only in this format("yyyy-mm-dd")

        Returns
        -------
        Latest 25 records if only deviceid is specified and for specific date 
        "from" parameter should be passed and if "from" and "to" parameters are
        passed, records between them will be returned
    """
    try:
        if (request.content_type=='application/json'):
            data = request.json
            deviceid = data.get('deviceid')
            from_date = data.get('from')
            to_date = data.get('to')
            if not from_date and deviceid:
                try:
                    device = db.session.query(App).filter(App.deviceid==deviceid).order_by(App.dt_start.desc()).limit(25).all()
                    if len(device)==0:
                        raise Exception(f"No device Found with deviceid: {deviceid}")
                    else:
                        return jsonify(device)
                except Exception as e:
                    return str(e)
            elif from_date and deviceid and not to_date:
                try:
                    from_date = from_date.split("-")
                    year = from_date[0]
                    month = from_date[1]
                    day = from_date[2]
                    if year and month and day:
                        from_date = date(int(year), int(month), int(day))
                        device = App.query.filter(func.date(App.dt_start)==from_date,App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            raise Exception(f"No record found for date {day}/{month}/{year} of deviceid: {deviceid}")
                        else:
                            return jsonify(device)
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            elif from_date and to_date and deviceid:
                try:
                    from_date = from_date.split("-")
                    to_date = to_date.split("-")
                    fyear = from_date[0]
                    fmonth = from_date[1]
                    fday = from_date[2]
                    tyear = to_date[0]
                    tmonth = to_date[1]
                    tday = to_date[2]
                    if fyear and fmonth and fday and tyear and tmonth and tday:
                        from_date = date(int(fyear), int(fmonth), int(fday))
                        to_date = datetime.datetime(int(tyear), int(tmonth), int(tday),23,59,59)
                        device = App.query.filter(App.dt_start.between(from_date,to_date),App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            raise Exception(f"No record found for date {day}/{month}/{year} of deviceid: {deviceid}")
                        else:
                            return jsonify(device)
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            else:
                raise Exception("Enter DeviceId to get data")
        elif(request.content_type=="application/x-www-form-urlencoded"):
            data = request.form
            deviceid = data.get('deviceid')
            from_date = data.get('from')
            to_date = data.get('to')
            if not from_date and deviceid:
                try:
                    device = db.session.query(App).filter(App.deviceid==deviceid).order_by(App.dt_start.desc()).limit(25).all()
                    if len(device)==0:
                        return redirect(url_for('.dashboard',error="No device Found with deviceid: "+deviceid))
                        # return render_template("index.html",error="No device Found with deviceid: "+deviceid)
                    else:
                        # return redirect(url_for('.dashboard',deviceid=device))
                        return render_template('index.html',deviceid=device,devices=set(db.session.query(App.deviceid)))
                except Exception as e:
                    return str(e)
            elif from_date and deviceid and not to_date:
                try:
                    from_date = from_date.split("-")
                    year = from_date[0]
                    month = from_date[1]
                    day = from_date[2]
                    if year and month and day:
                        from_date = date(int(year), int(month), int(day))
                        device = App.query.filter(func.date(App.dt_start)==from_date,App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            return render_template('index.html',error=f"No record found for date {day}/{month}/{year} of deviceid: {deviceid}",devices=set(db.session.query(App.deviceid)))
                        else:
                            return render_template('index.html',deviceid=device,from_date=str(from_date),devices=set(db.session.query(App.deviceid)))
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            elif from_date and to_date and deviceid:
                try:
                    from_date = from_date.split("-")
                    to_date = to_date.split("-")
                    fyear = from_date[0]
                    fmonth = from_date[1]
                    fday = from_date[2]
                    tyear = to_date[0]
                    tmonth = to_date[1]
                    tday = to_date[2]
                    if fyear and fmonth and fday and tyear and tmonth and tday:
                        from_date = date(int(fyear), int(fmonth), int(fday))
                        to_date = datetime.datetime(int(tyear), int(tmonth), int(tday),23,59,59)
                        device = App.query.filter(App.dt_start.between(from_date,to_date),App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            return render_template('index.html',error=f"No record found for date {day}/{month}/{year} of deviceid: {deviceid}",devices=set(db.session.query(App.deviceid)))
                        else:
                            return render_template('index.html',deviceid=device,from_date=str(from_date),to_date=str(date(int(tyear), int(tmonth), int(tday))),devices=set(db.session.query(App.deviceid)))
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            else:
                raise Exception("Enter DeviceId to get data")
        else:
            raise Exception("Invalid Format")
    except Exception as e:
        return str(e)
        
        
# this api endpoint can only be accessed if request has content-type as json or
    # form-encode
@api_blueprint.route("/return-pdf", methods=["POST"])
@auth.login_required
def get_pdf():
    """
    Function is to get queried records from database in pdf format
        Each parameter data should be in json format in request body, 
        (ie. "key":"value" pairs) 

        Parameters to pass in json request body
        --------------------------------------
        device_id : str
            DESCRIPTION:-
                Name/Id of the device
        from : str
            DESCRIPTION:-
                (Optional parameter)
                date only in this format("yyyy-mm-dd")
               
        to : str
            DESCRIPTION:-
                (Optional parameter)
                date only in this format("yyyy-mm-dd")

        Returns
        -------
        Latest 25 records if only deviceid is specified and for specific date 
        "from" parameter should be passed and if "from" and "to" parameters are
        passed, records between them will be returned
    """
    try:
        if (request.content_type=='application/json'):
            data = request.json
            deviceid = data.get('deviceid')
            from_date = data.get('from')
            to_date = data.get('to')
            if not from_date and deviceid:
                try:
                    device = db.session.query(App).filter(App.deviceid==deviceid).order_by(App.dt_start.desc()).limit(25).all()
                    if len(device)==0:
                        raise Exception(f"No device Found with deviceid: {deviceid}")
                    # else:
                    #     return jsonify(device)
                except Exception as e:
                    return str(e)
            elif from_date and deviceid and not to_date:
                try:
                    from_date = from_date.split("-")
                    year = from_date[0]
                    month = from_date[1]
                    day = from_date[2]
                    if year and month and day:
                        from_date = date(int(year), int(month), int(day))
                        device = App.query.filter(func.date(App.dt_start)==from_date,App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            raise Exception(f"No record found for date {day}/{month}/{year} of deviceid: {deviceid}")
                        # else:
                        #     return jsonify(device)
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            elif from_date and to_date and deviceid:
                try:
                    from_date = from_date.split("-")
                    to_date = to_date.split("-")
                    fyear = from_date[0]
                    fmonth = from_date[1]
                    fday = from_date[2]
                    tyear = to_date[0]
                    tmonth = to_date[1]
                    tday = to_date[2]
                    if fyear and fmonth and fday and tyear and tmonth and tday:
                        from_date = date(int(fyear), int(fmonth), int(fday))
                        to_date = datetime.datetime(int(tyear), int(tmonth), int(tday),23,59,59)
                        device = App.query.filter(App.dt_start.between(from_date,to_date),App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            raise Exception(f"No record found between {fday}/{fmonth}/{fyear} and {tday}/{tmonth}/{tyear} of deviceid: {deviceid}")
                        # else:
                        #     return jsonify(device)
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            else:
                raise Exception("Enter DeviceId to get data")
        elif(request.content_type=="application/x-www-form-urlencoded"):
            data = request.form
            deviceid = data.get('deviceid')
            from_date = data.get('from')
            to_date = data.get('to')
            if not from_date and deviceid:
                try:
                    device = db.session.query(App).filter(App.deviceid==deviceid).order_by(App.dt_start.desc()).limit(25).all()
                    if len(device)==0:
                        return redirect(url_for('.dashboard',error="No device Found with deviceid: "+deviceid))
                    # else:
                    #     return render_template('index.html',deviceid=device,devices=set(db.session.query(App.deviceid)))
                except Exception as e:
                    return str(e)
            elif from_date and deviceid and not to_date:
                try:
                    from_date = from_date.split("-")
                    year = from_date[0]
                    month = from_date[1]
                    day = from_date[2]
                    if year and month and day:
                        from_date = date(int(year), int(month), int(day))
                        device = App.query.filter(func.date(App.dt_start)==from_date,App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            return render_template('index.html',error=f"No record found for date {day}/{month}/{year} of deviceid: {deviceid}",devices=set(db.session.query(App.deviceid)))
                        # else:
                        #     return render_template('index.html',deviceid=device,from_date=str(from_date),devices=set(db.session.query(App.deviceid)))
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            elif from_date and to_date and deviceid:
                try:
                    from_date = from_date.split("-")
                    to_date = to_date.split("-")
                    fyear = from_date[0]
                    fmonth = from_date[1]
                    fday = from_date[2]
                    tyear = to_date[0]
                    tmonth = to_date[1]
                    tday = to_date[2]
                    if fyear and fmonth and fday and tyear and tmonth and tday:
                        from_date = date(int(fyear), int(fmonth), int(fday))
                        to_date = datetime.datetime(int(tyear), int(tmonth), int(tday),23,59,59)
                        device = App.query.filter(App.dt_start.between(from_date,to_date),App.deviceid==deviceid).order_by(App.dt_start.desc()).all()
                        if len(device)==0:
                            return render_template('index.html',error=f"No record found between {fday}/{fmonth}/{fyear} and {tday}/{tmonth}/{tyear} of deviceid: {deviceid}",devices=set(db.session.query(App.deviceid)))
                        # else:
                        #     return render_template('index.html',deviceid=device,from_date=str(from_date),to_date=str(to_date),devices=set(db.session.query(App.deviceid)))
                    else:
                        raise Exception("Missing values for date")
                except Exception as e:
                    return str(e)
            else:
                raise Exception("Enter DeviceId to get data")
        else:
            raise Exception("Invalid Format")
        # device = App.query.all()
        pdf = canvas.Canvas("report.pdf")
        styles = getSampleStyleSheet()
        tdata = [["timestamp","data1","data2","data3","data4","data5"]]
        for row in device:
            rowdata = []
            data1 = row.data1
            data2 = row.data2
            data3 = row.data3
            data4 = row.data4
            data5 = row.data5
            start = row.dt_start
            dt_start = start.strftime('%Y-%m-%d %I:%M:%S %p')
            rowdata.append(dt_start)
            rowdata.append(data1)
            rowdata.append(data2)
            rowdata.append(data3)
            rowdata.append(data4)
            rowdata.append(data5)
            tdata.append(rowdata)

        for i in range(len(tdata)):
            if(i%26==0 and i>0):
                pdf.showPage()
                text = "Ref: "
                style=styles['Normal']
                para = Paragraph(text, style)
                para.wrapOn(pdf,50,50)
                para.drawOn(pdf,50,700)
                text = "Date: "+ str(datetime.datetime.now().date())
                style=styles['Normal']
                para = Paragraph(text, style)
                para.wrapOn(pdf,100,50)
                para.drawOn(pdf,450,700)
                text = "DeviceId: "+ str(deviceid)
                style=styles['Heading3']
                para = Paragraph(text, style)
                para.wrapOn(pdf,200,50)
                para.drawOn(pdf,50,630)

                table = Table([tdata[0]],colWidths=[120,80,80,80,80,80])
                ts = TableStyle([("GRID",(0,0),(-1,-1),1,colors.black),
                                ('FONT', (0,0), (-1,-1), 'Times-Bold',10),
                                ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
                                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                ])
                table.setStyle(ts)
                table.wrapOn(pdf, 35, 600)
                table.drawOn(pdf, 35, 600)

            if i == 0:
                
                text = "Ref: "
                style=styles['Normal']
                style.spaceAfter=1.5*inch
                para = Paragraph(text, style)
                para.wrapOn(pdf,50,50)
                para.drawOn(pdf,50,700)
                text = "Date: "+ str(datetime.datetime.now().date())
                style=styles['Normal']
                para = Paragraph(text, style)
                para.wrapOn(pdf,100,50)
                para.drawOn(pdf,450,700)
                text = "DeviceId: "+ str(deviceid)
                style=styles['Heading3']
                para = Paragraph(text, style)
                para.wrapOn(pdf,200,50)
                para.drawOn(pdf,50,630)

                table = Table([tdata[0]],colWidths=[120,80,80,80,80,80])
                ts = TableStyle([("GRID",(0,0),(-1,-1),1,colors.black),
                                ('FONT', (0,0), (-1,-1), 'Times-Bold',10),
                                ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
                                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                ])
                table.setStyle(ts)
                table.wrapOn(pdf, 35, 582)
                table.drawOn(pdf, 35, 582)

            else:
                table = Table([tdata[i]],colWidths=[120,80,80,80,80,80])
                ts = TableStyle([("GRID",(0,0),(-1,-1),1,colors.black),
                                ('FONT', (0,0), (-1,-1), 'Times-Bold',10),
                                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                ])
                table.setStyle(ts)
                table.wrapOn(pdf, 35, 582-((i%26)*18))
                table.drawOn(pdf, 35, 582-((i%26)*18))

        pdf.save()
        
        return send_file(f"{PDF_PATH}/report.pdf" , attachment_filename=f"report_{deviceid}.pdf", as_attachment=True)
    except Exception as e:
        return str(e)

# @api_blueprint.route("/search-by-time/", methods=["POST"])
# @auth.login_required
# def get_time():
#     try:
#         data = request.json 
#     except Exception as e:
#         return str(e)
#     else:
#         # deviceid = data.get('deviceid')
#         from_date = data.get('fromdate')
#         to_date = data.get('todate')
#         from_date = from_date.split("-")
#         to_date = to_date.split("-")
#         fyear = from_date[0]
#         fmonth = from_date[1]
#         fday = from_date[2]
#         tyear = to_date[0]
#         tmonth = to_date[1]
#         tday = to_date[2]
#         connections = []
#         first_date = date(fyear, fmonth, fday)
#         last_date = date(tyear, tmonth, tday,23,59,59)
#         d = App.query.filter(App.dt_start.between(first_date, last_date)).all()
#         connections.append(d)
#         return jsonify(connections)
