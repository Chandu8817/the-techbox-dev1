from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import EmployeeForm, TechToolForm, AssignToolForm
from django.contrib import messages
from django.views.generic import UpdateView


class DashBoard(View):

    @method_decorator(login_required(login_url="/"))
    def get(self, request):
        data = {}
        employees = Employee.objects.all()
        data['employees'] = employees
        tools = TechTool.objects.all()
        data['numberofemp'] = employees.count()
        data['numberoftools'] = tools.count()
        issued_tools = ToolsIssue.objects.all()
        data['issued_tools'] = issued_tools
        data['tools'] = tools

        trainee = 0
        tl = 0
        jd = 0
        sd = 0
        data['assigned_to_tl'] = 0
        data['assigned_to_sd'] = 0
        data['assigned_to_jd'] = 0
        data['assigned_to_trainee'] = 0
        issuedcount = issued_tools.count()

        for i in issued_tools:
            if i.empName.designation == '1':
                tl += 1

            elif i.empName.designation == '2':
                sd += 1

            elif i.empName.designation == '3':
                jd += 1

            elif i.empName.designation == '4':
                trainee += 1

        if trainee > 0:
            data['assigned_to_trainee'] = ((trainee * 100) / issuedcount)
        if jd > 0:
            data['assigned_to_jd'] += ((jd * 100) // issuedcount)
        if sd > 0:
            data['assigned_to_sd'] += ((sd * 100) // issuedcount)
        if tl > 0:
            data['assigned_to_tl'] += ((tl * 100) // issuedcount)

        return render(request, 'dashboard/dashboard.html', data)


class AddTechTools(View):

    def post(self, request):
        data = {}
        print(request.POST)
        add_too_form = TechToolForm(request.POST)
        if add_too_form.is_valid():
            add_too_form.save()
            newtool = TechTool.objects.get(name=request.POST.get('name'))
            print(newtool.id)
            data['newtool'] = newtool

        return render(request, 'dashboard/newtool.html', data)

    # def get(self, request):
    #     form = TechToolForm
    #     return render(request, 'dashboard/techtool_add.html', {'form': form})


class TechToolList(View):

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request):
        data = {}
        form = TechToolForm
        tools = TechTool.objects.all()
        data['tools'] = tools
        data['form'] = form
        return render(request, 'dashboard/techtool-list.html', data)


class UpdateTechTools(View):

    def post(self, request):
        data = {}
        try:
            pk = request.POST.get("id")
            print(request.POST)
            tool = TechTool.objects.get(id=pk)
            print(tool)

            status = request.POST.get('status')
            print(status)
            if status == 'on':
                tool.status = True
                tool.save()
                data['newtool'] = tool


            else:
                print(status)
                tool.status = False
                tool.save()
                data['newtool'] = tool
        except Exception as e:
            print(e)
        return render(request, 'dashboard/newtool.html', data)
    #
    #
    # def get(self, request):
    #
    #     form = TechToolForm()
    #     return render(request, 'dashboard/update-tool.html', {'form': form})


class DeleteTechTools(View):

    def post(self, request):
        tool_id = request.POST.get('id')
        print(tool_id)
        tool = TechTool.objects.get(id=tool_id)

        tool.delete()

        return redirect('techtool_list')


# Employee views


class AddEmployees(View):

    def get(self, request):
        form = EmployeeForm
        return render(request, 'dashboard/add-employee.html', {'form': form})

    def post(self, request, *args, **kwargs):
        try:
            data = {}
            emp_form = EmployeeForm(request.POST, request.FILES)
            print(request.POST),
            print(request.FILES)
            if emp_form.is_valid():
                emp_form.save()
                messages.success(request, 'Employee Add Successfully ')
                newemp = Employee.objects.get(name=request.POST.get('name'))
                data['newemp'] = newemp

                return render(request, 'dashboard/newempdata.html', data)
            else:
                return HttpResponse("not valid")

        except Exception as e:
            print(e)
        return render(request, 'dashboard/employee-list.html')


class EmployeeList(View):

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request):
        data = {}
        employees = Employee.objects.all()
        data['employees'] = employees
        data['form'] = EmployeeForm

        return render(request, 'dashboard/employee-list.html', data)


class EmployeeDetail(View):

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, pk):
        data = {}
        employee = Employee.objects.get(pk=pk)
        data['employee'] = employee

        return render(request, 'dashboard/employee-profile.html', data)


class EmployeeUpdate(View):

    def get(self, request, pk):
        form = EmployeeForm
        return render(request, 'dashboard/update-employee.html', {'form': form})

    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, pk):

        employee = Employee.objects.get(id=pk)
        emp_upd_form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if emp_upd_form.is_valid():
            emp_upd_form.save()
            return redirect('employee_list')
        else:
            return HttpResponse("update not valid ")


class EmployeeDelete(View):

    @method_decorator(login_required(login_url="/login/"))
    def post(self, request):
        data = {}
        pk = request.POST.get('id')
        employee = Employee.objects.get(pk=pk)
        employee.delete()
        messages.success(request, 'Employee Delete Successfully ')

        return redirect('employee_list')


class AssignTools(View):
    def post(self, request, *args, **kwargs):
        assign_form = AssignToolForm(request.POST)

        if assign_form.is_valid():
            t_id = request.POST.get('techTool')

            tool = TechTool.objects.get(id=t_id)

            if tool.status == True:
                assign_form.save()
                messages.success(request, "tool are issued")
                return redirect('tools_issued')

            else:
                messages.error(request, "tool not available")
                return redirect('assign_tool')

        else:
            return HttpResponse("no tool issued")
    def get(self, request):
        assign_from = AssignToolForm

        return render(request, 'dashboard/assign-tool.html', {'assign_from':assign_from})


class ToolIssued(View):

    def get(self, request):
        assign_from = AssignToolForm
        issued_tools = ToolsIssue.objects.all()
        return render(request, 'dashboard/tool-issue.html', {'issued_tools': issued_tools,'assign_from':assign_from})
