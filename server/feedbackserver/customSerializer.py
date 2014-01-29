from tastypie.serializers import Serializer
from django.utils.encoding import force_unicode
from tastypie.bundle import Bundle
from lxml import etree
from configuration import getNamespaceInfo, getAttributeDictionary, getAttributeValueDictionary, getSchemaLocation, getXMLTextFields
import logging
import json as json
import xmltodict

try:
    import lxml
    from lxml.etree import Element
except ImportError:
    lxml = None

def itemKeyList():
    return ['subject', 'dateStamp', 'rating', 'userComment', 'userRole', 'user', 'domainURN', 'tags',
    'identifier','primaryTarget', 'secondaryTarget', 'supplementaryTarget', 'usage', 'citation',
    'externalFeedback', 'reply-to', 'resource_uri']


def ordering():
    collectionOrder  = ["itemUnderReview", "itemCollection" , "pagination", "summary"]
    summaryOrder = ["itemUnderReview", "averageRating", "numberOfRatings", "numberOfFeedbackItems", "ratingsByLevel",
                    "numberOfUserComments", "averageUserExpertiseLevel", "latestReview", "numberOfPublications", "numberOfSecondaryTargets",
                    "numberOfSupplementaryTargets", "numberOfUsageReports", "userRoleCount", "userRatingsByExpertiseLevel",
                    "feedbackItemsByExpertiseLevel"]#TODO extend
    itemorder = ["identifier", "subject", "primaryTarget", "secondaryTarget", "supplementaryTarget",
    "userRole", "user", "dateStamp", "qualityOverride", "externalFeedback", "userComment", "rating",
    "usage", "citation", "reply-to", "domainURN", "tags", "resource_uri"]
    targetOrder = ["resourceRef", "dataFocus", "natureOfTarget", "parent"]
    ratingOrder = ["score", "justification"]
    usageReportOrder = ["reportAspect", "usageDescription", "discoveredIssue"]
    userCommentOrder = ["comment", "mime-type"]
    userInformationOrder = ["userDetails", "applicationDomain", "expertiseLevel", "userRole", "externalUserId"]
    userDetailOrder = ["individualName", "organisationName", "positionName", "contactInfo", "role"]
    dataFocusOrder = ["extent", "otherFocus"]
    md_identifierOrder = ["authority", "code", "codeSpace", "version"]
    publicationOrder = ["title", "alternateTitle", "date", "edition", "editionDate", "identifier", "citedResponsibleParty",
    "presentationForm", "series", "otherCitationDetails", "collectiveTitle", "ISBN", "ISSN"]
    citationOrder = publicationOrder
    publicationOrder.extend([ "target", "doi", "volume", "issue", "pages", "purpose", "relatedResource", "scope", "category", "onlineResource"])
    onlineResourceOrder = ["linkage", "protocol", "applicationProfile", "name", "description", "function"]
    discoveredIssueOrder = ["target", "knownProblem", "workAround", "alternativeDataset", "referenceDoc", "fixedResource", "expectedFix"]
    dateOrder = ["date", "dateType"]
    categoryOrder = ["value", "average", "count", "GVQ_PublicationCategoryCode"]


    return {
    "GVQ_FeedbackCollection": collectionOrder,
    "item" : itemorder,
    "primaryTarget" : targetOrder,
    "secondaryTarget" : targetOrder,
    "supplementaryTarget" : targetOrder,
    "rating" : ratingOrder,
    "usage": usageReportOrder,
    "userComment": userCommentOrder,
    "user" : userInformationOrder,
    "dataFocus": dataFocusOrder,
    "MD_Identifier" : md_identifierOrder,
    "GVQ_Publication" : publicationOrder,
    "GVQ_DiscoveredIssue" : discoveredIssueOrder,
    "CI_OnlineResource" : onlineResourceOrder,
    "CI_Citation" : citationOrder,
    "CI_Date" : dateOrder,
    "category" : categoryOrder,
    "summary" : summaryOrder,
    "userDetails" : userDetailOrder,
    }

class CustomXMLSerializer(Serializer):

    def to_xml(self, data, options = None):

        options = options or {}

        data = self.to_json(data)
        data = json.loads(data)

        # Load namespaces and attributevalues specific for this serializer.
        self.attributeDictionary = getAttributeDictionary()
        self.attributeValueDictionary = getAttributeValueDictionary()
        namespaceDict, NSMAP = getNamespaceInfo()

        data = self.to_customEtree(data, namespaceDict, options, nsmap=NSMAP)
        etree.strip_tags(data, "itemCollection")
        ##Create string data.
        data = etree.tostring(data)
        return data

    def to_html(self, data, options = None):
        data = self.to_json(data)
        data = json.loads(data)
        return self.parseData(data, None, 0)


    def parseData(self, data, parent, level):
        if parent == None: parent = ""
        if isinstance(data, (list, tuple)):
            if level == 1:
                htmlString = "<div id='collectionList' class='list-array level"+str(level)+"'>\n"
                for item in data:
                    htmlString += self.parseData(item, parent, level + 1)
                htmlString += "</div>\n"
            else:
                htmlString = "<ul class='list-array level"+str(level)+"'>\n"
                for item in data:
                    htmlString += self.parseData(item, parent, level + 1)
                htmlString += "</ul>\n"
            return htmlString
        if isinstance(data, dict):
            if level == 0 and 'GVQ_FeedbackCollection' in data:
                htmlString = "<p>GVQ_FeedbackCollection</p>"
                for item in data:
                    htmlString += self.parseData(data[item], parent, level+1)
            elif level == 2 and 'item' in data:
                if 'subject' in data['item']:
                    htmlString = "<h3>Feedback item: "+data['item']['subject']+"</h3>\n<div>\n"
                    for key in itemKeyList():
                        if key in data['item']:
                                htmlString += "<li><p>"+key+"</p>\n<div data-type='item-"+key+"'>"+self.parseData(data['item'][key], parent, level+1)+"</div></li>"

                    htmlString += '</div>\n'
            else:
                htmlString = "<ul class='list-dict level"+str(level)+"'>\n"
                for item in data:
                    htmlString += "<div data-type='data-"+item+"'><p>"+item+"</p>" +self.parseData(data[item], parent, level+1)+"</div>"
                htmlString += "</ul>\n"
            return htmlString

        else:
            return "<ul><li>"+force_unicode(data)+"</li></ul>"

    def to_customEtree(self, data, subs, options=None,  nsmap=None, namespace=None, name=None, depth=0, parent = None):
        """Adapted version of tastypies 0.9.11 to_customEtree serializer code version 0.9.11 available under BSD license
        Now supports namespaces and creation of attributes. Some small adaptions.
        """
        if name == None: sname = ''
        else: sname = name
        if isinstance(data, (list, tuple)):
            if name == None and parent != None:
                element = parent
            else:
                if depth == 0 and data and 'collection' in data[0]:
                    #Add the defined namespaces.
                    sname = 'GVQ_FeedbackResponse'
                    element = Element(subs.get(sname, '') + sname, nsmap=nsmap)
                    element.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation" , getSchemaLocation())
                else:
                    element = Element(subs.get(sname,'') + (name or 'objects'), nsmap=nsmap)
            for item in data:
                element.append(self.to_customEtree(item, subs, options, depth=depth+1, parent = element))
        elif isinstance(data, dict):
            if depth == 0:
                #Add the defined namespaces.
                if 'GVQ_FeedbackCollection' in data:
                    sname = 'GVQ_FeedbackResponse'
                    element = Element(subs.get(sname, '') + sname, nsmap=nsmap)
                    element.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation" , getSchemaLocation())
                else:
                    element = Element(subs.get(sname, '') + (name or 'response'), nsmap=nsmap)
            else:
                if name == None and parent != None:
                    element = parent
                else:
                    element = Element(subs.get(sname, '') + (name or 'object'), nsmap=nsmap)
                #element.set('type', 'hash')

            ##Ordering needed.
            orderingDict = ordering()
            orderName = name or element.tag
            if orderName.find("}") != -1: orderName = orderName.split("}")[1]
            if orderName in orderingDict:
                for orderedElement in orderingDict[orderName]:
                    if (orderedElement in data) and (data[orderedElement]):
                        if (orderedElement == 'domainURN' or orderedElement == 'applicationDomain') or isinstance(data[orderedElement], list) :#data[orderedElement]:#or orderedElement == 'usage' or orderedElement == 'discoveredIssue'):#isinstance(field_object, list):
                            for item in data[orderedElement]:
                                element.append(self.to_customEtree(item, subs, options, name = orderedElement, depth = depth + 1,  parent = element))
                        else:
                            element.append(self.to_customEtree(data[orderedElement], subs, options, name = orderedElement, depth = depth + 1, parent = element))
            else:
                for (key, value) in data.items():
                    if ((key == 'domainURN' or key == 'applicationDomain') or isinstance(value, list) and (key != 'items')) :#isinstance(field_object, list):
                        for item in value:
                            element.append(self.to_customEtree(item, subs, options, name = key, depth = depth + 1,  parent = element))
                    else:
                        element.append(self.to_customEtree(value, subs, options, nsmap=nsmap, name=key, depth=depth+1,  parent = element))

        else:
            element = Element(subs.get(sname, '') + (name or 'value'), nsmap=nsmap)
            simple_data = self.to_simple(data, options)
            data_type = get_type_string(simple_data)
            #if data_type != 'string':
                #element.set('type', get_type_string(simple_data))
            if data_type != 'null':
                # Handle the attributes.Note only at this level attributes are added.
                for key, value in self.attributeDictionary.get(name, dict()).items():
                    element.set(key, value)
                attributeValueList = self.attributeValueDictionary.get(name, None)
                if attributeValueList: element.set(attributeValueList, simple_data)
                element.text = force_unicode(simple_data)
        return element


    def from_xml(self, content):
        tree = etree.fromstring(content)
        NSMAP = ['codeList', 'codeListValue', 'schemaLocation']

        etree.strip_attributes(tree, *NSMAP)
        root = tree
        etree.cleanup_namespaces(root)

        namespaces = {
             'gvq'         :'',
             'gco'         :'',
             'gmd19157'    :'',
             'updated19115':'',
             'gmd'         :'',
             'gml'         :'',
             'xsi'         :'',
             'xmlns'       :'',
             }

        #Some fields are xml text fields. The fields must be unique inside the model.
        # Store those elements temporarily.
        listOfTextFields = getXMLTextFields()
        fieldDictionary = dict()
        namespaceDict, originalNamespace =  getNamespaceInfo()

        for field in listOfTextFields:
            foundElements = root.findall(".//"+namespaceDict[field]+field, namespaces=originalNamespace)
            valueList = list()
            for element in foundElements:
                valueList.append(''.join([etree.tostring(child) for child in element]))
            fieldDictionary[field] = valueList

        xmlcontent = etree.tostring(root)
        jsondata = xmltodict.parse(xmlcontent, namespaces=namespaces)

        #Replace all textFields with the xml text.
        for field in listOfTextFields:
            i = 0
            replaceDictValueWithStringElement(jsondata, field, i, fieldDictionary)

        if 'GVQ_FeedbackCollection' in jsondata:
            item = jsondata['GVQ_FeedbackCollection']['item']
        elif 'item' in jsondata:
            item = jsondata['item']
        else:
            item = jsondata
        self.from_json(json.dumps(item))
        return item

def replaceDictValueWithStringElement(jsondict, field, counter, textDictionary):
    # Solve for lists and dictionaries.
    if not isinstance(jsondict, dict):
        return
    for key in jsondict:
        if key == field:
            jsondict[field] = textDictionary[field][counter]
            counter += 1
        else:
            if isinstance(jsondict[key], dict):
                replaceDictValueWithStringElement(jsondict[key], field, counter, textDictionary)
            elif isinstance(jsondict[key], list):
                for listElement in jsondict[key]:
                    replaceDictValueWithStringElement(listElement, field, counter, textDictionary)


def get_type_string(data):
    """
    Translates a Python data type into a string format.
    """
    data_type = type(data)

    if data_type in (int, long):
        return 'integer'
    elif data_type == float:
        return 'float'
    elif data_type == bool:
        return 'boolean'
    elif data_type in (list, tuple):
        return 'list'
    elif data_type == dict:
        return 'hash'
    elif data is None:
        return 'null'
    elif isinstance(data, basestring):
        return 'string'
