from django.conf.urls import patterns
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^content-admin/', contentAdmin, name='content-admin'),
    url(r'^my_topic_ajax/', my_topic_ajax, name='my_topic_ajax'),
    url(r'^upload_topics/', upload_topics, name='upload_topics'),
    url(r'download_topics/', download_topic_data, name='download_topic_data'),
    url(r'import-topics/', import_topics_data, name='import_topics_data'),
    url(r'^my_subtopic_ajax/', my_subtopic_ajax, name='my_subtopic_ajax'),
    url(r'^upload_subtopics/', upload_subtopics, name='upload_subtopics'),
    url(r'download_subtopics/', download_subtopic_data, name='download_subtopic_data'),
    url(r'import-subtopics/', import_subtopics_data, name='import_subtopics_data'),
    url(r'content_details/', ContentDetailsView.as_view(), name='content_details'),
    url(r'content_demand/', ContentDemandView.as_view(), name='content_demand'),
    url(r'get_course/', get_course, name='get_course'),
    url(r'^my_table_ajax/', my_table_ajax, name='my_table_ajax'),
    
    url(r'^tttinfo/', tttinfo, name='tttinfo'),
    url(r'^get_time_table/', get_time_table, name='get_time_table'),
    url(r'^manage_tttinfo/', manage_tttinfo, name='manage_tttinfo'),
    url(r'^update_time_table/', update_time_table, name='update_time_table'),
    url(r'^delete_time_table/', delete_time_table, name='delete_time_table'),
    url(r'^tv_timetable_bulk_upload/', tv_timetable_bulk_upload, name='tv_timetable_bulk_upload'),
    url(r'^multi_stat/', multi_stat, name='multi_stat'),
    url(r'^stat_fetch_details/', stat_fetch_details, name='stat_fetch_details'),
    url(r'^stat_summary/', stat_summary, name='stat_summary'),
    url(r'^get_stat_table/', get_stat_table, name='get_stat_table'),
    url(r'^get_session_table/', get_session_table, name='get_session_table'),
    url(r'^get_course_coverage/', get_course_coverage, name='get_course_coverage'),
    url(r'^get_planed_topics_by_grade/', get_planed_topics_by_grade, name='get_planed_topics_by_grade'),
    url(r'^nps_awards/', nps_awards_pdf, name='nps_awards_pdf'),
    url(r'^faq/?$', faq, name="faq"),
    url(r'^nps/?$', nps, name="nps"),
    url(r'^faq/(?P<id>\d+)/$', faq_answer, name="faq_answer"),
    url(r'^roshni/?$', roshni, name="roshni"),
    url(r'^plounge/?$', Plounge.as_view(), name="plounge"),
    url(r'^mobile-plounge/(?P<pk>\d+)/?$', MobilePlounge.as_view(), name="plounge-mobile"),
    url(r'^bulk-upload-digital-school/?$', BulkUploadDigitalSchoolView.as_view(), name="BulkUploadDigitalSchoolView"),
    url(r'^upload_digital_school_doc/?$', UploadDigitalSchoolDoc.as_view(), name="UploadDigitalSchoolDoc"),
    url(r'^content/volunteer/?$', ContentVolunteerView.as_view(), name="ContentVolunteerView"),
    url(r'^content/admin/?$', ContentAdminView.as_view(), name="CenterAdminView"),
    url(r'^get_enroll/(?P<cent_id>\d+)/(?P<off_id>\d+)/?$', ModifyStudentEnroll.as_view(), name='GETStudentEnroll'),
    url(r'^modify_student_enroll/?$', ModifyStudentEnroll.as_view(), name='ModifyStudentEnroll'),
    url(r'^manage_booking/?', ManageBooking.as_view(), name='manage_booking'),

    
]

