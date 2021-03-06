import csv
import os
import time
import traceback

from django.contrib import messages
from django.db import connection, transaction
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db import models as md
from django.core.paginator import Paginator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Count
from . import models, forms
from .pylouvain import PyLouvain
from scipy import stats
import matplotlib.pyplot as plt
import hashlib
import xlrd
import xlwt
import logging

# Create your views here.
class Variable(md.Model):
    Variable_name = md.CharField(max_length=128, primary_key=True)
    Value = md.IntegerField()

    def __str__(self):
        return self.Variable_name


# To encode the password

def get_result_fromat(data, cols):
    tmp_str = ""
    for col in cols:
        tmp_str += '"%s",' % (col)
    yield tmp_str.strip(",") + "\n"
    for row in data.iterator():
        tmp_str = ""
        for col in cols:
            tmp_str += '"%s",' % (str(row[col]))
        yield tmp_str.strip(',') + "\n"

def hash_code(s, salt='LTEsystem'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def hello(request):
    return render(request, 'login/index.html')


def index(request):
    pass
    return render(request, 'login/index.html')


def login(request):
    # if request.session.get('is_login', None):  # 已登录不允许重复登录
    #     return redirect('/main/')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        message = '请重新检查填写内容！'
        if username.strip() and password:  # 确保用户名和密码都不为空
            try:
                user = models.User.objects.get(name=username)
            except:
                message = '用户不存在！'
                return render(request, 'login/login.html', {'message': message})
            # 使用密码哈希值进行比对
            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/main/')
            else:
                message = '密码错误！'
                return render(request, 'login/login.html', {'message': message})
        else:
            return render(request, 'login/login.html', {'message': message})
    return render(request, 'login/login.html')


def adminlogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        dbpassword = request.POST.get('dbpassword')
        message = '请重新检查填写内容！'
        if username.strip() and password and dbpassword:
            try:
                user = models.Admin.objects.get(name=username)
            except:
                message = '该帐户不存在！'
                return render(request, 'login/adminlogin.html', {'message': message})

            if user.password != password:
                message = '密码错误！'
                return render(request, 'login/adminlogin.html', {'message': message})
            elif user.dbpassword == dbpassword:
                request.session['is_admin'] = True
                request.session['admin_id'] = user.id
                request.session['admin_name'] = user.name
                return redirect('/manager/')
            else:
                message = '数据库口令错误！'
                return render(request, 'login/adminlogin.html', {'message': message})
        else:
            return render(request, 'login/adminlogin.html', {'message': message})
    return render(request, 'login/adminlogin.html')


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，不用登出
        return redirect("/login/")
    request.session.flush()
    return redirect('/login/')


def adminlogout(request):
    if not request.session.get('is_admin', None):
        # 如果本来就未登录，不用登出
        return redirect("/adminlogin/")
    request.session.flush()
    return redirect('/adminlogin/')


def register(request):
    """实现注册功能，首先检查两次密码是否相同，再检查用户名是否已存在"""
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.save()

                return redirect('/login/')
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


# 用户主界面
def main(request):
    if not request.session.get('is_login', None):  # 未登录，不允许直接访问
        return redirect('/login/')
    return render(request, 'login/main.html', locals())


def manager(request):
    if not request.session.get('is_admin', None):  # 未登录，不允许直接访问
        return redirect('/adminlogin/')
    return render(request, 'login/manager.html', locals())


def datamanage(request):
    if not request.session.get('is_admin', None) and not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/datamanage.html', locals())


nrows = 1
cur_row = 0         # 全局变量，导入进度条使用
def importdata(request):
    global cur_row
    global nrows
    cur_row = 0
    logging.basicConfig(filename='import_data.log', filemode='w', level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    once_row = 300  # 每次读取行数，可修改
    if not request.session.get('is_admin', None) and not request.session.get('is_login', None):
        return redirect('/login/')
    if request.method == 'POST':
        f = request.FILES['upfile']
        filetype = f.name.split('.')[2]
        if filetype == 'xlsx' or filetype == 'xls':
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())  # 打开表对象
            table = wb.sheets()[0]  # 获取sheet1
            nrows = table.nrows  # 总行数
            message = '导入成功！'
            if request.POST['table'] == 'tbcell':
                earfcn_list = [37900, 38098, 38400, 38496, 38544, 38950, 39148]
                pci_list = [x for x in range(504)]
                vendor_list = ['华为', '中兴', '诺西', '爱立信', '贝尔', '大唐']
                style_list = ['室分', '宏站']
                try:
                    with transaction.atomic():
                        cur_row = 1  # 跳过表头，只读数据
                        while cur_row < nrows:
                            cnt = 0
                            row_list = []  # 使用行列表批量插入
                            while cnt < once_row and cur_row < nrows:
                                row = table.row_values(cur_row)  # 表的一行数据
                                if row[5] in earfcn_list and row[6] in pci_list and row[10] in vendor_list \
                                        and -180.00000 <= float(row[11]) <= 180.00000 and -90.00000 <= float(
                                    row[12]) <= 90.00000 and row[13] in style_list and not isinstance(row[18], str) \
                                        and row[18] == row[16] + row[17]:  # 数据清洗
                                    if models.Tbcell.objects.filter(sector_id=row[1]).count() != 0:  # 数据已存在，用新数据覆盖原数据
                                        models.Tbcell.objects.filter(sector_id=row[1]).delete()
                                    line = models.Tbcell(city=row[0],
                                                         sector_id=row[1],
                                                         sector_name=row[2],
                                                         enodebid=int(row[3]),
                                                         enodeb_name=row[4],
                                                         earfcn=int(row[5]),
                                                         pci=int(row[6]),
                                                         tac=int(row[9]) if not isinstance(row[9], str) else None,
                                                         vendor=row[10],
                                                         longitude=float(row[11]),
                                                         latitude=float(row[12]),
                                                         style=row[13],
                                                         azimuth=row[14],
                                                         height=row[15] if not isinstance(row[15], str) else None,
                                                         electtilt=row[16] if not isinstance(row[9], str) else None,
                                                         mechtilt=row[17] if not isinstance(row[9], str) else None,
                                                         totletilt=row[18])
                                    row_list.append(line)
                                else:
                                    logging.info("File( %s ) [line %d] is not qualified.", f.name, cur_row)
                                    # 日志文件记录被剔除数据的位置、编号
                                cnt += 1
                                cur_row += 1
                            models.Tbcell.objects.bulk_create(row_list)  # 批量导入一个list
                except Exception as e:
                    logging.exception(e)
                    message = '导入有误！请检查源表格式是否正确'
            elif request.POST['table'] == 'tbkpi':
                try:
                    with transaction.atomic():
                        cur_row = 1
                        while cur_row < nrows:
                            cnt = 0
                            row_list = []
                            while cnt < once_row and cur_row < nrows:
                                row = table.row_values(cur_row)
                                if row[0] != '' and row[2] != '' and row[3] != '':
                                    date_pre = time.strptime(row[0], "%m/%d/%Y %H:%M:%S")
                                    date_insert = time.strftime("%Y-%m-%d %H:%M:%S", date_pre)
                                    if models.Tbkpi.objects.filter(date=date_insert,
                                                                   sector_name=row[3]).count() != 0:  # 数据已存在，用新数据覆盖原数据
                                        models.Tbkpi.objects.filter(date=date_insert, sector_name=row[3]).delete()
                                    line = models.Tbkpi(date=date_insert,  # 读入是str，日期格式转换
                                                        enodeb_name=row[1],
                                                        sector=row[2],
                                                        sector_name=row[3],
                                                        rpc_establish=int(row[4]),
                                                        rpc_request=int(row[5]),
                                                        rpc_succrate=None if row[5] == 0 or isinstance(row[5],
                                                                                                       str) or isinstance(
                                                            row[6], str) else float(row[4]) / float(row[5]),
                                                        erab_succ=int(row[7]),
                                                        erab_att=int(row[8]),
                                                        erab_succrate=float(row[9]),
                                                        enodeb_erab_ex=int(row[10]),
                                                        sector_switch_erab_ex=int(row[11]),
                                                        erab_lossrate=float(row[12]),
                                                        ay=float(row[13]),
                                                        enodeb_reset_ue_release=int(row[14]),
                                                        ue_ex_release=int(row[15]),
                                                        ue_succ=int(row[16]),
                                                        lossrate=float(row[17]),
                                                        enodeb_in_diff_succ=int(row[18]),
                                                        enodeb_in_diff_att=int(row[19]),
                                                        enodeb_in_same_succ=int(row[20]),
                                                        enodeb_in_same_att=int(row[21]),
                                                        enodeb_out_diff_succ=int(row[22]),
                                                        enodeb_out_diff_att=int(row[23]),
                                                        enodeb_out_same_succ=int(row[24]),
                                                        enodeb_out_same_att=int(row[25]),
                                                        enodeb_in_succrate=float(row[26]) if not isinstance(row[26],
                                                                                                            str) else None,
                                                        enodeb_out_succrate=float(row[27]) if not isinstance(row[27],
                                                                                                             str) else None,
                                                        enodeb_same_succrate=float(row[28]) if not isinstance(row[28],
                                                                                                              str) else None,
                                                        enodeb_diff_succrate=float(row[29]) if not isinstance(row[29],
                                                                                                              str) else None,
                                                        enodeb_switch_succrate=float(row[30]) if not isinstance(row[30],
                                                                                                                str) else None,
                                                        pdcp_up=int(row[31]),
                                                        pdcp_down=int(row[32]),
                                                        rpc_rebuild=int(row[33]),
                                                        rpc_rebuildrate=float(row[34]),
                                                        rebuild_enodeb_out_same_succ=int(row[35]),
                                                        rebuild_enodeb_out_diff_succ=int(row[36]),
                                                        rebuild_enodeb_in_same_succ=int(row[37]),
                                                        rebuild_enodeb_in_diff_succ=int(row[38]),
                                                        enb_in_succ=int(row[39]),
                                                        eno_in_request=int(row[40]))
                                    row_list.append(line)
                                else:
                                    logging.info("File( %s ) [line %d] is not qualified.", f.name, cur_row)
                                cnt += 1
                                cur_row += 1
                            models.Tbkpi.objects.bulk_create(row_list)
                except Exception as e:
                    print(e.args)
                    logging.exception(e)
                    message = '导入有误！请检查源表格式是否正确'
            elif request.POST['table'] == 'tbprb':
                try:
                    with transaction.atomic():
                        cur_row = 1
                        while cur_row < nrows:
                            cnt = 0
                            row_list = []
                            while cnt < once_row and cur_row < nrows:
                                row = table.row_values(cur_row)
                                date_pre = time.strptime(row[0], "%m/%d/%Y %H:%M:%S")
                                date_insert = time.strftime("%Y-%m-%d %H:%M:%S", date_pre)
                                if models.Tbprb.objects.filter(date=date_insert,
                                                               sector_name=row[3]).count() != 0:  # 数据已存在，用新数据覆盖原数据
                                    models.Tbprb.objects.filter(date=date_insert, sector_name=row[3]).delete()
                                if row[0] != '' and row[3] != '':
                                    line = models.Tbprb(date=date_insert,
                                                        enodeb_name=row[1],
                                                        sector_description=row[2],
                                                        sector_name=row[3],
                                                        avr_noise_prb0=int(row[4]),
                                                        avr_noise_prb1=int(row[5]),
                                                        avr_noise_prb2=int(row[6]),
                                                        avr_noise_prb3=int(row[7]),
                                                        avr_noise_prb4=int(row[8]),
                                                        avr_noise_prb5=int(row[9]),
                                                        avr_noise_prb6=int(row[10]),
                                                        avr_noise_prb7=int(row[11]),
                                                        avr_noise_prb8=int(row[12]),
                                                        avr_noise_prb9=int(row[13]),
                                                        avr_noise_prb10=int(row[14]),
                                                        avr_noise_prb11=int(row[15]),
                                                        avr_noise_prb12=int(row[16]),
                                                        avr_noise_prb13=int(row[17]),
                                                        avr_noise_prb14=int(row[18]),
                                                        avr_noise_prb15=int(row[19]),
                                                        avr_noise_prb16=int(row[20]),
                                                        avr_noise_prb17=int(row[21]),
                                                        avr_noise_prb18=int(row[22]),
                                                        avr_noise_prb19=int(row[23]),
                                                        avr_noise_prb20=int(row[24]),
                                                        avr_noise_prb21=int(row[25]),
                                                        avr_noise_prb22=int(row[26]),
                                                        avr_noise_prb23=int(row[27]),
                                                        avr_noise_prb24=int(row[28]),
                                                        avr_noise_prb25=int(row[29]),
                                                        avr_noise_prb26=int(row[30]),
                                                        avr_noise_prb27=int(row[31]),
                                                        avr_noise_prb28=int(row[32]),
                                                        avr_noise_prb29=int(row[33]),
                                                        avr_noise_prb30=int(row[34]),
                                                        avr_noise_prb31=int(row[35]),
                                                        avr_noise_prb32=int(row[36]),
                                                        avr_noise_prb33=int(row[37]),
                                                        avr_noise_prb34=int(row[38]),
                                                        avr_noise_prb35=int(row[39]),
                                                        avr_noise_prb36=int(row[40]),
                                                        avr_noise_prb37=int(row[41]),
                                                        avr_noise_prb38=int(row[42]),
                                                        avr_noise_prb39=int(row[43]),
                                                        avr_noise_prb40=int(row[44]),
                                                        avr_noise_prb41=int(row[45]),
                                                        avr_noise_prb42=int(row[46]),
                                                        avr_noise_prb43=int(row[47]),
                                                        avr_noise_prb44=int(row[48]),
                                                        avr_noise_prb45=int(row[49]),
                                                        avr_noise_prb46=int(row[50]),
                                                        avr_noise_prb47=int(row[51]),
                                                        avr_noise_prb48=int(row[52]),
                                                        avr_noise_prb49=int(row[53]),
                                                        avr_noise_prb50=int(row[54]),
                                                        avr_noise_prb51=int(row[55]),
                                                        avr_noise_prb52=int(row[56]),
                                                        avr_noise_prb53=int(row[57]),
                                                        avr_noise_prb54=int(row[58]),
                                                        avr_noise_prb55=int(row[59]),
                                                        avr_noise_prb56=int(row[60]),
                                                        avr_noise_prb57=int(row[61]),
                                                        avr_noise_prb58=int(row[62]),
                                                        avr_noise_prb59=int(row[63]),
                                                        avr_noise_prb60=int(row[64]),
                                                        avr_noise_prb61=int(row[65]),
                                                        avr_noise_prb62=int(row[66]),
                                                        avr_noise_prb63=int(row[67]),
                                                        avr_noise_prb64=int(row[68]),
                                                        avr_noise_prb65=int(row[69]),
                                                        avr_noise_prb66=int(row[70]),
                                                        avr_noise_prb67=int(row[71]),
                                                        avr_noise_prb68=int(row[72]),
                                                        avr_noise_prb69=int(row[73]),
                                                        avr_noise_prb70=int(row[74]),
                                                        avr_noise_prb71=int(row[75]),
                                                        avr_noise_prb72=int(row[76]),
                                                        avr_noise_prb73=int(row[77]),
                                                        avr_noise_prb74=int(row[78]),
                                                        avr_noise_prb75=int(row[79]),
                                                        avr_noise_prb76=int(row[80]),
                                                        avr_noise_prb77=int(row[81]),
                                                        avr_noise_prb78=int(row[82]),
                                                        avr_noise_prb79=int(row[83]),
                                                        avr_noise_prb80=int(row[84]),
                                                        avr_noise_prb81=int(row[85]),
                                                        avr_noise_prb82=int(row[86]),
                                                        avr_noise_prb83=int(row[87]),
                                                        avr_noise_prb84=int(row[88]),
                                                        avr_noise_prb85=int(row[89]),
                                                        avr_noise_prb86=int(row[90]),
                                                        avr_noise_prb87=int(row[91]),
                                                        avr_noise_prb88=int(row[92]),
                                                        avr_noise_prb89=int(row[93]),
                                                        avr_noise_prb90=int(row[94]),
                                                        avr_noise_prb91=int(row[95]),
                                                        avr_noise_prb92=int(row[96]),
                                                        avr_noise_prb93=int(row[97]),
                                                        avr_noise_prb94=int(row[98]),
                                                        avr_noise_prb95=int(row[99]),
                                                        avr_noise_prb96=int(row[100]),
                                                        avr_noise_prb97=int(row[101]),
                                                        avr_noise_prb98=int(row[102]),
                                                        avr_noise_prb99=int(row[103]))
                                    row_list.append(line)
                                else:
                                    logging.info("File( %s ) [line %d] is not qualified.", f.name, cur_row)
                                cnt += 1
                                cur_row += 1
                            models.Tbprb.objects.bulk_create(row_list)
                except Exception as e:
                    logging.exception(e)
                    message = '导入有误！请检查源表格式是否正确'
        elif filetype == 'csv':
            f_csv = f.read().decode("utf-8")
            if request.POST['table'] == 'tbmrodata':
                # reader = csv.reader(f_csv)
                lines = f_csv.split("\r\n")
                try:
                    with transaction.atomic():
                        once_row = 5000
                        row_list = []
                        for index, line in enumerate(lines):
                            row = line.split(",")
                            if index == 0:
                                continue
                            if index % once_row == 0:  # 批量插入
                                models.Tbmrodata.objects.bulk_create(row_list)
                                row_list = []
                            if row[0] != '' and row[1] != '' and row[2] != '':
                                line_in = models.Tbmrodata(timestamp=row[0],
                                                           servingsector=row[1],
                                                           interferingsector=row[2],
                                                           ltescrsrp=float(row[3]),
                                                           ltencrsrp=float(row[4]),
                                                           ltencearfcn=int(row[5]),
                                                           ltencpci=int(row[6]))
                                row_list.append(line_in)
                            else:
                                logging.info("File( %s ) [line %d] is not qualified.", f.name, index + 1)
                        models.Tbmrodata.objects.bulk_create(row_list)  # 最后剩余数据
                        message = '导入成功！'
                except Exception as e:
                    logging.exception(e)
                    message = '导入有误！请检查源表格式是否正确'
            else:
                message = '请检查导入目的表是否相符'
        return render(request, 'login/datamanage.html', {'message': message})
    return render(request, 'login/datamanage.html')


def exportdata(request):
    response = HttpResponse("请先查询再导出！")
    if not request.session.get('is_admin', None) and not request.session.get('is_login', None):
        return redirect('/login/')
    if request.method == 'POST':
        table_name = request.POST['tables-export']
        format = request.POST['format']
        if (table_name == 'tbCell'):
            rows = models.Tbcell.objects.values()
            first = rows.first()
        elif (table_name == 'tbKPI'):
            rows = models.Tbkpi.objects.values()
            first = rows.first()
        elif (table_name == 'tbPRB'):
            rows = models.Tbprb.objects.values()
            first = rows.first()
        else:
            rows = models.Tbmrodata.objects.values()
            first = rows.first()
            print(123456)
        columns = []
        if not first:
            return render(request, "login/datamanage.html", {'message': '此数据表为空！'})
        for key in first:
            columns.append(key)
        try:
            if format == 'excel':
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="' + table_name + '.xls"'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet(table_name)
                # Sheet header, first row
                row_num = 0
                font_style = xlwt.XFStyle()
                font_style.font.bold = True
                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()
                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)
                for row in rows.iterator():
                    row_num += 1
                    # print(row.get(columns[0]))
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[columns[col_num]], font_style)
                wb.save(response)
                return response
            else:
                # response = HttpResponse(content_type='text/csv')
                response = StreamingHttpResponse(get_result_fromat(rows,columns))
                response['Content-Type'] = 'application/vnd.ms-excel'
                response['Content-Disposition'] = 'attachment;filename="{0}"'.format(table_name + '.csv')
                return response
        except:
            print('error')
    return response


def connectmanage(request):
    if not request.session.get('is_admin', None) and not request.session.get('is_login', None):
        return redirect('/login/')
    if request.method == "POST":
        time = request.POST.get('time')
        cachesize = request.POST.get('cachesize')
        if time != "":
            sql = "set global wait_timeout=" + time + ';'
            cursor = connection.cursor()
            try:
                cursor.execute(sql)
                transaction.commit()
                messages.success(request, "修改成功！")
            except Exception as e:
                traceback.print_exc(e)
        if cachesize != "":
            sql = "set  global key_buffer_size=" + cachesize + ';'
            cursor = connection.cursor()
            try:
                cursor.execute(sql)
                transaction.commit()
                messages.success(request, "修改成功！")
            except Exception as e:
                traceback.print_exc(e)
    return render(request, 'login/conmanage.html', locals())


# 允许该页面在<frame>中展示
@xframe_options_exempt
def initframe(request):
    return render(request, 'login/frame.html', locals())


@xframe_options_exempt
def infocate1(request):
    for var in Variable.objects.raw("show global variables like 'wait_timeout';"):
        wait_timeout = var.Value
    for variable in Variable.objects.raw("show global variables like 'interactive_timeout';"):
        interactive_timeout = variable.Value
    return render(request, 'login/info/cate1.html', locals())


@xframe_options_exempt
def infocate2(request):
    var_map = {}
    for var in Variable.objects.raw('show global variables;'):
        var_map[var.Variable_name] = var.Value
    # print(var_map)
    return render(request, 'login/info/cate2.html', locals())


@xframe_options_exempt
def infocate3(request):
    for var in Variable.objects.raw("show global variables like 'key_buffer_size';"):
        key_buffer_size = var.Value
    return render(request, 'login/info/cate3.html', locals())


'''业务查询功能'''


def info_query(request):
    if not request.session.get('is_admin', None) and not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/query/info_query.html', locals())


# show information of cell settings
def cell_info(request):
    cell_dict = []
    cellname = ''
    cellid = ''
    message = ''
    # 过滤出所有小区名，并通过模板传递
    name_list = models.Tbcell.objects.values_list("sector_name", flat=True).distinct()  # 查询表中所有小区名并去重
    if request.method == "POST":
        if request.POST.get('submit') == 'export':
            return load_csv(csv_filename="cell_info")
        if request.POST.get('submit') == 'text':
            cellname = request.POST.get('cellname')
            cellid = request.POST.get('cellid')
            # 判断是通过 name还是id 还是同时有
            if cellid and not cellname:
                cell_dict = models.Tbcell.objects.filter(sector_id=cellid).values()  # 使用.values把对象转为字典
            elif cellname and not cellid:
                cell_dict = models.Tbcell.objects.filter(sector_name=cellname).values()
            elif cellid and cellname:
                cell_dict = models.Tbcell.objects.filter(sector_id=cellid).values()
            if not cell_dict:
                message = "请检查输入是否正确!"
                return render(request, 'login/query/cell_info.html', locals())
        elif request.POST.get('submit') == 'select':
            cellname = request.POST.get('selected')
            cell_dict = models.Tbcell.objects.filter(sector_name=cellname).values()
        # 生成csv文件保存
        csv_file = "login/static/login/csv_files/cell_info.csv"
        # tablehead = []
        # rows_list = []
        # for key, val in dict.items():
        #     tablehead.append(key)
        #     rows_list.append(val)
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cell_dict[0].keys())
            for dict in cell_dict:
                writer.writerow(dict.values())
        return render(request, 'login/query/cell_info.html', locals())
    return render(request, 'login/query/cell_info.html', locals())


def enodeb_info(request):
    cell_dict = []
    enodeb_name = ''
    enodeb_id = ''
    message = ''
    # 过滤出所有基站名
    name_list = models.Tbcell.objects.values_list("enodeb_name", flat=True).distinct()  # 查询表中所有基站名并去重
    if request.method == "POST":
        if request.POST.get('submit') == 'export':
            return load_csv(csv_filename="enodeb_info")
        if request.POST.get('submit') == 'text':
            enodeb_name = request.POST.get('enodeb_name')
            enodeb_id = request.POST.get('enodeb_id')
            if enodeb_id and not enodeb_name:
                cell_dict = models.Tbcell.objects.filter(enodebid=enodeb_id).values()  # 使用.values把对象转为字典
            elif enodeb_name and not enodeb_id:
                cell_dict = models.Tbcell.objects.filter(enodeb_name=enodeb_name).values()
            elif enodeb_id and enodeb_name:  # 都存在，根据id
                cell_dict = models.Tbcell.objects.filter(enodebid=enodeb_id).values()
            if not cell_dict:
                message = "请检查输入是否正确!"
                return render(request, 'login/query/enodeb_info.html', locals())
        elif request.POST.get('submit') == 'select':
            enodeb_name = request.POST.get('selected')
            cell_dict = models.Tbcell.objects.filter(enodeb_name=enodeb_name).values()
        # 生成csv文件保存
        csv_file = "login/static/login/csv_files/enodeb_info.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cell_dict[0].keys())
            for dict in cell_dict:
                writer.writerow(dict.values())
        return render(request, 'login/query//enodeb_info.html', locals())
    return render(request, 'login/query/enodeb_info.html', locals())


# TODO 分页
def kpi_info(request):
    name_list = models.Tbkpi.objects.values_list("sector_name", flat=True).distinct()  # 查询表中所有小区名并去重
    if request.method == "POST":
        textname = request.POST.get('cellname')
        selected = request.POST.get('selected')
        if textname != '':
            cellname = textname
        else:
            cellname = selected

        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')

        select_attr = request.POST.get('attr')  # 得到选择的属性
        # 根据时间范围、属性、小区名查询，注意filter __gt  __lt
        attr_list = models.Tbkpi.objects.filter(sector_name=cellname, date__gte=date_start, date__lte=date_end).values(
            "date", select_attr)
        # 绘图 开始两行代码解决 plt 中文显示的问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        x_date = [str(data['date']).split()[0] for data in attr_list]
        y_value = [data[select_attr] for data in attr_list]
        plt.figure(figsize=(10, 4), dpi=100)
        plt.plot(x_date, y_value, marker="*", linewidth=1.0)
        plt.grid(color="k", linestyle=":")
        # plt.bar(x_date, y_value, width=0.5, color="#87CEFA")
        plt.title("小区：" + cellname + "    属性：" + select_attr)
        plt.xlabel('日期')
        plt.ylabel('属性值')
        for a, b in zip(x_date, y_value):
            plt.text(a, b, b, ha='center', va='bottom', fontsize=12)
        plt.savefig("login/static/login/images/kpi_info.png")

        img_dir = "login/images/kpi_info.png"
        belong_func = "kpi_info"
        return render(request, 'login/query/image_kpi.html', locals())
    return render(request, 'login/query/kpi_info.html', locals())


def load_image(request):
    if request.method == "POST":
        if request.POST.get('export') == 'kpi_info':
            try:
                with open("login/static/login/images/kpi_info.png", 'rb') as img_file:
                    response = HttpResponse(img_file)
                    response['Content-Type'] = 'application/octet-stream'
                    response['Content-Disposition'] = 'attachment;filename="kpi_info.png"'
                    return response
            except FileNotFoundError:
                response = HttpResponse("请先查询再导出！")
                return response
        elif request.POST.get('export') == 'prb_info':
            try:
                with open("login/static/login/images/prb_info.png", 'rb') as img_file:
                    response = HttpResponse(img_file)
                    response['Content-Type'] = 'application/octet-stream'
                    response['Content-Disposition'] = 'attachment;filename="prb_info.png"'
                    return response
            except FileNotFoundError:
                response = HttpResponse("请先查询再导出！")
                return response
        elif request.POST.get('export') == 'louvain':
            try:
                with open("login/static/login/images/louvain.png", 'rb') as img_file:
                    response = HttpResponse(img_file)
                    response['Content-Type'] = 'application/octet-stream'
                    response['Content-Disposition'] = 'attachment;filename="louvain.png"'
                    return response
            except FileNotFoundError:
                response = HttpResponse("请先查询再导出！")
                return response
    else:
        response = HttpResponse("请先查询再导出！")
        return response


def load_csv(csv_filename):
    try:
        with open("login/static/login/csv_files/" + csv_filename + ".csv", 'rb') as csv_file:
            response = HttpResponse(csv_file)
            response['Content-Type'] = 'text/csv'
            response['Content-Disposition'] = 'attachment;filename="cell_info.csv"'
            return response
    except FileNotFoundError:
        response = HttpResponse("请先查询再导出！")
        return response


def prb_info(request):
    range_list = [i for i in range(1, 100)]
    name_list = models.Tbprb.objects.values_list("sector_name", flat=True).distinct()  # 查询表中所有小区名并去重
    if request.method == "POST":
        textname = request.POST.get('cellname')
        selected = request.POST.get('selected')
        if textname != '':
            cellname = textname
        else:
            cellname = selected

        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')

        select_index = request.POST.get('index')  # 得到选择的属性
        select_prb = "avr_noise_prb" + str(select_index)
        # 根据时间范围、属性、小区名查询，注意filter __gt  __lt
        attr_list = models.Tbprbnew.objects.filter(sector_name=cellname, date__gte=date_start, date__lte=date_end).values(
            "date", select_prb)
        # 绘图 开始两行代码解决 plt 中文显示的问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        x_date = [str(data['date']) for data in attr_list]
        y_value = [data[select_prb] for data in attr_list]
        plt.figure(figsize=(20, 10), dpi=100)
        plt.plot(x_date, y_value, marker="*", linewidth=1.0)

        # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(5))
        plt.xticks(rotation=-90)
        plt.grid(color="k", linestyle=":")
        # plt.bar(x_date, y_value, width=0.5, color="#87CEFA")
        plt.title("小区：" + cellname + "    第" + select_index + "个PRB")
        plt.xlabel('时间（小时）')
        plt.ylabel(select_prb)
        for a, b in zip(x_date, y_value):
            plt.text(a, b, b, ha='center', va='bottom', fontsize=10)
        plt.savefig("login/static/login/images/prb_info.png")

        img_dir = "login/images/prb_info.png"
        belong_func = "prb_info"
        return render(request, 'login/query/image_prb.html', locals())
    return render(request, 'login/query/prb_info.html', locals())


def prb_stat(request):
    '''models.Tbprbnew.objects.all().delete()
    cursor = connection.cursor()
    sql = "call kpi_info()"
    cursor.execute(sql)'''
    # 通过StreamingHttpResponse指定返回格式为csv
    row = models.Tbprbnew.objects.values().first()
    columns = []
    for key in row:
        columns.append(key)

    def get_result(cols):
        tmp_str = ""
        for col in cols:
            tmp_str += '"%s",' % (col)
        yield tmp_str.strip(",") + "\n"
        for row in models.Tbprbnew.objects.values().iterator():
            tmp_str = row['date'].strftime('%Y-%m-%d %H:%M:%S')+','
            for i in range(1,len(cols)):
                tmp_str += '"%s",' % (row[cols[i]])
            yield tmp_str.strip(",") + "\n"
    def get_result2(cols):
        tmp_str = []
        for col in cols:
            tmp_str.append(col)
        yield tmp_str
        for row in models.Tbprbnew.objects.values().iterator():
            tmp_str.clear()
            tmp_str.append(row['date'].strftime('%Y-%m-%d %H:%M:%S'))
            for i in range(1,len(cols)):
                tmp_str.append(row[cols[i]])
            yield tmp_str

    response = StreamingHttpResponse(get_result(columns))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format('Tbprbnew.csv')
    return response


'''三元组分析'''


def analyze1(num):
    models.TbC2Inew.objects.all().delete()
    cursor = connection.cursor()
    sql = "call analyze1(" + str(num) + ")"
    print(sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        line = models.TbC2Inew(
            nc_sector_id=row[1],
            sc_sector_id=row[0],
            rsrp_avg=row[2],
            rsrp_std=row[3],
            probility_9=stats.norm.cdf((9 - row[2]) / row[3]),
            probility_6=stats.norm.cdf((6 - row[2]) / row[3]) - stats.norm.cdf(
                (-6 - row[2]) / row[3]),
        )
        line.save()
    return "success"

dict = []
def analyze2(request):
    paginator = Paginator(dict, 14)
    if request.method == "POST":
        flag = float(request.POST.get("bound_arg")) / 100.0
        num = request.POST.get("control_arg")
        if (num != ""):
            analyze1(int(num))
        try:
            A_list = models.TbC2Inew.objects.values_list('sc_sector_id').annotate(
                Count('sc_sector_id'))  # ('5641-129', 29)
        except:
            print("error")
            return render(request, 'login/analyze.html', locals())
        row_list = []
        # global dict
        dict.clear()
        for A in A_list:
            B_list = models.TbC2Inew.objects.values_list('nc_sector_id', 'probility_6').filter(
                sc_sector_id=A[0])  # ('253917-2', 0.459995836019516)
            for B in B_list:
                if (B[1] >= flag):
                    C_list = models.TbC2Inew.objects.values_list('sc_sector_id', 'probility_6').filter(
                        nc_sector_id=B[0])  # ('253917-2', 0.459995836019516)
                    for C in C_list:
                        if (C[0] != A[0]):
                            Prb_6 = models.TbC2Inew.objects.values_list('probility_6').filter(nc_sector_id=C[0],
                                                                                              sc_sector_id=A[0])
                            temp = [A[0], B[0], C[0]]
                            temp.sort()
                            if (temp not in dict and Prb_6.exists() and Prb_6[0][0] >= flag):
                                dict.append(temp)
        paginator = Paginator(dict, 14)  # 每页显示25条
        contacts = paginator.get_page(1)
    if request.method == "GET":
        page = request.GET.get('page')
        if page is not None:
            contacts = paginator.get_page(page)
    return render(request, 'login/analyze.html', locals())


'''
louvain画干扰图,主逻辑在pylouvain模块
'''


def getLouImages(request):
    if not os.path.exists("login/static/login/images/louvain.png"):
        pyl = PyLouvain.from_sql()
        partition, q = pyl.apply_method()
        pyl.drawNetworkGraph(partition, q)
    else:
        time.sleep(3)
    img_dir = "login/images/louvain.png"
    belong_func = "louvain"
    return render(request, 'login/query/image_louvain.html', locals())


'''
进度条
'''


def progress_bar(request):
    return render(request, 'progress.html')

'''
前端JS需要访问此程序来更新数据
'''


def show_progress(request):
    num_progress = cur_row * 100 / nrows
    return JsonResponse(num_progress, safe=False)