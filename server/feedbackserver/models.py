from django.db import models


class DomainURN(models.Model):
    domainURN = models.CharField(max_length = 200)

    def __unicode__(self):
        return self.domainURN

class CI_OnlineResource(models.Model):
    linkage = models.CharField(max_length= 500)
    protocol = models.CharField(max_length = 250, blank = True, null = True)
    applicationProfile = models.CharField(max_length = 250, blank = True, null = True)
    name = models.CharField(max_length = 250, blank = True, null = True)
    description = models.CharField(max_length = 250, blank = True, null = True)

    ONLINEFUNCTION_CODE = (
        ('download','download'),
        ('information','information'),
        ('offlineAccess','offlineAccess'),
        ('order','order'),
        ('search','search'),
    )
    function = models.CharField(max_length = 250, choices = ONLINEFUNCTION_CODE, blank = True)

    def __unicode__(self):
        return self.linkage

class CI_Contact(models.Model):
    phone = models.TextField(blank=True) #Note: this should be a CI_Telephone type.
    address = models.TextField(blank=True) #Note this should be a CI_Address.
    #Note that only one onlineResource can be added according to the model.
    onlineResource = models.ManyToManyField(CI_OnlineResource, related_name = 'contactResource',  null = True, blank = True)
    hoursOfService = models.TextField(blank = True, null = True)
    contactInstructions = models.TextField(blank = True, null = True)

    def __unicode__(self):
        return self.address

class CI_ResponsibleParty(models.Model):
    CI_ROLECODE_CODELIST= (
        ('resourceProvider','resourceProvider'),
        ('custodian','custodian')              ,
        ('owner','owner')                      ,
        ('sponsor','sponsor')                  ,
        ('user','user')                        ,
        ('distributor','distributor')          ,
        ('originator','originator')            ,
        ('pointofContact','pointofContact')    ,
        ('principalInvestigator','principalInvestigator'),
        ('processor','processor')              ,
        ('publisher','publisher')              ,
        ('author','author')                    ,
        ('collaborator', 'collaborator')
    )
    individualName=models.CharField(max_length=100, blank=True, null = True)
    organisationName=models.CharField(max_length=100, blank=True, null = True)
    positionName=models.CharField(max_length=100, blank=True, null = True)
    role= models.CharField(max_length=32, choices = CI_ROLECODE_CODELIST)
    contactInfo = models.ManyToManyField(CI_Contact, related_name = 'contactInfo', null = True, blank=True)

    def __unicode__(self):
        return self.get_role_display()

class Tags(models.Model):
    tags = models.CharField(max_length = 200)

    def __unicode__(self):
        return self.tags

class GVQ_UserRoleCode(models.Model):
    USER_ROLE_CHOICES =(
        ('CommercialDataProducer' , 'CommercialDataProducer'),
        ('ResearchEndUser'  , 'ResearchEndUser'),
        ('NonResearchEndUser', 'NonResearchEndUser'),
        ('ScientificDataProducer','ScientificDataProducer'),
    )
    GVQ_UserRoleCode = models.CharField(max_length = 32, choices = USER_ROLE_CHOICES, default = 'NonresearchEndUser')

    def __unicode__(self):
        return self.get_GVQ_UserRoleCode_display()

class CI_Date(models.Model):
    date = models.DateField()
    DATETYPE_CHOICES =(
        ('creation', 'creation'),
        ('publication', 'publication'),
        ('revision', 'revision'),
    )
    dateType = models.CharField(max_length = 12, choices = DATETYPE_CHOICES, default = 'creation')

    def __unicode__(self):
        return self.dateType


class CI_Series(models.Model):
    name = models.CharField(max_length = 200, blank = True, null = True)
    issueIdentification = models.CharField(max_length = 200, blank = True, null = True)
    page = models.CharField(max_length = 200, blank = True, null = True)

    def __unicode__(self):
        return self.name

class MD_Identifier(models.Model):
    code = models.CharField(max_length= 200)
    codeSpace = models.CharField(max_length = 200, blank = True, null = True)
    version = models.CharField(max_length = 200, blank = True, null = True)
    authority = models.ForeignKey('feedbackserver.CI_Citation', related_name = 'authority', null = True, blank = True)
    def __unicode__(self):
        return self.code

class CI_Citation(models.Model):

    title = models.CharField(max_length = 200)
    #alternateTitle -> covered in foreignkey.
    date = models.ManyToManyField(CI_Date, related_name = 'Citation_date')
    edition = models.CharField(max_length = 200, blank = True, null = True)
    editionDate = models.DateField(null = True, blank = True)
    editionDateTime = models.DateTimeField(blank = True, null = True)
    identifier = models.ManyToManyField(MD_Identifier, related_name = 'citation_identifier', null = True, blank = True)
    citedResponsibleParty = models.ManyToManyField(CI_ResponsibleParty, related_name = 'citedResponsibleParty', null=True, blank=True)
    PRESENTATIONFORMCODES = (
        ('documentDigital'    ,'documentDigital'),
        ('documentHardCopy'   ,'documentHardCopy'),
        ('imageDigital'       ,'imageDigital'),
        ('imageHardCopy'      ,'imageHardCopy'),
        ('mapDigital'         ,'mapDigital'),
        ('mapHardCopy'        ,'mapHardCopy'),
        ('modelDigital'       ,'modelDigital'),
        ('modelHardCopy'      ,'modelHardCopy'),
        ('profileDigital'     ,'profileDigital'),
        ('profileHardCopy'    ,'profileHardCopy'),
        ('tableDigital'       ,'tableDigital'),
        ('tableHardCopy'      ,'tableHardCopy'),
        ('videoDigital'       ,'videoDigital'),
        ('videoHardCopy'      ,'videoHardCopy'),
    )

    presentationForm = models.CharField(max_length = 32, choices = PRESENTATIONFORMCODES, blank = True, null = True)
    series = models.ManyToManyField(CI_Series, related_name = 'series', blank = True, null = True)
    otherCitationDetails = models.TextField(blank = True, null = True)
    collectiveTitle = models.CharField(max_length = 200, blank = True, null = True)
    ISBN = models.CharField(max_length = 200, blank = True, null = True)
    ISSN = models.CharField(max_length = 200, blank = True, null = True)
    def __unicode__(self):
        return self.title

class ApplicationDomain(models.Model):
    applicationDomain = models.CharField(max_length = 200)
    def __unicode__(self):
       return self.applicationDomain

class GVQ_UserInformation(models.Model):
    userDetails = models.ForeignKey(CI_ResponsibleParty, related_name = 'userDetails')
    expertiseLevel = models.IntegerField()
    userRole = models.ManyToManyField(GVQ_UserRoleCode, related_name = 'userRole')
    externalUserID = models.ManyToManyField(MD_Identifier, related_name = 'externalUserID', null = True, blank = True)
    applicationDomain = models.ManyToManyField(ApplicationDomain,  related_name ='applicationDomains',null = True, blank = True)
    def __unicode__(self):
        return "userInfo"

class GVQ_DataFocus(models.Model):
    extent = models.TextField()
    otherFocus = models.CharField(max_length = 50, blank=True)
    def __unicode__(self):
        return self.extent

class GVQ_FeedbackTarget(models.Model):
    resourceRef = models.ManyToManyField(MD_Identifier, related_name = 'resourceRef')
    SCOPE_CODE =(
        ('attribute' , 'attribute'),
        ('activity'  , 'activity'),
        ('document', 'document'),
        ('metadataDocument','metadataDocument'),
        ('attributeType', 'attributeType'),
        ('collectionHardware', 'collectionHardware'),
        ('collectionSession', 'collectionSession'),
        ('dataset', 'dataset'),
        ('series', 'series'),
        ('nonGeographicDataset', 'nonGeographicDataset'),
        ('dimensionGroup', 'dimensionGroup'),
        ('feature', 'feature'),
        ('featureType', 'featureType'),
        ('propertyType', 'propertyType'),
        ('fieldSession', 'fieldSession'),
        ('software', 'software'),
        ('service', 'service'),
        ('model', 'model'),
        ('title', 'title'),
    )
    dataFocus = models.ManyToManyField(GVQ_DataFocus, related_name = 'dataFocus', null = True, blank = True)
    natureOfTarget = models.CharField(max_length = 32, choices = SCOPE_CODE, null = True, blank = True)
    parent = models.ForeignKey('self', null = True, blank = True)

    def __unicode__(self):
        return "resourceRefSet"


class GVQ_Publication(CI_Citation):
    DOI = models.CharField(max_length = 250, blank = True, null = True)
    volume = models.IntegerField(null = True, blank = True)
    issue = models.CharField(max_length = 250, blank = True, null = True)
    pages = models.CharField(max_length = 250, blank = True, null = True)
    relatedResource = models.ManyToManyField(MD_Identifier, related_name = 'relatedResource', blank = True, null = True)
    scope = models.TextField(blank = True, null=True)
    onlineResource = models.ManyToManyField(CI_OnlineResource, related_name = 'onlineResource', blank = True, null = True)
    #title = models.CharField(max_length = 250)
    #date = models.DateField()
    PUBLICATION_PURPOSE = (
        ('compare', 'compare'),
        ('derive', 'derive'),
        ('describe', 'describe'),
        ('evaluate', 'evaluate'),
    )
    purpose = models.CharField(max_length = 15, choices = PUBLICATION_PURPOSE, blank = True, null = True)
    PUBLICATION_CATEGORY = (
        ('bookChapter', 'bookChapter'),
        ('book','book'),
        ('report', 'report'),
        ('journalArticle', 'journalArticle'),
        ('magazineNewspaper', 'magazineNewspaper'),
        ('atlasPaperMap', 'atlasPaperMap'),
        ('applicationProgram', 'applicationProgram'),
        ('conferenceProceedings','conferenceProceedings'),
        ('cdDvd', 'cdDvd'),
        ('blogWiki', 'blogWiki'),
        ('webSite', 'webSite'),
        ('webPage', 'webPage'),
        ('onlineVideo', 'onlineVideo'),

    )
    category = models.CharField(max_length = 30, choices = PUBLICATION_CATEGORY)
    target = models.ManyToManyField(MD_Identifier, related_name = 'pub_target')

class GVQ_DiscoveredIssue(models.Model):
    target = models.ManyToManyField(MD_Identifier, related_name = 'target')
    knownProblem = models.TextField()
    workAround = models.TextField(blank = True, null = True)
    alternativeDataset = models.TextField(blank=True, null=True) #MD_DataIdentification xml field
    referenceDoc = models.ManyToManyField(GVQ_Publication, related_name = 'referenceDoc', blank = True, null = True)
    fixedResource = models.ManyToManyField(MD_Identifier, related_name = 'fixedResource', blank = True, null = True)
    expectedFix = models.ForeignKey(CI_Date, related_name = 'expectedFix', null = True, blank = True)


class GVQ_UsageReport(models.Model):
    usageDescription = models.TextField()
    discoveredIssue = models.ManyToManyField(GVQ_DiscoveredIssue, related_name = 'discoveredIssue', blank = True, null = True)
    REPORTASPECT_CODE = (
        ('Usage', 'Usage'),
        ('Problem', 'Problem'),
        ('FitnessForPurpose', 'FitnessForPurpose'),
        ('Alternatives', 'Alternatives'),
    )
    reportAspect = models.CharField(max_length = 30, choices = REPORTASPECT_CODE, blank = True, null = True)

class GVQ_FeedbackItem(models.Model):
    identifier = models.OneToOneField(MD_Identifier, related_name = 'identifier')
    subject = models.CharField(max_length = 50, blank = False)
    primaryTarget = models.ManyToManyField(GVQ_FeedbackTarget, related_name = 'primaryTarget')
    secondaryTarget = models.ManyToManyField(GVQ_FeedbackTarget, related_name = 'secondaryTarget', blank = True, null = True)
    supplementaryTarget = models.ManyToManyField(GVQ_FeedbackTarget, related_name = 'supplementaryTarget', blank = True, null = True)
    dateStamp = models.DateTimeField('date submitted')
    userRole = models.ForeignKey(GVQ_UserRoleCode, related_name = 'userItemRole')
    user = models.ForeignKey(GVQ_UserInformation, related_name = 'user')

    externalFeedback = models.ManyToManyField(CI_OnlineResource, related_name = 'externalFeedback', blank = True, null = True)
    #UserComment and mime-type belong together. Originally mime-type is always text/plain at this moment.
    userComment = models.TextField(blank = True, null = True)
    usage = models.ManyToManyField(GVQ_UsageReport,related_name = 'usage', blank = True, null = True)

    qualityOverride = models.TextField(blank = True, null = True)
    citation = models.ManyToManyField(GVQ_Publication, related_name = 'citation', blank = True, null = True)

    reply_to = models.ManyToManyField(MD_Identifier, null = True, blank = True, related_name = 'reply_to')
    tags = models.ManyToManyField(Tags, null = True, blank = True)
    domainURN = models.ManyToManyField(DomainURN, null = True, blank = True)

    def __unicode__(self):
        return self.subject

class GVQ_Rating(models.Model):
    item = models.ForeignKey(GVQ_FeedbackItem)
    score = models.IntegerField()
    justification = models.TextField()

    def __unicode__(self):
        return "number"

class CharacterString(models.Model):

    string = models.TextField()
    citationAlternateTitle = models.ForeignKey(CI_Citation)

    def __unicode__(self):
        return self.string
