from .models import *
from django.shortcuts import render, redirect
from django.http import HttpResponse
# from django.http import JsonResponse
from student.models import Time_Table
import json
from student.utils import StudentLogin, GuardianLogin
from django.contrib import messages
from datetime import datetime, timedelta
import requests
import settings as appSettingObj
import settings
import genutilities.uploadDocumentService as docUploadService
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt




def student_login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        user = Guardian.objects.filter(mobile = mobile)
        if not user:
            messages.error(request, 'No student found!, please reach to your coordinator')
            return redirect('/')
        
        if len(str(mobile)) > 10 or len(str(mobile)) < 10 :
            context = {'message' : 'Invalid mobile number' , 'class' : 'danger' }
            return render(request, 'student_login_page.html', {'contect':context} )
        else:
            otp = str(random.randint(1111,9999))
            time_now = datetime.now()
            expiry_time = time_now + timedelta(minutes = 15)
            UserOtp.objects.create(mobile=mobile,otp=otp,type='guardian',expiry_time=expiry_time)
            send_otp(mobile,otp)
            request.session['mobile'] = mobile
            return redirect('/student/student_verify_otp/')
    return render(request, 'student_login_page.html')

def send_otp(mobile, otp):
    authKey = appSettingObj.SMS_AUTHENTICATION_KEY
    mobileHashCode = appSettingObj.MOBILE_HASH_CODE_LOCAL
    mobile = appSettingObj.MOBILE_PREFIX + str(mobile)
    mobileHashCode = " " +mobileHashCode+". -EVIDYALOKA"
    message = "Your eVidyaLoka login otp is {}. {}".format(otp, mobileHashCode)
    sender = appSettingObj.MOBILE_SENDER_ID
    otpExpiry = 5
    extra_params = {}
    sender = "EVDYLK"
    baseURL = appSettingObj.BASE_URL_MSG91
    url = baseURL + "/api/sendotp.php?authkey={}&mobile={}&message={}&sender={}&otp={}&otp_expiry={}&DLT_TE_ID=1107164075999531088".format(
        authKey, mobile, message, sender, otp, otpExpiry)
    resp = requests.get(url)
    response = resp.json()
    return redirect('/verify_otp')
    
def student_verify_otp(request):
    context = {'message' : 'User not found' , 'class' : 'danger' }
    if 'mobile' in request.session:
        mobile = request.session['mobile']
        if request.method == 'POST':
            otp = request.POST.get('otp')
            if UserOtp.objects.filter(mobile=mobile,otp=otp).exists():
                request.session['guardian'] = Guardian.objects.filter(mobile = mobile)
                return redirect('/student/select_student')
            else:
                messages.error(request, 'Entered OTP is Wrong!')
                return redirect('/student/student_verify_otp')
    else:
        return redirect('/')
    return render(request, 'verify_otp.html', {'mobile':mobile})

@GuardianLogin
def select_student(request):
    guardian = request.session['guardian']
    guardianId = guardian[0].id
    mobile = request.session['mobile']

    student = Student_Guardian_Relation.objects.filter(guardian_id=guardianId)
    studentObj = Student.objects.filter(phone=mobile)
    if request.method == "POST":
        student = request.POST['student_name']
        request.session['student']=student
        return redirect('/student/student_dashboard/')
    return render(request, 'select_student.html',{'student':studentObj})

@GuardianLogin
@StudentLogin
def studentdashboard(request):
    studentId = request.session['student']
    studentobj = Student.objects.get(id=studentId)
    print(studentobj)
    offeringId = Offering_enrolled_students.objects.filter(student_id=studentId).values_list('offering')
    print ("offeringId", offeringId)
    if not offeringId:
        messages.error(request, "Student `{}-{}` was not enrolled or Student don't have offerings".format(studentobj.id,studentobj.name))
        return redirect('/student/select_student')
    else:
        offeringObj = Offering.objects.filter(id__in=offeringId,status='running')
        print('offeringObj',offeringObj)
        if offeringObj:
            offeringObj = Offering.objects.get(id__in=offeringId,status='running')
            courseId=offeringObj.course_id
            courseObj = Course.objects.get(id=courseId)
        else:
            messages.error(request, "Student `{}-{}` was don't have running offerings".format(studentobj.id,studentobj.name))
            return redirect('/student/select_student')
           
    return render(request, 'evd.html', {'student':studentobj,'offerings':offeringObj,'course':courseObj})


@GuardianLogin
@StudentLogin
def student_calendar(request):
    studentId = request.session['student']
    offeringId = Offering_enrolled_students.objects.filter(student_id=studentId).values_list('offering')
    offeringObj = Offering.objects.get(id__in=offeringId, status='running')
    courseId=offeringObj.course_id
    courseObj = Course.objects.get(id=courseId)
    start = request.GET.get('start')
    end   = request.GET.get('end')
    std_sessions = Session.objects.filter(date_start__gte=start,date_start__lte=end,offering_id__in=offeringId).values_list('id','date_start','date_end','ts_link','teacher')
    # sessions = Session.objects.filter(offering_id__in=offeringId)
    out = []
    for tm in std_sessions:
        e_id=tm[0]
        start_date=tm[1].strftime("%Y-%m-%d %H:%M:%S")
        end_date=tm[2].strftime("%Y-%m-%d %H:%M:%S")
        link = tm[3]
        teacher = tm[4]
        out.append({   
            'id':e_id,
            'title': '{}th {} Click here to join class'.format(courseObj.grade,courseObj.subject),
            'start': start_date,
            'end': end_date,
            'link': link,
            'tm_type':'live'                                
        })

    return HttpResponse(json.dumps(out),content_type="application/json")

@GuardianLogin
@StudentLogin
def student_ask_doubt(request):
    studentId = request.session['student']
    student = Student.objects.get(id=studentId)

    offeringId = Offering_enrolled_students.objects.filter(student_id=studentId).values_list('offering')
    offeringObj = Offering.objects.get(id__in=offeringId, status='running')
    courseId=offeringObj.course_id
    topics = Topic.objects.filter(course_id = courseId).exclude( status = 'Inactive').order_by('priority')#.exclude(id__in = complted_session_topic_id)

    if request.method == 'POST':
        studentid = request.POST.get('studentid')
        offeringid = request.POST.get('offeringid')

        topic = request.POST.get('topics')
        subtopic=request.POST.get('subtopics')
        text = request.POST.get('text')
        urlString = request.POST.get('url')
        attachmentType = request.POST.get('attachmentType')

        studentObj = Student.objects.get(id=studentId)
        offeringId = Offering_enrolled_students.objects.filter(student_id=studentId).values_list('offering')
        offeringObj = Offering.objects.get(id__in=offeringId, status='running')

        dtDoc = None; resourceType = '2'; resourceUrl = ''; contentTypeId = 2
        
        if attachmentType == "image":
            cloudFolderName = settings.TEACHER_DOUBT_RESPONSE_STORAGE_FOLDER
            dtDoc = docUploadService.upload_user_document_s3(request, "teacher", None, cloudFolderName,None,"obj")
            resourceUrl = dtDoc.url

        elif urlString and len(urlString) > 10:
            resourceType = '5'
            resourceUrl = urlString
            contentTypeId = 4
            
        Doubt_Thread.objects.create(
            student=studentObj,
            offering=offeringObj,
            topic_id=topic,
            subtopic_id=subtopic,
            text=text,
            resource_type=resourceType,
            resource_url = resourceUrl,
            resource_doc = dtDoc,
            content_type_id=contentTypeId,
            created_by_id = settings.SYSTEM_USER_ID_AUTH,
            updated_by_id = settings.SYSTEM_USER_ID_AUTH,
        )

        # messages.success(request, 'Posting Doubt...')
        return redirect('/student/student_dashboard/')

    return render(request, 'student_askdoubt.html',{'topics':topics, 'student':student})

@GuardianLogin
@StudentLogin
def load_subtopics(request):
    topic_id = request.GET.get('topic_id')

    subtopics = SubTopics.objects.filter(topic_id=topic_id)
    subtopic_list = [{'id': subtopic.id, 'name': subtopic.name} for subtopic in subtopics]
    response_data = {'subtopics': subtopic_list}

    return HttpResponse(json.dumps(response_data), content_type='application/json')

@GuardianLogin
@StudentLogin
def list_studentdoubts(request):
    studentId = request.session['student']
    student = Student.objects.get(id=studentId)
    doubtObj = Doubt_Thread.objects.filter(student=student).order_by('id')
    
    offeringId = Offering_enrolled_students.objects.filter(student_id=studentId).values_list('offering')
    offeringObj = Offering.objects.get(id__in=offeringId, status='running')
    courseId=offeringObj.course_id
    courseObj = Course.objects.get(id=courseId)

    return render(request, 'doubt_list.html', {'doubtList':doubtObj,'student':student,'course':courseObj})


@csrf_exempt
def getSessionId(request):

    if request.method == 'POST':
        sessionId = request.POST.get('id')
        request.session['sessionId']=sessionId

        sessionObj = Session.objects.get(id=sessionId)
        print('get',sessionObj.teacher.first_name)

    else:
        return HttpResponse('else statemant')
    return HttpResponse('sessionId',sessionObj)

@GuardianLogin
@StudentLogin
def update_liveclass_attendance(request):
    studentId = request.session['student']
    studentObj = Student.objects.get(id=studentId)
    sessionId = request.session['sessionId']

    try:
        try:
            sessionObj = Session.objects.get(id=sessionId)
            print(sessionObj)
        except:
            return HttpResponse("No class today")

        sessAttendance = None
        sessObjts = SessionAttendance.objects.filter(session=sessionObj, student=studentObj)
        if sessObjts and len(sessObjts) > 0:
            sessAttendance = sessObjts[0]


        if sessAttendance and (sessAttendance.is_present is None or sessAttendance.is_present != "yes"):
            sessAttendance.is_present = "yes"
            sessAttendance.save()
        else:
            if sessAttendance is None:
                sessAttendance = SessionAttendance.objects.create(
                    student = studentObj,
                    session = sessionObj,
                    is_present = "yes"
                )
                sessAttendance.save()

        dataObj = {
            "message":"Attendance updated successfully"
        }
        return redirect(sessionObj.ts_link)
    except Exception as e:
        print("update_liveclass_attendance",e)


def student_logout(request):
    del request.session['student']
    return redirect('/')