from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from openpyxl import Workbook
from django.http import HttpResponse
import os

from .models import Student

# LOGIN_PAGE

def login_page(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        username_exists = User.objects.filter(
            username=username
        ).exists()

        if not username_exists:
            error = "Username is wrong"
        else:
            error = "Password is wrong"

        return render(request, "students/login.html", {
            "error": error
        })

    return render(request, "students/login.html")


# HOME PAGE

@login_required
def home(request):

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "save":

            registration_no = request.POST.get("registration_no")
            name = request.POST.get("name")
            course = request.POST.get("course")
            join_date = request.POST.get("join_date")
            course_fees = Decimal(request.POST.get("course_fees"))
            paid_fees = Decimal(request.POST.get("paid_fees"))

            # To Pay can be blank
            to_pay = request.POST.get("to_pay") or None

            certificate = request.POST.get("certificate")
            remarks = request.POST.get("remarks")

            try:

                Student.objects.create(
                    registration_no=registration_no,
                    name=name,
                    course=course,
                    join_date=join_date,
                    course_fees=course_fees,
                    paid_fees=paid_fees,
                    to_pay=to_pay,
                    certificate=certificate,
                    remarks=remarks
                )

                update_excel_file()

                return render(request, "students/home.html", {
                    "success": "Student saved successfully!"
                })

            except IntegrityError:

                return render(request, "students/home.html", {
                    "error": "Registration number already exists!"
                })

    return render(request, "students/home.html")

# UPDTAE STUDENT DATA

@login_required
def update_student(request):

    student = None
    error = None
    success = None

    if request.method == "POST":

        action = request.POST.get("action")
        registration_no = request.POST.get("registration_no")

        # SEARCH STUDENT
        if action == "search":

            try:
                student = Student.objects.get(
                    registration_no=registration_no
                )

            except Student.DoesNotExist:

                error = "Student not found!"

        # UPDATE STUDENT
        elif action == "update":

            try:

                student = Student.objects.get(
                    registration_no=registration_no
                )

                student.name = request.POST.get("name")
                student.course = request.POST.get("course")
                student.join_date = request.POST.get("join_date")

                student.course_fees = Decimal(
                    request.POST.get("course_fees")
                )

                student.paid_fees = Decimal(
                    request.POST.get("paid_fees")
                )

                # To Pay can be blank
                student.to_pay = request.POST.get("to_pay") or None

                student.certificate = request.POST.get("certificate")
                student.remarks = request.POST.get("remarks")

                student.save()

                update_excel_file()

                success = "Student details updated successfully!"

            except Student.DoesNotExist:

                error = "Student not found!"

            except IntegrityError:

                error = "Unable to update student details!"

    return render(
        request,
        "students/update_student.html",
        {
            "student": student,
            "error": error,
            "success": success
        }
    )

# DELETE STUDENT

@login_required
def delete_student(request):

    if request.method == "POST":

        action = request.POST.get("action")
        registration_no = request.POST.get("registration_no")

        if action == "delete":

            try:

                student = Student.objects.get(
                    registration_no=registration_no
                )

                student.delete()

                update_excel_file()

                return render(
                    request,
                    "students/delete_student.html",
                    {
                        "success": "Student deleted successfully!"
                    }
                )

            except Student.DoesNotExist:

                return render(
                    request,
                    "students/delete_student.html",
                    {
                        "error": "Student not found!"
                    }
                )

    return render(
        request,
        "students/delete_student.html"
    )

# EXPORT REPORT

def update_excel_file():

    students = Student.objects.all()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Students"

    worksheet.append([
        "Registration No",
        "Name",
        "Course",
        "Join Date",
        "Course Fees",
        "Paid Fees",
        "To Pay",
        "Balance",
        "Certificate",
        "Remarks"
    ])

    for student in students:

        worksheet.append([
            student.registration_no,
            student.name,
            student.course,
            student.join_date.strftime("%d-%m-%Y") if student.join_date else "",
            student.course_fees,
            student.paid_fees,
            student.to_pay,
            student.balance,
            student.certificate,
            student.remarks
        ])

    export_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "exports"
    )

    os.makedirs(export_folder, exist_ok=True)

    excel_file = os.path.join(
        export_folder,
        "students.xlsx"
    )

    workbook.save(excel_file)


@login_required
def export_students(request):

    students = Student.objects.all()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Students"

    worksheet.append([
        "Registration No",
        "Name",
        "Course",
        "Join Date",
        "Course Fees",
        "Paid Fees",
        "To Pay",
        "Balance",
        "Certificate",
        "Remarks"
    ])

    for student in students:

        worksheet.append([
            student.registration_no,
            student.name,
            student.course,
            student.join_date.strftime("%d-%m-%Y") if student.join_date else "",
            student.course_fees,
            student.paid_fees,
            student.to_pay,
            student.balance,
            student.certificate,
            student.remarks
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="students.xlsx"'
    )

    workbook.save(response)

    return response