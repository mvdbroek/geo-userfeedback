from django.conf.urls import patterns, include, url

# Enable admin
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.defaults import *
from tastypie.api import Api
from feedbackserver.api import *

v1_api = Api(api_name='v1/feedback')

v1_api.register(ApplicationDomainResource())
v1_api.register(DomainURNResource())
v1_api.register(CI_ContactResource())
v1_api.register(CI_ResponsiblePartyResource())
v1_api.register(TagsResource())
v1_api.register(GVQ_UserRoleCodeResource())
v1_api.register(CI_DateResource())
v1_api.register(CI_CitationResource())
v1_api.register(MD_IdentifierResource())
v1_api.register(GVQ_UserInformationResource())
v1_api.register(GVQ_FeedbackTargetResource())
v1_api.register(CI_OnlineResourceResource())
v1_api.register(GVQ_PublicationResource())
v1_api.register(GVQ_DataFocusResource())
v1_api.register(GVQ_RatingResource())
v1_api.register(GVQ_FeedbackItemResource())
v1_api.register(GVQ_DiscoveredIssueResource())
v1_api.register(GVQ_UsageReportResource())
v1_api.register(CI_Series())



urlpatterns = patterns('',
    url(r'^feedbackserver/', include('feedbackserver.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)

