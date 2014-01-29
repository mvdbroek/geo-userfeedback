from django.db.models import Q

""" This file contains several functions related to configuration. These are related to namespaces and
    allowed search fields when doing a HTTP request. """
#===================================================================================================

#Constructs 'OR' type search filter for requested fields (is also a filter to include certain fields).
def construct_field_filter_list(request, fieldName, findDictionary):

    # Create an empty argument list.
    argumentList = list()
    # Select the fields list.

    fieldList = (request.GET.get(fieldName, '')).split(',')
    if fieldList == '': return argumentList

    for field in fieldList:
        for key in findDictionary:
            if field == key :
                argumentList.append(Q(**{findDictionary[key] :False} ))

    return argumentList

#Constructs 'OR' type search filter for the allowed key-value pairs.
def construct_value_filter_list(request, key, database_key):

    argumentList = list()
    values = request.GET.get(key, None)
    if values:
        valueList = values.split(',')
        for value in valueList:
            argumentList.append(Q(**{database_key : value}))

    return argumentList

#Constructs 'OR' type search filter, to look for a certain query value q in diverse database fields.
def construct_search_list(searchItems, searchValue):

    argumentList = list()
    for searchItem in searchItems:
        argumentList.append(Q(**{searchItem : searchValue}))
    return argumentList

#===================================================================================================
# This could be moved to a configuration file. But this not more work, and a little faster.


# The codespace for your feedback MD_Identifier.
def getServerCodeSpace():
    return "geoviqua_test_server"

# Parameters that can be part of the HTTP request for feedback "items".
def getAllowedParameters():
    return {
            'target_codespace':      None,
            'target_code':           None,
            'rating':               ['1','2','3', '4','5'],
            'report_aspect':        ['usage', 'problem', 'fitnessforpurpose', 'alternatives'],
            'feedback_domain': None,
            'user_domain' :  None,
            'user_role'  : ['CommercialDataProducer',
                             'ResearchEndUser'  ,
                             'NonResearchEndUser',
                             'ScientificDataProducer'],
             'fields' : ['comment',
                            'rating',
                            'citation',
                            'quality_override',
                            'domain_urn',
                            'reply_to',
                            'external_feedback',
                            'tags',
                            'usage'],
               'q': None,
               'expertise_level': ['1','2','3','4','5'],
               'view': ['full','brief','summary'],
               'format': None,
               'limit': None,
               'offset': None

           }
# Parameters that can be part of the HTTP request for feedback "primary_target_ids".
def getAllowedTargetParameters():
    return {
            'minimum_average_rating' : ['1','1.5','2','2.5','3','3.5','4','4.5','5'],
            'minimum_total_count': None,
            'rating': ['1','2','3', '4','5'],
            'report_aspect': ['usage', 'problem', 'fitnessforpurpose', 'alternatives'],
            'feedback_domain': None,
            'user_domain' :  None,
            'user_role'  : ['CommercialDataProducer',
                             'ResearchEndUser'  ,
                             'NonResearchEndUser',
                             'ScientificDataProducer'],
             'fields' : ['comment',
                            'rating',
                            'citation',
                            'quality_override',
                            'domain_urn',
                            'reply_to',
                            'external_feedback',
                            'tags',
                            'usage'],
             'expertise_level': ['1','2','3', '4','5'],
              'q': None,
               'format': None,
               'limit': None,
               'offset': None

           }

# Parameters that can be part of the HTTP request for feedback "collections".
def getAllowedCollectionParameters():
    return {
              'target_codespace':None,
              'target_code': None,
              'format': None,
              'limit': None,
              'offset': None

           }

# Defines the relations between search parameters and database entries when searching for items.
def getModelNameValueSearchDictionary():
    return { 'target_code'               : 'primaryTarget__resourceRef__code__iexact',
        'target_codespace'           : 'primaryTarget__resourceRef__codeSpace__iexact',
        'rating'                  : 'gvq_rating__score__exact',
        'report_aspect'           : 'usage__reportAspect__iexact',
        'feedback_domain'          : 'domainURN__domainURN__iexact',
        'user_domain'              : 'user__applicationDomain__applicationDomain__iexact',
        'user_role'                : 'userRole__GVQ_UserRoleCode__iexact',
        'expertise_level'            : 'user__expertiseLevel__exact'
    }

# Defines the relations between the "field" parameter and database entries when searching for items.
def getModelFieldSearchDictionary():
    return { 'comment'           : 'userComment__isnull',
            'rating'            :  'gvq_rating__isnull',
            'citation'          :  'citation__title__isnull',
            'quality_override'   : 'qualityOverride__isnull',
            'domain_urn'         : 'domainURN__isnull',
            'reply_to'          :  'reply_to__isnull',
            'external_feedback'  : 'externalFeedback__isnull',
            'tags'              :  'tags__isnull',
            'usage'             :  'usage__isnull'
            }

# Defines the any text field database entries..
def getqSearchItems():
    return              [  'tags__tags__icontains',
                        'subject__icontains',
                        'userComment__icontains',
                        'citation__title__icontains',
                        'citation__DOI__icontains',
                        'domainURN__domainURN__icontains',
                        'usage__usageDescription__icontains',
                        'gvq_rating__justification__icontains',
                        'primaryTarget__dataFocus__otherFocus__icontains'
                        ]

# Defines the relations between search parameters and database entries when searching for primary_target_ids.
def getTargetModelNameValueSearchDictionary():
    return {
          'rating'                  : 'resourceRef__primaryTarget__gvq_rating__score__iexact',
          'report_aspect'           : 'resourceRef__primaryTarget__usage__reportAspect__iexact',
          'feedback_domain'         : 'resourceRef__primaryTarget__domainURN__domainURN__iexact',
          'user_domain'             : 'resourceRef__primaryTarget__user__applicationDomain__applicationDomain__iexact',
          'user_role'               : 'resourceRef__primaryTarget__userRole__GVQ_UserRoleCode__iexact',
          'expertise_level'         : 'resourceRef__primaryTarget__user__expertiseLevel__exact',
          'minimum_total_count'     : 'count_items__gte',
          'minimum_average_rating'  : 'avg_items__gte'
        }

# Defines the relations between the "field" parameter and database entries when searching for primary_target_ids.
def getTargetModelFieldSearchDictionary():
    return { 'comment'           : 'resourceRef__primaryTarget__userComment__isnull',
            'rating'            :  'resourceRef__primaryTarget__gvq_rating__isnull',
            'citation'          :  'resourceRef__primaryTarget__citation__title__isnull',
            'quality_override'   : 'resourceRef__primaryTarget__qualityOverride__isnull',
            'domain_urn'         : 'resourceRef__primaryTarget__domainURN__isnull',
            'reply_to'          :  'resourceRef__primaryTarget__reply_to__isnull',
            'external_feedback'  : 'resourceRef__primaryTarget__externalFeedback__isnull',
            'tags'              :  'resourceRef__primaryTarget__tags__isnull',
            'usage'             :  'resourceRef__primaryTarget__usage__isnull'
            }

# Defines the any text field database entries, when searching for primary_target_ids.
def getTargetqSearchItems():
    return     [   'resourceRef__primaryTarget__tags__tags__icontains',
                    'resourceRef__primaryTarget__subject__icontains',
                    'resourceRef__primaryTarget__userComment__icontains',
                    'resourceRef__primaryTarget__citation__title__icontains',
                    'resourceRef__primaryTarget__citation__DOI__icontains',
                    'resourceRef__primaryTarget__domainURN__domainURN__icontains',
                    'resourceRef__primaryTarget__usage__usageDescription__icontains',
                    'resourceRef__primaryTarget__gvq_rating__justification__icontains',
                    'resourceRef__primaryTarget__primaryTarget__dataFocus__otherFocus__icontains'
                ]

# Codelists used and the reference to it.
def getAttributeDictionary():

    return {'GVQ_UserRoleCode' : {'codeList':
                'http://schemas.geoviqua.org/GVQ/4.0/resources/Codelist/gvqCodelists.xml#GVQ_UserRoleCode'},
            'MD_ScopeCode': {'codeList':
                'http://schemas.geoviqua.org/GVQ/4.0/resources/Codelist/gvqCodelists.xml#MD_ScopeCode'
                },
            'CI_RoleCode' : {'codeList':
                'http://wis.wmo.int/2008/catalogues/draft_version_1-1/WMO_Codelists_ver1_1.xml#CI_RoleCode'
                },
            'GVQ_ReportAspectCode': {'codeList':
                'http://schemas.geoviqua.org/GVQ/4.0/resources/Codelist/gvqCodelists.xml#GVQ_ReportAspectCode'
                },
            'CI_DateTypeCode': {'codeList':
                'http://wis.wmo.int/2008/catalogues/draft_version_1-1/WMO_Codelists_ver1_1.xml#CI_DateTypeCode'
                },
            'GVQ_PublicationPurposeCode': {'codeList':
                'http://schemas.geoviqua.org/GVQ/4.0/resources/Codelist/gvqCodelists.xml#GVQ_PublicationPurposeCode'
                },
             'GVQ_PublicationCategoryCode': {'codeList':
                'http://schemas.geoviqua.org/GVQ/4.0/resources/Codelist/gvqCodelists.xml#GVQ_PublicationCategoryCode'
                },
             'CI_OnlineFunctionCode': {'codeList': 'http://www.isotc211.org/2005/gmd'},

             'CI_PresentationFormCode': {'codeList': 'http://www.isotc211.org/2005/gmd'}
            }

# Value used for attributes related to codelists..
def getAttributeValueDictionary():
    return  {'GVQ_UserRoleCode' : 'codeListValue',
            'MD_ScopeCode' : 'codeListValue',
            'CI_RoleCode': 'codeListValue',
            'GVQ_ReportAspectCode': 'codeListValue',
            'CI_DateTypeCode': 'codeListValue',
            'GVQ_PublicationCategoryCode': 'codeListValue',
            'GVQ_PublicationPurposeCode': 'codeListValue',
            'CI_OnlineFunctionCode': 'codeListValue',
            'CI_PresentationFormCode': 'codeListValue'
            }

# The fields that are not fully modeled, but where a textfield is assumed which contains the XML related element.
def getXMLTextFields():
    return ["phone", "address", "extent", "alternativeDataset", "qualityOverride"]

# The schema location
def getSchemaLocation():
    return "http://www.geoviqua.org/QualityInformationModel/4.0 http://schemas.geoviqua.org/GVQ/4.0/GeoViQua_PQM_UQM.xsd"

# The namespaces used.s
def getNamespaceInfo():

    gvqspace            =   "http://www.geoviqua.org/QualityInformationModel/4.0"
    gcospace            =   "http://www.isotc211.org/2005/gco"
    gmd19157space       =   "http://www.geoviqua.org/gmd19157"
    updated19115space   =   "http://www.geoviqua.org/19115_updates"
    gmdspace            =   "http://www.isotc211.org/2005/gmd"
    gmlspace            =   "http://www.opengis.net/gml/3.2"
    xsispace            =   "http://www.w3.org/2001/XMLSchema-instance"


    gco            =    "{%s}" %      gcospace
    gmd19157       =    "{%s}" %      gmd19157space
    gmd            =    "{%s}" %      gmdspace
    updated19115   =    "{%s}" %      updated19115space
    gvq            =    "{%s}" %      gvqspace
    xsi            =    "{%s}" %      xsispace

    NSMAP = {'gvq'         :    gvqspace,
             'gco'         :    gcospace,
             'gmd19157'    :    gmd19157space,
             'updated19115':    updated19115space,
             'gmd'         :    gmdspace,
             'gml'         :    gmlspace,
             'xsi'         :    xsispace,
             }

    namespaceDict = {   'GVQ_FeedbackResponse':         gvq,
                        'GVQ_FeedbackCollection':       gvq,
                        'itemUnderReview':              gvq,
                        'collection':                   gvq,
                        'summary':                      gvq,
                        'pagination':                   gvq,
                        'offset':                       gvq,
                        'limit':                        gvq,
                        'count':                        gvq,
                        'value':                        gvq,
                        'average':                      gvq,
                        'averageRating':                gvq,
                        'numberOfFeedbackItems':        gvq,
                        'numberOfRatings':              gvq,
                        'ratingsByLevel':               gvq,
                        'level1':                       gvq,
                        'level2':                       gvq,
                        'level3':                       gvq,
                        'level4':                       gvq,
                        'level5':                       gvq,
                        'numberOfUserComments':         gvq,
                        'numberOfUsageReports':         gvq,
                        'averageUserExpertiseLevel':    gvq,
                        'userRatingsByExpertiseLevel' : gvq,
                        'feedbackItemsByExpertiseLevel':gvq,
                        'latestReview':                 gvq,
                        'userRoleCount':                gvq,
                        'numberOfPublications':         gvq,
                        'numberOfSecondaryTargets':     gvq,
                        'numberOfSupplementaryTargets': gvq,
                        'primaryTarget':                gvq,
                        'userFeedback':                 gvq,
                        'item':                         gvq,
                        'identifier':                   gvq,
                        'subject':                      gvq,
                        'resourceRef':                  gvq,
                        'GVQ_Publication':              gvq,
                        'GVQ_PublicationPurposeCode':   gvq,
                        'scope'   :                     gvq,
                        'target'   :                    gvq,
                        'title':                        gmd,
                        'doi'   :                       gvq,
                        'volume'   :                    gvq,
                        'issue'   :                     gvq,
                        'pages'   :                     gvq,
                        'purpose'   :                   gvq,
                        'relatedResource'   :           gvq,
                        'category'   :                  gvq,
                        'onlineResource'   :            gvq,
                        'otherFocus'   :                gvq,
                        'dataFocus'    :                gvq,
                        'natureOfTarget'   :            gvq,
                        'parent'   :                    gvq,
                        'secondaryTarget'   :           gvq,
                        'supplementaryTarget'   :       gvq,
                        'userRole'   :                  gvq,
                        'GVQ_UserRoleCode'   :          gvq,
                        'user'   :                      gvq,
                        'userDetails'   :               gvq,
                        'applicationDomain'   :         gvq,
                        'expertiseLevel'   :            gvq,
                        'externalUserId'   :            gvq,
                        'dateStamp'   :                 gvq,
                        'qualityOverride'   :           gvq,
                        'externalFeedback'   :          gvq,
                        'userComment'   :               gvq,
                        'comment'   :                   gvq,
                        'mime-type':                    gvq,
                        'rating'   :                    gvq,
                        'score':                        gvq,
                        'justification':                gvq,
                        'usage'   :                     gvq,
                        'reportAspect'   :              gvq,
                        'GVQ_ReportAspectCode'   :      gvq,
                        'usageDescription'   :          gvq,
                        'discoveredIssue'   :           gvq,
                        'GVQ_DiscoveredIssue'   :       gvq,
                        'knownProblem'   :              gvq,
                        'workAround'   :                gvq,
                        'alternativeDataset'   :        gvq,
                        'referenceDoc'   :              gvq,
                        'fixedResource'   :             gvq,
                        'citation'   :                  gvq,
                        'reply-to'   :                  gvq,
                        'domainURN'   :                 gvq,
                        'tags'   :                      gvq,
                        'expectedFix'   :               gvq,
                        'DQ_Scope'    :                 gmd19157,
                        'extent'  :                     gvq,
                        'MD_Identifier':                updated19115,
                        'version':                      updated19115,
                        'authority':                    gmd,
                        'code':                         gmd,
                        'codeSpace':                    updated19115,
                        'CI_Date':                      gmd,
                        'CI_PresentationFormCode'   :   gmd,
                        'alternateTitle'   :            gmd,
                        'date'   :                      gmd,
                        'Date'   :                      gco,
                        'dateType'   :                  gmd,
                        'CI_DateTypeCode'   :           gmd,
                        'CI_ResponsibleParty'   :       gmd,
                        'linkage'   :                   gmd,
                        'URL'   :                       gmd,
                        'protocol':                     gmd,
                        'applicationProfile':           gmd,
                        'name'              :           gmd,
                        'function'          :           gmd,
                        'description'       :           gmd,
                        'spatialExtent'   :             gmd,
                        'individualName'   :            gmd,
                        'organisationName'   :          gmd,
                        'positionName'   :              gmd,
                        'contactInfo'   :               gmd,
                        'phone' :                       gmd,
                        'contactInstructions':          gmd,
                        'hoursOfService':               gmd,
                        'address' :                     gmd,
                        'role'   :                      gmd,
                        'CI_RoleCode':                  gmd,
                        'MD_DataIdentification'   :     gmd,
                        'MD_ScopeCode':                 gvq,
                        'DateTime'   :                  gco,
                        'DateType'   :                  gco,
                        'CharacterString':              gco,
                        'Integer':                      gco,
                        'DOI' :                         gvq,
                        'ISBN':                         gmd,
                        'ISSN':                         gmd,
                        'edition':                      gmd,
                        'editionDate':                  gmd,
                        'otherCitationDetails':         gmd,
                        'collectiveTitle' :             gmd,
                        'dateTime':                     gmd,
                        'editionDateTime':              gmd,
                        'citedResponsibleParty':        gmd,
                        'presentationForm':             gmd,
                        'CI_OnlineResource':            gmd,
                        'CI_OnlineFunctionCode':        gmd,
                        'issueIdentification':          gmd,
                        'page':                         gmd,
                        'series':                       gmd,
                        'schemaLocation' :              xsi
                  }


    return namespaceDict, NSMAP

