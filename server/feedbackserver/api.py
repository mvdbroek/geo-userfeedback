# myapp/api.py
from django.conf.urls.defaults import *
from django.db import transaction
from tastypie.paginator import Paginator
from tastypie.bundle import Bundle
from django.db.models import Avg, Count
from tastypie.utils import trailing_slash
#Wrapper for tastypie fields
import complexFields as fields
from complexResources import ComplexModelResource
from django.forms.models import modelform_factory
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import  BadRequest
import feedbackserver.models as feedbackmodel
from customSerializer import CustomXMLSerializer
from feedbackValidation import ModelFormValidation
import operator
import logging
import uuid
from django.db.models import Q
from configuration import  getModelNameValueSearchDictionary, getqSearchItems
from configuration import getAllowedParameters, getModelFieldSearchDictionary, getServerCodeSpace
from configuration import construct_field_filter_list, construct_value_filter_list, construct_search_list
from configuration import getTargetqSearchItems, getTargetModelFieldSearchDictionary, getTargetModelNameValueSearchDictionary, getAllowedTargetParameters, getAllowedCollectionParameters

logger = logging.getLogger(__name__)

def hydrateManyToMany(bundle, element):
    if element in bundle.data and (type(bundle.data[element])) != None and (type(bundle.data[element]) != list):
        bundle.data[element] = [bundle.data[element]]
    return bundle

def hydrateManyToManyWithSubElement(bundle, element, subElement):
    if not element in bundle.data or (type(bundle.data[element])) == None: return bundle
    if (type(bundle.data[element]) != list):
        bundle.data[element] = [bundle.data[element]]
    if not bundle.data[element]: return bundle
    if not isinstance(bundle.data[element][0], Bundle) and subElement in bundle.data[element][0]:
        i = 0
        for item in bundle.data[element]:
            if subElement in item:
                bundle.data[element][i] = item[subElement]
            i = i + 1
    return bundle

def hydrateWithSubElement(bundle, element, subElement):
    if element in bundle.data and (type(bundle.data[element]) == dict):
        bundle.data[element] = bundle.data[element][subElement]
    return bundle

def dehydrateWithSubElement(bundle, element, subElement):
    if element in bundle.data and bundle.data[element]:
        bundle.data[element] = {subElement : bundle.data[element]}
    return bundle

def dehydrateManyToManyWithSubElement(bundle, element, subElement):
    if element in bundle.data:
        itemList = bundle.data[element]
        bundle.data[element] = []
        for item in itemList:
            bundle.data[element].append({subElement : item})
    return bundle

class PostAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        return super(PostAuthentication, self).is_authenticated(request, **kwargs)


BRIEF = 0
SUMMARY = 1
FULL = 2

class ApplicationDomainResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.ApplicationDomain.objects.all()
        resource_name = 'applicationdomain'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.ApplicationDomain))

class DomainURNResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.DomainURN.objects.all()
        resource_name = 'domainurn'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.DomainURN))

class CI_ContactResource(ComplexModelResource):
    onlineResource = fields.ManyToManyField('feedbackserver.api.CI_OnlineResourceResource', 'onlineResource',  full = True, null = True, blank = True)
    class Meta:
        queryset = feedbackmodel.CI_Contact.objects.all()
        resource_name = 'contactresource'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CI_Contact))

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'hoursOfService', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'contactInstructions', 'CharacterString')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'onlineResource', 'CI_OnlineResource')
        return bundle

    def hydrate_hoursOfService(self, bundle):
        return hydrateWithSubElement(bundle, 'hoursOfService', 'CharacterString')

    def hydrate_contactInstructions(self, bundle):
        return hydrateWithSubElement(bundle, 'contactInstructions', 'CharacterString')

    def hydrate_onlineResource(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'onlineResource', 'CI_OnlineResource')

class CI_ResponsiblePartyResource(ComplexModelResource):
    contactInfo = fields.ManyToManyField(CI_ContactResource, 'contactInfo', full = True, null=True, blank=True)
    class Meta:
        queryset = feedbackmodel.CI_ResponsibleParty.objects.all()
        resource_name = 'responsibleparty'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CI_ResponsibleParty, exclude=('role')))

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'individualName', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'organisationName', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'positionName', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'role', 'CI_RoleCode')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'contactInfo', 'CI_Contact')
        return bundle

    def hydrate(self, bundle):
        bundle = hydrateWithSubElement(bundle, 'individualName', 'CharacterString')
        bundle = hydrateWithSubElement(bundle, 'organisationName', 'CharacterString')
        bundle = hydrateWithSubElement(bundle, 'positionName', 'CharacterString')
        bundle = hydrateWithSubElement(bundle, 'role', 'CI_RoleCode')
        bundle = hydrateManyToManyWithSubElement(bundle, 'contactInfo', 'CI_Contact')
        return bundle

class TagsResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.Tags.objects.all()
        resource_name = 'tags'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.Tags))

class GVQ_UserRoleCodeResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.GVQ_UserRoleCode.objects.all()
        resource_name = 'userRole'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_UserRoleCode))

class CI_DateResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.CI_Date.objects.all()
        resource_name = 'ci_date'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CI_Date))

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'dateType', 'CI_DateTypeCode')
        bundle = dehydrateWithSubElement(bundle, 'date', 'Date')
        return bundle

    def hydrate_date(self, bundle):
        return hydrateWithSubElement(bundle, 'date', 'Date')

    def hydrate_dateType(self, bundle):
        return hydrateWithSubElement(bundle, 'dateType', 'CI_DateTypeCode')

class CI_Series(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.CI_Series.objects.all()
        resource_name = 'ci_series'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CI_Series))

    def hydrate_name(self, bundle):
        return hydrateWithSubElement(bundle, 'name', 'CharacterString')

    def hydrate_issueIdentification(self, bundle):
        return hydrateWithSubElement(bundle, 'issueIdentification', 'CharacterString')

    def hydrate_page(self, bundle):
        return hydrateWithSubElement(bundle, 'page', 'CharacterString')

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'page', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'issueIdentification', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'name', 'CharacterString')
        return bundle


class CI_CitationResource(ComplexModelResource):
    alternateTitle = fields.ToManyField('feedbackserver.api.CharacterStringResource', 'characterstring_set', related_name= 'alternateTitle', null = True, full = True)
    identifier =  fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'identifier', full = True, null = True, blank = True)
    date = fields.ManyToManyField('feedbackserver.api.CI_DateResource', 'date', full = True)
    citedResponsibleParty = fields.ManyToManyField('feedbackserver.api.CI_ResponsiblePartyResource', 'citedResponsibleParty', full = True, null = True, blank = True)
    series = fields.ManyToManyField(CI_Series, 'series', full = True, null = True, blank = True)

    class Meta:
        queryset = feedbackmodel.CI_Citation.objects.all()
        resource_name = 'ci_citation'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CI_Citation))

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'otherCitationDetails', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'collectiveTitle', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'ISBN', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'ISSN', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'title', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'editionDate', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'presentationForm', 'CI_PresentationFormCode')

        bundle = dehydrateManyToManyWithSubElement(bundle, 'identifier', 'MD_Identifier')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'date', 'CI_Date')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'citedResponsibleParty', 'CI_ResponsibleParty')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'series', 'CI_Series')

        return bundle

    def hydrate_otherCitationDetails(self, bundle):
        return hydrateWithSubElement(bundle, 'otherCitationDetails', 'CharacterString')

    def hydrate_collectiveTitle(self, bundle):
        return hydrateWithSubElement(bundle, 'collectiveTitle', 'CharacterString')

    def hydrate_ISBN(self, bundle):
        return hydrateWithSubElement(bundle, 'ISBN', 'CharacterString')

    def hydrate_ISSN(self, bundle):
        return hydrateWithSubElement(bundle, 'ISSN', 'CharacterString')

    def hydrate_title(self, bundle):
        return hydrateWithSubElement(bundle, 'title', 'CharacterString')

    def hydrate_edition(self, bundle):
        return hydrateWithSubElement(bundle, 'edition', 'CharacterString')

    def hydrate_editionDate(self, bundle):
        return hydrateWithSubElement(bundle, 'editionDate', 'Date')

    def hydrate_presentationForm(self, bundle):
        return hydrateWithSubElement(bundle, 'presentationForm', 'CI_PresentationFormCode')

    def hydrate_date(self, bundle):
        bundle = hydrateManyToManyWithSubElement(bundle, 'date', 'CI_Date')
        return bundle

    def hydrate_identifier(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'identifier', 'MD_Identifier')

    def hydrate_citedResponsibleParty(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'citedResponsibleParty', 'CI_ResponsibleParty')

    def hydrate_series(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'series', 'CI_Series')


class MD_IdentifierResource(ComplexModelResource):
    authority = fields.ToOneField(CI_CitationResource, 'authority', null = True, blank = True, full=True)
    class Meta:
        queryset = feedbackmodel.MD_Identifier.objects.all()
        resource_name = 'md_identifier'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.MD_Identifier))

    def hydrate_code(self, bundle):
        return hydrateWithSubElement(bundle, 'code', 'CharacterString')

    def hydrate_codeSpace(self, bundle):
        return hydrateWithSubElement(bundle, 'codeSpace', 'CharacterString')

    def hydrate_version(self, bundle):
        return hydrateWithSubElement(bundle, 'version', 'CharacterString')

    def hydrate_authority(self, bundle):
        return hydrateWithSubElement(bundle, 'authority', 'CI_Citation')

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'codeSpace', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'code', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'version', 'CharacterString')
        return bundle

    def override_urls(self):
        return [url(r"^primary_target_ids%s$" % (trailing_slash()),
                self.wrap_view('get_datasets'),name="api_get_datasets"),
                url(r"^primary_target_ids%ssearch$" % (trailing_slash()),
                self.wrap_view('get_datasets'),name="api_get_datasets"),
               ]

    def get_datasets(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.is_authorized(request)
        self.throttle_check(request)

        self._check_request(request)
        sqs = feedbackmodel.MD_Identifier.objects.all().exclude(resourceRef__primaryTarget = None).annotate(avg_items = Avg('resourceRef__primaryTarget__gvq_rating__score')).annotate(count_items = Count('resourceRef__primaryTarget__subject'))

        ##Check the average rating.
        averageRating = request.GET.get('minimum_average_rating', '')
        if averageRating != '':
            try:
                average = float(averageRating)
            except ValueError as error:
                raise BadRequest("Average rating '"+averageRating+"' is not a valid float.")


        #Check the total count.
        total = request.GET.get('minimum_total_count', '')
        if total != '':
            try:
                totalCount = int(total)
            except ValueError as error:
                raise BadRequest("Minimum total count '"+totalCount+"' is not an integer.")


        #Filter on fields.
        fieldDictionary = getTargetModelFieldSearchDictionary()

        fieldList = construct_field_filter_list(request, 'fields', fieldDictionary)
        if len(fieldList) != 0 :
            sqs = sqs.filter( reduce(operator.or_, fieldList ) ).distinct()
            #Cannot search for in more than 5-6 tables in one go. Force database request.
            len(sqs)

        #Name value dictionary supported.
        urlDatabaseNamedictionary = getTargetModelNameValueSearchDictionary()


        ##Filter on special values.
        #Probably not necessary to execute the filterset already.
        for urlKey in urlDatabaseNamedictionary:
            resultList = construct_value_filter_list(request, urlKey, urlDatabaseNamedictionary[urlKey])
            if len(resultList) != 0 :
                sqs = sqs.filter(reduce(operator.or_,  resultList) ).distinct()


        #Handle the text search.
        searchItems = getTargetqSearchItems()
        searchList = request.GET.get('q', '').split()
        if searchList != '':
            first_search = True
            #'And' all the searches for q.
            for searchValue in searchList:
                #Execute after the first search.
                if first_search:
                    first_search = False
                else: len(sqs)
                sqs = sqs.filter( reduce(operator.or_, construct_search_list(searchItems, searchValue))).distinct()


        ##Check the average rating.
        averageRating = request.GET.get('minimum_average_rating', '')
        if averageRating != '':
            try:
                average = float(averageRating)
            except ValueError as error:
                raise BadRequest("Average rating '"+averageRating+"' is not a valid float.")
            sqs.filter(avg_items__gte = average)


        #Check the total count.
        total = request.GET.get('minimum_total_count', '')
        if total != '':
            try:
                totalCount = int(total)
            except ValueError as error:
                raise BadRequest("Minimum total count '"+totalCount+"' is not an integer."+error)
            sqs.filter(count_items__gte = totalCount)

        #Use the Tastypie paginator.
        paginator = Paginator(request.GET, sqs)
        try:
            to_be_serialized = paginator.page()
        except ValueError:
            raise BadRequest("Sorry, no results on that page.")

        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['objects']]
        meta_info = to_be_serialized['meta']
        #to_be_serialized['objects'] = []
        to_be_serialized = []


        for bundle in bundles:
            self.full_dehydrate(bundle)
            to_be_serialized.append(bundle)

        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

        #Append extra information the format to create a collection.

        object_list = { 'MD_identifierList': to_be_serialized,  'meta': meta_info}

        return self.create_response(request, object_list)


    def _check_request(self, request):

        #Check the return and what to raise...
        allowed_parameters = getAllowedTargetParameters()

        user_parameters = request.GET
        for parameter in user_parameters.keys():
            if not parameter in allowed_parameters.keys():
                raise BadRequest("Parameter '"+parameter+"' of the request is unknown")
            """ If list user input is possible and the allowed values are also specified, check all the values.
            Note: there is no boolean case currently(one allowed parameter value).
            Parameter q, the only '+' separated list does not have list values. Therefore splitting is always done
            on ','"""
            if isinstance(allowed_parameters[parameter], list):
                userValues = user_parameters[parameter].split(",")
                for userValue in userValues:
                    if not userValue.lower() in [par.lower() for par in allowed_parameters[parameter]]:
                        raise BadRequest("Value for parameter "+parameter+" '"+userValue+
                                    "' is unknown. Options are: "+", ".join(allowed_parameters[parameter]))

class GVQ_UserInformationResource(ComplexModelResource):
    applicationDomain = fields.ManyToManyField('feedbackserver.api.ApplicationDomainResource', 'applicationDomain', full=True, null = True, blank = True)
    userRole = fields.ManyToManyField('feedbackserver.api.GVQ_UserRoleCodeResource', 'userRole', full = True)
    userDetails = fields.ToOneField(CI_ResponsiblePartyResource, 'userDetails', full = True)
    externalUserID = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'externalUserID', full = True, null = True, blank = True)
    class Meta:
        queryset = feedbackmodel.GVQ_UserInformation.objects.all()
        resource_name = 'userinformation'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_UserInformation, exclude=('applicationDomain')))

    def hydrate(self, bundle):
        if 'applicationDomain' in bundle.data:
            domainList = bundle.data['applicationDomain']
            if (isinstance(bundle.data['applicationDomain'], basestring)):
                bundle.data['applicationDomain'] = []
                bundle.data['applicationDomain'].append({'applicationDomain' : domainList})
                return bundle
            if (type(bundle.data['applicationDomain']) == list) and len(bundle.data['applicationDomain']) !=0 and isinstance(bundle.data['applicationDomain'][0], Bundle): return bundle
            bundle.data['applicationDomain'] = []
            for domain in domainList:
                bundle.data['applicationDomain'].append({'applicationDomain' : domain})
        if 'externalUserId' in bundle.data and (type(bundle.data['externalUserId']) == dict):
            bundle.data['externalUserID'] =  bundle.data['externalUserId']['MD_Identifier']
            del bundle.data['externalUserId']
        return bundle

    def hydrate_userRole(self, bundle):
        return hydrateManyToMany(bundle, 'userRole')

    def dehydrate(self, bundle):
        if 'applicationDomain' in bundle.data:
            appList = []
            for app in bundle.data['applicationDomain']:
                if isinstance(app, Bundle):
                    if 'applicationDomain' in app.data:
                        appList.append(app.data['applicationDomain'])
            bundle.data['applicationDomain'] = appList
        if 'externalUserID' in bundle.data and bundle.data['externalUserID']:
            bundle.data['externalUserId'] = {'MD_Identifier' : bundle.data['externalUserID']}
            del bundle.data['externalUserID']
        return bundle

class GVQ_FeedbackTargetResource(ComplexModelResource):
    resourceRef = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'resourceRef', full=True)
    dataFocus = fields.ManyToManyField('feedbackserver.api.GVQ_DataFocusResource', 'dataFocus', null = True, blank= True, full = True)
    class Meta:
        queryset = feedbackmodel.GVQ_FeedbackTarget.objects.all()
        resource_name = 'gvq_feedbacktarget'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_FeedbackTarget))

    def hydrate_natureOfTarget(self, bundle):
        return hydrateWithSubElement(bundle, 'natureOfTarget', 'MD_ScopeCode')

    def hydrate_resourceRef(self, bundle):
        bundle = hydrateManyToManyWithSubElement(bundle, 'resourceRef', 'MD_Identifier')
        return bundle

    def hydrate_dataFocus(self, bundle):
        return hydrateManyToMany(bundle, 'dataFocus')

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'natureOfTarget', 'MD_ScopeCode')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'resourceRef', 'MD_Identifier')
        return bundle

class GVQ_DataFocusResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.GVQ_DataFocus.objects.all()
        resource_name = 'gvq_datafocus'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_DataFocus))

class CI_OnlineResourceResource(ComplexModelResource):
    class Meta:
        queryset = feedbackmodel.CI_OnlineResource.objects.all()
        resource_name = 'ci_onlineresource'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CI_OnlineResource))

    def hydrate_linkage(self, bundle):
        return hydrateWithSubElement(bundle, 'linkage', 'URL')

    def hydrate_protocol(self, bundle):
        return hydrateWithSubElement(bundle, 'protocol', 'CharacterString')

    def hydrate_name(self, bundle):
        return hydrateWithSubElement(bundle, 'name', 'CharacterString')

    def hydrate_applicationProfile(self, bundle):
        return hydrateWithSubElement(bundle, 'applicationProfile', 'CharacterString')

    def hydrate_function(self, bundle):
        return hydrateWithSubElement(bundle, 'function', 'CI_OnLineFunctionCode')

    def hydrate_description(self, bundle):
        return hydrateWithSubElement(bundle, 'description', 'CharacterString')

    def dehydrate(self, bundle):
        #Corrects or creates the tag.
        bundle = dehydrateWithSubElement(bundle, 'linkage', 'URL')
        bundle = dehydrateWithSubElement(bundle, 'protocol', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'name', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'applicationProfile', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'function', 'CI_OnLineFunctionCode')
        bundle = dehydrateWithSubElement(bundle, 'description', 'CharacterString')

        return bundle

class GVQ_PublicationResource(CI_CitationResource):
    relatedResource = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'relatedResource', full = True, null=True)
    onlineResource = fields.ManyToManyField('feedbackserver.api.CI_OnlineResourceResource',  'onlineResource', full = True, null=True)
    target = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'target', related_name = 'pub_target', full=True)

    class Meta:
        queryset = feedbackmodel.GVQ_Publication.objects.all()
        resource_name = 'gvq_publication'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_Publication))

    def hydrate_DOI(self, bundle):
        return hydrateWithSubElement(bundle, 'DOI', 'CharacterString')


    def hydrate_volume(self, bundle):
        return hydrateWithSubElement(bundle, 'volume', 'Integer')

    def hydrate_issue(self, bundle):
        return hydrateWithSubElement(bundle, 'issue', 'CharacterString')

    def hydrate_pages(self, bundle):
        return hydrateWithSubElement(bundle, 'pages', 'CharacterString')

    def hydrate_purpose(self, bundle):
        return hydrateWithSubElement(bundle, 'purpose', 'GVQ_PublicationPurposeCode')

    def hydrate_category(self, bundle):
        return hydrateWithSubElement(bundle, 'category', 'GVQ_PublicationCategoryCode')

    def hydrate_target(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'target', 'MD_Identifier')

    def hydrate_relatedResource(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'relatedResource', 'MD_Identifier')

    def hydrate_onlineResource(self, bundle):
        bundle = hydrateManyToManyWithSubElement(bundle, 'onlineResource', 'CI_OnlineResource')
        return bundle

    def hydrate(self, bundle):
        CI_CitationResource.hydrate_ISSN(self, bundle)
        CI_CitationResource.hydrate_ISBN(self, bundle)
        CI_CitationResource.hydrate_title(self, bundle)
        CI_CitationResource.hydrate_collectiveTitle(self, bundle)
        CI_CitationResource.hydrate_otherCitationDetails(self, bundle)
        CI_CitationResource.hydrate_presentationForm(self, bundle)
        CI_CitationResource.hydrate_date(self, bundle)
        CI_CitationResource.hydrate_edition(self, bundle)
        CI_CitationResource.hydrate_editionDate(self, bundle)
        CI_CitationResource.hydrate_identifier(self, bundle)
        CI_CitationResource.hydrate_citedResponsibleParty(self, bundle)
        CI_CitationResource.hydrate_series(self, bundle)
        return bundle

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'DOI', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'volume', 'Integer')
        bundle = dehydrateWithSubElement(bundle, 'issue', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'pages', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'category', 'GVQ_PublicationCategoryCode')
        bundle = dehydrateWithSubElement(bundle, 'purpose', 'GVQ_PublicationPurposeCode')
        bundle = dehydrateWithSubElement(bundle, 'target', 'MD_Identifier')

        bundle = dehydrateManyToManyWithSubElement(bundle, 'onlineResource', 'CI_OnlineResource')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'relatedResource', 'MD_Identifier')

        CI_CitationResource.dehydrate(self, bundle)
        return bundle

class GVQ_DiscoveredIssueResource(ComplexModelResource):
    target = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'target', full = True)
    referenceDoc = fields.ManyToManyField('feedbackserver.api.GVQ_PublicationResource', 'referenceDoc', null = True, full = True)
    fixedResource = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'fixedResource', null = True, full = True)
    expectedFix = fields.ToOneField(CI_DateResource, 'expectedFix', null = True, blank = True, full = True)

    class Meta:
        queryset = feedbackmodel.GVQ_DiscoveredIssue.objects.all()
        resource_name = 'gvq_discoveredissue'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_DiscoveredIssue))

    def hydrate_knownProblem(self, bundle):
        return hydrateWithSubElement(bundle, 'knownProblem', 'CharacterString')


    def hydrate_workAround(self, bundle):
        return hydrateWithSubElement(bundle, 'workAround', 'CharacterString')


    def hydrate_target(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'target', 'MD_Identifier')

    def hydrate_referenceDoc(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'referenceDoc', 'GVQ_Publication')

    def hydrate_fixedResource(self, bundle):
        return hydrateManyToManyWithSubElement(bundle, 'fixedResource', 'MD_Identifier')

    def hydrate_expectedFix(self, bundle):
        return hydrateWithSubElement(bundle, 'expectedFix', 'CI_Date')


    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'knownProblem', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'workAround', 'CharacterString')
        bundle = dehydrateWithSubElement(bundle, 'target', 'MD_Identifier')
        bundle = dehydrateWithSubElement(bundle, 'expectedFix', 'CI_Date')

        bundle = dehydrateManyToManyWithSubElement(bundle, 'referenceDoc', 'GVQ_Publication')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'fixedResource', 'MD_Identifier')
        return bundle


    def obj_update(self, bundle, **kwargs):
        bundle = self.full_hydrate(bundle)
        # Save FKs just in case.
        self.save_related(bundle)
        # Save the main object.
        bundle.obj.save()
        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle


class GVQ_UsageReportResource(ComplexModelResource):
    discoveredIssue = fields.ManyToManyField('feedbackserver.api.GVQ_DiscoveredIssueResource', 'discoveredIssue', null = True, full = True)

    class Meta:
        queryset = feedbackmodel.GVQ_UsageReport.objects.all()
        resource_name = 'gvq_usagereport'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_UsageReport))

    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'reportAspect', 'GVQ_ReportAspectCode')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'discoveredIssue', 'GVQ_DiscoveredIssue')
        return bundle


    def hydrate_reportAspect(self, bundle):
        if 'reportAspect' in bundle.data and type(bundle.data['reportAspect']) == dict:
            bundle.data['reportAspect'] = bundle.data['reportAspect']['GVQ_ReportAspectCode']
        return bundle

    def hydrate_discoveredIssue(self, bundle):
        bundle = hydrateManyToManyWithSubElement(bundle, 'discoveredIssue', 'GVQ_DiscoveredIssue')
        return bundle

    def obj_update(self, bundle, **kwargs):

        bundle = self.full_hydrate(bundle)
        # Save FKs just in case.
        self.save_related(bundle)
        # Save the main object.
        bundle.obj.save()
        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

class GVQ_FeedbackItemResource(ComplexModelResource):
    identifier = fields.ToOneField(MD_IdentifierResource, 'identifier', full= True)
    primaryTarget = fields.ManyToManyField('feedbackserver.api.GVQ_FeedbackTargetResource', 'primaryTarget', full=True)
    secondaryTarget = fields.ManyToManyField('feedbackserver.api.GVQ_FeedbackTargetResource', 'secondaryTarget', null=True, full=True)
    supplementaryTarget = fields.ManyToManyField('feedbackserver.api.GVQ_FeedbackTargetResource', 'supplementaryTarget', null=True, full=True)
    tags = fields.ManyToManyField('feedbackserver.api.TagsResource', 'tags', null = True, full=True)
    user = fields.ToOneField(GVQ_UserInformationResource, 'user', full=True)
    userRole = fields.ToOneField(GVQ_UserRoleCodeResource, 'userRole', full=True)
    domainURN = fields.ManyToManyField('feedbackserver.api.DomainURNResource', 'domainURN', null = True, full=True)
    rating = fields.ToManyField('feedbackserver.api.GVQ_RatingResource', 'gvq_rating_set', related_name = 'item', null = True, blank = True, full = True)
    externalFeedback = fields.ManyToManyField('feedbackserver.api.CI_OnlineResourceResource', 'externalFeedback', null = True, full = True)
    reply_to = fields.ManyToManyField('feedbackserver.api.MD_IdentifierResource', 'reply_to', null=True, full = True)
    usage = fields.ManyToManyField('feedbackserver.api.GVQ_UsageReportResource', 'usage', null = True, full = True)
    citation = fields.ManyToManyField('feedbackserver.api.GVQ_PublicationResource', 'citation', null = True, full = True)

    class Meta:
        queryset = feedbackmodel.GVQ_FeedbackItem.objects.all()
        resource_name = 'items'
        excludes = ['id']
        include_resource_uri = False
        serializer = CustomXMLSerializer()
        authentication = PostAuthentication()
        authorization = DjangoAuthorization()
        #The dateStamp is left out, because tastypie checks too early (before hydration) exclude the dateStamp and identifier.
        #Exclude the tags and domainURN because they have a special hydration.
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_FeedbackItem, exclude=('dateStamp', 'tags', 'identifier', 'domainURN')))

    # Storage of a new item.
    @transaction.commit_on_success
    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        # Add the identifier (or overwrite!!)
        # codespace = server name - parse from request.
        # code = URI.
        bundle.obj = self._meta.object_class()
        bundle.data['identifier'] =  {u'MD_Identifier':
          {u'code': {u'CharacterString': str(uuid.uuid4())},
          u'codeSpace': {u'CharacterString': getServerCodeSpace()}}}
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)

        self.is_valid(bundle, request)
        # Save the main object.
        bundle.obj.save()
        # M2M bundle.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)

        logger.info("New item has been saved.")
        return bundle

    def hydrate_identifier(self, bundle):
        return hydrateWithSubElement(bundle, 'identifier', 'MD_Identifier')

    def hydrate_reply_to(self, bundle):
        bundle = hydrateManyToManyWithSubElement(bundle, 'reply-to', 'MD_Identifier')
        if 'reply-to' in bundle.data:
            bundle.data['reply_to'] = bundle.data['reply-to']
            del bundle.data['reply-to']
        return bundle

    def hydrate_dateStamp(self, bundle):
        if 'dateStamp' in bundle.data and type(bundle.data['dateStamp']) == dict:
            bundle.data['dateStamp'] = bundle.data['dateStamp']['DateTime'].replace(" ","T")
        return bundle

    def hydrate_userComment(self, bundle):
        return hydrateWithSubElement(bundle, 'userComment', 'comment')


    def hydrate_tags(self, bundle):
        if 'tags' in bundle.data:
            if (type(bundle.data['tags'])) != None and (type(bundle.data['tags']) != list):
                if "/" in bundle.data['tags']: return bundle
                tagList = bundle.data['tags'].split(",")
                bundle.data['tags'] = list()
                for tags in tagList:
                    bundle.data['tags'].append({'tags': tags})
        return bundle

    def hydrate_rating(self, bundle):
        if 'rating' in bundle.data and (type(bundle.data['rating'])) != None and (type(bundle.data['rating']) != list):
            bundle.data['rating'] = [bundle.data['rating']]
        return bundle

    def hydrate_domainURN(self, bundle):
        if 'domainURN' in bundle.data:
            domainList = bundle.data['domainURN']
            if (isinstance(bundle.data['domainURN'], basestring)):
                bundle.data['domainURN'] = []
                bundle.data['domainURN'].append({'domainURN' : domainList})
                return bundle
            if (type(bundle.data['domainURN']) == list) and len(bundle.data['domainURN']) !=0 and isinstance(bundle.data['domainURN'][0], Bundle): return bundle
            bundle.data['domainURN'] = []
            for domain in domainList:
                bundle.data['domainURN'].append({'domainURN' : domain})
        return bundle

    def hydrate(self, bundle):
        #Hydrate all manytomany elements
        manytomanyList = ['primaryTarget', 'usage', 'secondaryTarget', 'supplementaryTarget']
        for element in manytomanyList:
            bundle = hydrateManyToMany(bundle, element)
        bundle = hydrateManyToManyWithSubElement(bundle, 'externalFeedback', 'CI_OnlineResource')

        return bundle


    def dehydrate(self, bundle):
        bundle = dehydrateWithSubElement(bundle, 'identifier', 'MD_Identifier')
        bundle = dehydrateWithSubElement(bundle, 'dateStamp', 'DateTime')


        if 'userComment' in bundle.data and bundle.data['userComment']:
            bundle.data['userComment'] = {'comment': bundle.data['userComment'], 'mime-type':  'plain/text'}
        if 'rating' in bundle.data and (len(bundle.data['rating']) != 0):
            bundle.data['rating'] = bundle.data['rating'][0]
        if 'tags' in bundle.data:
            taglist = []
            for element in bundle.data['tags']:
                taglist.append(element.data['tags'])
            bundle.data['tags'] = ','.join(taglist)
        if 'reply_to' in bundle.data and bundle.data['reply_to']:
            bundle.data['reply-to'] = {'MD_Identifier' : bundle.data['reply_to']}
        del bundle.data['reply_to']
        if 'domainURN' in bundle.data:
            domainList = []
            for domain in bundle.data['domainURN']:
                if isinstance(domain, Bundle):
                    if 'domainURN' in domain.data:
                        domainList.append(domain.data['domainURN'])
            bundle.data['domainURN'] = domainList

        bundle = dehydrateManyToManyWithSubElement(bundle, 'citation', 'GVQ_Publication')
        bundle = dehydrateManyToManyWithSubElement(bundle, 'externalFeedback', 'CI_OnlineResource')

        return bundle

    # Update to prepend_urls when 1.0 versions is used.
    def override_urls(self):
        return [url(r"^(?P<resource_name>%s)/search$" % (self._meta.resource_name),
                self.wrap_view('get_search'),name="api_get_search"),
                url(r"^collections%s$" % (trailing_slash()),
                self.wrap_view('get_collections'),name="api_get_collections"),
                url(r"^collections%ssearch$" % (trailing_slash()),
                self.wrap_view('get_collections'),name="api_get_collections"),
               ]

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.is_authorized(request)
        self.throttle_check(request)

        self._check_request(request)

        # Create the 'or' filtersets.
        sqs = feedbackmodel.GVQ_FeedbackItem.objects.all()

        #Filter on fields.
        fieldDictionary = getModelFieldSearchDictionary()

        fieldList = construct_field_filter_list(request, 'fields', fieldDictionary)
        if len(fieldList) != 0 :
            sqs = sqs.filter( reduce(operator.or_, fieldList ) ).distinct()
            #Cannot search for in more than 5-6 tables in one go. Force database request.
            len(sqs)

        #Name value dictionary supported.
        urlDatabaseNamedictionary = getModelNameValueSearchDictionary()


        ##Filter on special values.
        #Probably not necessary to execute the filterset already.
        for urlKey in urlDatabaseNamedictionary:
            resultList = construct_value_filter_list(request, urlKey, urlDatabaseNamedictionary[urlKey])
            if len(resultList) != 0 :
                sqs = sqs.filter(reduce(operator.or_, resultList) ).distinct()


        #Handle the text search.
        searchItems = getqSearchItems()
        searchList = request.GET.get('q', '').split()
        if searchList != '':
            first_search = True
            #'And' all the searches for q.
            for searchValue in searchList:
                #Execute after the first search.
                if first_search:
                    first_search = False
                else: len(sqs)
                sqs = sqs.filter( reduce(operator.or_, construct_search_list(searchItems, searchValue))).distinct()
        return self._create_collection_response(request, sqs)

    def get_collections(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.is_authorized(request)
        self.throttle_check(request)

        codes, spaces = self._check_collection_request(request)

        #Create a list of primary target items. Search for each code - codespace combination.
        queryList = list()
        codeList = list()
        codeSpaceList = list()
        notFoundCodeList = list()
        notFoundCodeSpaceList = list()
        for code, space in zip(codes, spaces):
            alist = [('primaryTarget__resourceRef__code__iexact', code), ('primaryTarget__resourceRef__codeSpace__iexact', space)]
            andList = [Q(x) for x in alist]
            query = feedbackmodel.GVQ_FeedbackItem.objects.all().filter(reduce(operator.and_, andList))

            if query.count() > 0 :
                queryList.append(query)
                codeList.append(code)
                codeSpaceList.append(space)
            else:
                notFoundCodeList.append(code)
                notFoundCodeSpaceList.append(space)

        object_list = list()
        for query, code, codespace in zip(queryList, codeList, codeSpaceList):
            averageRating =                 query.aggregate(Avg('gvq_rating__score'))
            numberOfRatings =               query.filter(gvq_rating__isnull = False).distinct().count()
            totalCount = query.count()
            rating_1 =                      query.filter(gvq_rating__score__exact = 1).distinct().count()
            rating_2 =                      query.filter(gvq_rating__score__exact = 2).distinct().count()
            rating_3 =                      query.filter(gvq_rating__score__exact = 3).distinct().count()
            rating_4 =                      query.filter(gvq_rating__score__exact = 4).distinct().count()
            rating_5 =                      query.filter(gvq_rating__score__exact = 5).distinct().count()
            numberOfComments =              query.filter(userComment__isnull= False).distinct().count()
            averageUserExpertiseLevel =     query.aggregate(Avg('user__expertiseLevel'))
            latestReview =                  query.order_by('-dateStamp')[0].dateStamp.date()
            numberOfPublications =          query.filter(citation__title__isnull= False).distinct().count()
            numberOfSecondaryTargets =      query.filter(secondaryTarget__isnull= False).distinct().count()
            numberOfSupplementaryTargets =  query.filter(supplementaryTarget__isnull= False).distinct().count()
            numberOfUsageReports =          query.filter(usage__isnull= False).distinct().count()
            #TODO domainUsageCount
            #TODO tagCount
            commercialDataProducerRole =    query.filter(userRole__GVQ_UserRoleCode__iexact= 'CommercialDataProducer').distinct().count()
            researchEndUserRole =           query.filter(userRole__GVQ_UserRoleCode__iexact= 'ResearchEndUser').distinct().count()
            nonResearchEndUserRole  =       query.filter(userRole__GVQ_UserRoleCode__iexact= 'NonResearchEndUser').distinct().count()
            scientificDataProducerRole =    query.filter(userRole__GVQ_UserRoleCode__iexact= 'ScientificDataProducer').distinct().count()

            ratingsExp_1                 =    query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 1).distinct().count()
            ratingsExp_2                 =    query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 2).distinct().count()
            ratingsExp_3                 =    query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 3).distinct().count()
            ratingsExp_4                 =    query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 4).distinct().count()
            ratingsExp_5                 =    query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 5).distinct().count()

            ratingsExp = dict()
            ratingsExp['1']              =   query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 1).distinct().aggregate(Avg('gvq_rating__score'))['gvq_rating__score__avg']
            ratingsExp['2']              =   query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 2).distinct().aggregate(Avg('gvq_rating__score'))['gvq_rating__score__avg']
            ratingsExp['3']              =   query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 3).distinct().aggregate(Avg('gvq_rating__score'))['gvq_rating__score__avg']
            ratingsExp['4']              =   query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 4).distinct().aggregate(Avg('gvq_rating__score'))['gvq_rating__score__avg']
            ratingsExp['5']              =   query.filter(gvq_rating__isnull = False).filter(user__expertiseLevel__exact = 5).distinct().aggregate(Avg('gvq_rating__score'))['gvq_rating__score__avg']
            for k, v in ratingsExp.iteritems():
                if v == None:
                    ratingsExp[k] = '0'

            itemsExp_1                   =    query.filter(user__expertiseLevel__exact = 1).distinct().count()
            itemsExp_2                   =    query.filter(user__expertiseLevel__exact = 2).distinct().count()
            itemsExp_3                   =    query.filter(user__expertiseLevel__exact = 3).distinct().count()
            itemsExp_4                   =    query.filter(user__expertiseLevel__exact = 4).distinct().count()
            itemsExp_5                   =    query.filter(user__expertiseLevel__exact = 5).distinct().count()

            itemUnderReview = {'MD_Identifier':
                     {'code' : { 'CharacterString' : code},
                      'codeSpace' : { 'CharacterString' :  codespace}}}

            summary = {'itemUnderReview'            : itemUnderReview,
                       'averageRating'              : averageRating['gvq_rating__score__avg'] or '0',
                       'numberOfRatings'            : numberOfRatings or '0',
                       'numberOfFeedbackItems'      : totalCount or '0',
                       'ratingsByLevel'             : { 'level1': rating_1,
                                                        'level2': rating_2,
                                                        'level3': rating_3,
                                                        'level4': rating_4,
                                                        'level5': rating_5
                                                      },
                       'numberOfUserComments'       : numberOfComments or '0',
                       'averageUserExpertiseLevel'  : averageUserExpertiseLevel['user__expertiseLevel__avg'],
                       'latestReview'               : latestReview,
                       'numberOfPublications'       : numberOfPublications or '0',
                       'numberOfSecondaryTargets'   : numberOfSecondaryTargets or '0',
                       'numberOfSupplementaryTargets':numberOfSupplementaryTargets or '0',
                       'numberOfUsageReports'        : numberOfUsageReports or '0',
                       'userRoleCount'              :  { 'category' :[
                                                            {'value' : 'researchEndUser', 'count' : researchEndUserRole or '0'},

                                                            {'value' : 'nonResearchEndUser', 'count' : nonResearchEndUserRole or '0'},

                                                            {'value' : 'commercialDataProducer', 'count' : commercialDataProducerRole or '0'},

                                                            {'value' : 'scientificDataProducer', 'count' : scientificDataProducerRole or '0'}]}
                                                      ,
                        'userRatingsByExpertiseLevel': { 'category'  :[
                                                            {'value'  : '1',
                                                            'average' : ratingsExp['1'],
                                                            'count'   : ratingsExp_1 or '0'
                                                            },
                                                            {'value'  : '2',
                                                            'average' :ratingsExp['2'],
                                                            'count'   : ratingsExp_2 or '0'},
                                                            {'value'  : '3',
                                                            'average' : ratingsExp['3'],
                                                            'count'   : ratingsExp_3 or '0'},
                                                            {'value'  : '4',
                                                            'average' : ratingsExp['4'],
                                                            'count'   : ratingsExp_4 or '0'},
                                                            {'value'  : '5',
                                                            'average' : ratingsExp['5'],
                                                            'count'   : ratingsExp_5 or '0'}]}
                                                      ,
                       'feedbackItemsByExpertiseLevel': { 'category' :[
                                                            {'value' : '1', 'count' : itemsExp_1 or '0'},

                                                            {'value' : '2', 'count' : itemsExp_2 or '0'},

                                                            {'value' : '3', 'count' : itemsExp_3 or '0'},

                                                            {'value' : '4', 'count' : itemsExp_4 or '0'},

                                                            {'value' : '5', 'count' : itemsExp_5 or '0'}]}

                      }

            #Use the Tastypie paginator.
            paginator = Paginator(request.GET, query)
            try:
                to_be_serialized = paginator.page()
            except ValueError:
                raise BadRequest("Sorry, no results on that page.")

            bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['objects']]
            meta_info = to_be_serialized['meta']
            to_be_serialized = []


            for bundle in bundles:
                self.full_dehydrate(bundle)
                to_be_serialized.append({ "item" : bundle})

            to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

            #Append extra information the format to create a collection.
            object_list.append( {'collection':  {'GVQ_FeedbackCollection':
                { 'itemCollection' : to_be_serialized,
                  'pagination': {'count': meta_info['total_count'], 'limit': meta_info['limit'], 'offset':        meta_info['offset']},
                  'summary': summary,
                  'itemUnderReview': itemUnderReview} }})

        for code, codespace in zip(notFoundCodeList, notFoundCodeSpaceList):
            object_list.append( {'collection':  {'GVQ_FeedbackCollection':
                { 'itemUnderReview': {'MD_Identifier':
                     {'code' : { 'CharacterString' : code},
                      'codeSpace' : { 'CharacterString' :  codespace}}}} }})


        return self.create_response(request, object_list)


    def _check_collection_request(self, request):

        #Check the return and what to raise...
        allowed_parameters = getAllowedCollectionParameters()

        user_parameters = request.GET
        for parameter in user_parameters.keys():
            if not parameter in allowed_parameters.keys():
                raise BadRequest("Parameter '"+parameter+"' of the request is unknown")
            """ If list user input is possible and the allowed values are also specified, check all the values.
            Note: there is no boolean case currently(one allowed parameter value).
            Parameter q, the only '+' separated list does not have list values. Therefore splitting is always done
            on ','"""
        target_parameters = ['target_codespace', 'target_code']

        for parameter in target_parameters:
            if not parameter in user_parameters.keys():
                raise BadRequest("Parameter ' "+parameter+
                                    "' is required.")
        codeList = user_parameters['target_code'].split(",")
        codeSpaceList = user_parameters['target_codespace'].split(",")
        if len(codeList) != len(codeSpaceList):
            raise BadRequest("Number of codes and codespaces should be equal")
        if len(codeList) > 5:
            raise BadRequest("A maximum of five code/codespace combinations is allowed")

        return codeList, codeSpaceList

    def _check_request(self, request):

        #Check the return and what to raise...
        allowed_parameters = getAllowedParameters()

        user_parameters = request.GET
        for parameter in user_parameters.keys():
            if not parameter in allowed_parameters.keys():
                raise BadRequest("Parameter '"+parameter+"' of the request is unknown")
            """ If list user input is possible and the allowed values are also specified, check all the values.
            Note: there is no boolean case currently(one allowed parameter value).
            Parameter q, the only '+' separated list does not have list values. Therefore splitting is always done
            on ','"""
            if isinstance(allowed_parameters[parameter], list):
                userValues = user_parameters[parameter].split(",")
                for userValue in userValues:
                    if not userValue.lower() in [par.lower() for par in allowed_parameters[parameter]]:
                        raise BadRequest("Value for parameter "+parameter+" '"+userValue+
                                    "' is unknown. Options are: "+", ".join(allowed_parameters[parameter]))

            if parameter == "limit":
                try:
                    limit = int(user_parameters["limit"])
                    if limit > 500:
                        raise BadRequest("Too many items have been requested, the limit is 500")
                except ValueError:
                    raise BadRequest("Limit specified is not an integer.")

    def _create_collection_response(self, request, queryset):

        #Get the average rating. Rating is not added anymore.
        #ratingdict = queryset.aggregate(Avg('gvq_rating__score'))
        #average_rating = ratingdict['gvq_rating__score__avg']

        #Use the Tastypie paginator.
        paginator = Paginator(request.GET, queryset)
        try:
            to_be_serialized = paginator.page()
        except ValueError:
            raise BadRequest("Sorry, no results on that page.")

        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['objects']]
        meta_info = to_be_serialized['meta']
        to_be_serialized = []


        #Create the response set.
        responseValue = (request.GET.get("view", ''))
        responseType = BRIEF
        if responseValue == "summary": responseType = SUMMARY
        if responseValue == "full" : responseType = FULL
        # Dehydrate the bundles in preparation for serialization.
        for bundle in bundles:
            if responseType != BRIEF:
                self.full_dehydrate(bundle)
                if responseType == SUMMARY:
                    if 'qualityOverride' in bundle.data: del bundle.data['qualityOverride']
                    if 'externalFeedback' in bundle.data: del bundle.data['externalFeedback']
                    if 'usage' in bundle.data: del bundle.data['usage']
                    if 'reply_to' in bundle.data:del bundle.data['reply_to']
                    if 'domainURN' in bundle.data:  del bundle.data['domainURN']
                    if 'tags' in bundle.data:del bundle.data['tags']
                    if 'supplementaryTarget' in bundle.data: del bundle.data['supplementaryTarget']
                    if 'secondaryTarget' in bundle.data: del bundle.data['secondaryTarget']
                    if 'user' in bundle.data: del bundle.data['user']
                    if 'reply-to' in bundle.data: del bundle.data['reply-to']
                    if 'identifier' in bundle.data: del bundle.data['identifier']

                    #Add the reference for summaries.
                    bundle.data['resource_uri'] = self.dehydrate_resource_uri(bundle)
                to_be_serialized.append({"item": bundle})

            else:
                to_be_serialized.append({"item": {"resource_uri" :self.dehydrate_resource_uri(bundle)}})



        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

        #Append extra information the format to create a collection.
        dictionary = dict()
        dictionary['items'] = to_be_serialized
        dictionary['pagination'] = {'count': meta_info['total_count'], 'limit': meta_info['limit'], 'offset': meta_info['offset']}

        object_list = dictionary
        return self.create_response(request, object_list)



class GVQ_RatingResource(ComplexModelResource):
    item = fields.ToOneField(GVQ_FeedbackItemResource, 'item')
    class Meta:
        queryset = feedbackmodel.GVQ_Rating.objects.all()
        resource_name = 'rating'
        excludes = ['id']
        include_resource_uri = False
        authentication = PostAuthentication()
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.GVQ_Rating, exclude='item'))

    def obj_update(self, bundle, **kwargs):

        bundle = self.full_hydrate(bundle)
        # Save FKs just in case.
        self.save_related(bundle)
        # Save the main object.
        bundle.obj.save()
        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def dehydrate(self, bundle):
        del bundle.data['item']
        return bundle

class CharacterStringResource(ComplexModelResource):
    citationAlternateTitle = fields.ToOneField(CI_CitationResource, 'citationAlternateTitle')
    class Meta:
        queryset = feedbackmodel.CharacterString.objects.all()
        resource_name = 'characterString'
        excludes = ['id']
        include_resource_uri = False
        serializer = CustomXMLSerializer()
        validation = ModelFormValidation(form_class =  modelform_factory(feedbackmodel.CharacterString, exclude='citationAlternateTitle'))

    def dehydrate(self, bundle):
        del bundle.data['alternateTitle']
        return bundle
