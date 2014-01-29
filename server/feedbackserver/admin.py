
#from feedbackserver.models import GVQ_FeedbackItem, GVQ_FeedbackTarget, Tags, GVQ_UserRoleCode, GVQ_UserInformation, GVQ_ScopeCode
#from feedbackserver.models import ApplicationDomain, MD_Identifier, CI_ResponsibleParty, GVQ_Rating, GVQ_FeedbackCollection

from feedbackserver.models import *
from django.contrib import admin

admin.site.register(CI_ResponsibleParty)
admin.site.register(Tags)
admin.site.register(GVQ_UserRoleCode)
admin.site.register(CI_Date)
admin.site.register(CI_Citation)
admin.site.register(CI_Contact)
admin.site.register(MD_Identifier)
admin.site.register(GVQ_UserInformation)
#admin.site.register(GVQ_ScopeCode)
admin.site.register(GVQ_FeedbackTarget)
admin.site.register(GVQ_DataFocus)
#admin.site.register(GVQ_UserComment)
admin.site.register(GVQ_Rating)
admin.site.register(GVQ_FeedbackItem)
admin.site.register(ApplicationDomain)
admin.site.register(DomainURN)

admin.site.register(GVQ_UsageReport)
#admin.site.register(DQ_DataQuality)

admin.site.register(CI_OnlineResource)
admin.site.register(CI_Series)
admin.site.register(GVQ_Publication)
#admin.site.register(GVQ_PublicationPurposeCode)
#admin.site.register(GVQ_PublicationCategoryCode)
#admin.site.register(GVQ_ReportAspectCode)
admin.site.register(GVQ_DiscoveredIssue)

