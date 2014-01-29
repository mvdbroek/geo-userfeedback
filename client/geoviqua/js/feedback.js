$(document).ready(function () {
  try {
    var target = getUrlVar('target_code')
    if (typeof target === 'undefined') {
      throw ("primary target not specified in the URL");
    }
    var targetcodespace = getUrlVar('target_codespace');
    if (typeof targetcodespace === 'undefined') {
      throw ("target codeSpace is not specified in the URL");
    }
    var sourcePage = getUrlVar('source_page')
    var targetArray = target.split(",");
    $('#primaryTargetCode').val(targetArray[0]);
    var targetCSpaceArray = targetcodespace.split(",");
    $('#primaryTargetCodeSpace').val(targetCSpaceArray[0]);

    for (var i = 1; i < targetArray.length; i += 1) {
      ($("#targetList").append(createTarget(targetArray[i], targetCSpaceArray[i])));
    }
  }
  catch (err) {
    $('<div>No target is found: ' + err + '</div>').dialog(
      { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
     );
  }

  var natureOfTarget = getUrlVar('natureOfTarget');
  if (typeof natureOfTarget === 'undefined') {
    //The user can specify the natureOfTarget manually. This can result in multiple targets
    //per dataset reference.
    $('#natureOfTarget').removeAttr('disabled')
  }
  else {
    testmap = $.map(document.getElementById('natureOfTarget').options, function (option) { return option.value; })
    if ($.inArray(natureOfTarget, testmap) != -1) {
      $('#natureOfTarget').val(natureOfTarget);
    }
    else { $('#natureOfTarget').removeAttr('disabled') }
  }


  //Create and attach a widget for adding/removing input fields.
  attachTextFields("#manyTags");
  attachTextFields("#manyDomains");
  attachTextFields("#manyApplications");
  attachTextFields("#manyUserApplications");

  attachDivElement($("#manyExternals"), createExternalFeedbackElement(), "Online Resource");

  attachDivElement($("#manyCitations"), createPublicationElement(), "Publication");
  attachDivElement($("#manyFocus"), createFocusElement(), "Data Focus");
  attachDivElement($("#manyUsageReports"), createUsageElement(), "Usage report")

  $(function () {
    $("#wizard").smartWizard({ enableFinishButton: true,  keyNavigation: false, labelFinish: "Submit","onLeaveStep": validateFields, "onFinish": sendFeedback, transitionEffect: 'none' });
  });

  $(function () {
    $('#star').raty({ starOn: 'other/js/img/star-on.png', starOff: 'other/js/img/star-off.png' });
  });
});

var validateFields = function(obj) {
  var step_num = obj.attr('rel');
  return validateSteps(step_num);

}


function validateSteps(stepNumber){
  if (stepNumber == 1){
    if (document.getElementById("subject").value === '') {
      $('<div>Please fill in the "Subject" field</div>').dialog(
      { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
      );
      return false;
    }
    if ($('#star').raty('score') != undefined) {
      if (document.getElementById("justification").value == '') {
        $('<div>Please provide a justification with the rating</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
    }
    return true;
  }
  if (stepNumber == 2){
    return true;
  }
  if (stepNumber ==3){
    return true;
  }
  if (stepNumber == 4){
     //Validation for CI_OnlineResource, linkage is required.
    var linkageElements = $("#externalElementList").find("[data-name=linkage]");
    for (var i = 0; i < linkageElements.length; i += 1) {
      if ($(linkageElements[i]).val() == ""){
         $('<div>Please fill in the linkage elements for all online references</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
    }
    var title = $("#step-4").find("[data-name=publication]");
    for (var i = 0; i < title.length; i += 1) {
      if ($(title[i]).find("[data-name=title]").val() == "") {
         $('<div>Please fill in the title and date for all online publications / reference documentation</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
      if ($(title[i]).find("[data-name=date]").val() == ""){
         $('<div>Please fill in the title and date for all online publications / reference documentation</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
    }

    var codes = $("#step-4").find("[data-name=code]");
    for (var i = 0; i < codes.length; i += 1) {
      if ($(codes[i]).val() == ""){
         $('<div>Please fill in the code and codespace for all targets</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
    }

    var usage = $("#step-4").find("[data-name=usageDescription]");
    for (var i = 0; i < usage.length; i += 1) {
      if ($(usage[i]).val() == ""){
         $('<div>Please fill in the usage description for all usage reports</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
    }


    var known = $("#step-4").find("[data-name=knownProblem]");
    for (var i = 0; i < known.length; i += 1) {
      if ($(known[i]).val() == ""){
         $('<div>Please fill in the Known Problem for all discovered issues.</div>').dialog(
          { modal: true, buttons: { Ok: function () { $(this).dialog("close"); } } }
        );
        return false;
      }
    }

    return true;
  }
}

function validateAllSteps()
{
  return ((validateSteps(1)) && (validateSteps(2)) && validateSteps(3) && validateSteps(4));
}

var sendFeedback = function (e) {

  if (!validateAllSteps()){
    return;
  }

  //Create the object with initial data and functions to get the information in the form.
  var today = new Date();
  var formObject =
  {
    //Main data element.
    formdata:
    {
      "dateStamp": { "DateTime": today.toISOString() },
      "subject": document.getElementById("subject").value,
      "userRole": { "GVQ_UserRoleCode": document.getElementById("userRole").value },
    },

    appendComment: function () {
      if ($("#userComment").val() !== ""){
        this.formdata.userComment = { "comment": $("#userComment").val(), "mime-type": "text/plain" };
      }
    },

    appendUserInformation:  function() {
        if ($("#username").val() !== ""){
            var user = {};
            userdetails = {"individualName" : { "CharacterString" : $("#username").val()},
                                           "organisationName" : { "CharacterString" : $("#organisation").val()},
                                           "positionName" : { "CharacterString" : $("#position").val()},
                                           "role": { "CI_RoleCode" : $("#ciRole").val()}
                          };

            var manyApps = $.map($("#manyUserApplications").find("input:text"), function (item, index) { return $(item).val() });
            if (manyApps.length > 0 && manyApps[0] !== ""){
                user["applicationDomain"] = manyApps;
            }

            user["userDetails"] = userdetails;
            user["expertiseLevel"] = $("#expertiseLevel").val();
            user["userRole"] = {"GVQ_UserRoleCode": $("#genUserRole").val()};
            this.formdata.user = user;
        }
        else {
            this.formdata.user =  "/api/v1/feedback/userinformation/" + $("input:hidden[id=userId]").val() + "/";
        }
    },

    appendPrimaryTarget: function () {
      var manyFocus = $("#focusElementList").find("div[data-name=focus]");
      var focusList = [];
      for (var i = 0; i < manyFocus.length ; i++) {
        var xml = ""
        xml = createExtentFromInput($(manyFocus[i]).find("input[data-name=north]").val(), $(manyFocus[i]).find("input[data-name=east]").val(),
                            $(manyFocus[i]).find("input[data-name=west]").val(), $(manyFocus[i]).find("input[data-name=south]").val(),
                            $(manyFocus[i]).find("input[data-name=beginDate]").val(), $(manyFocus[i]).find("input[data-name=endDate]").val());
        focus = { "extent": xml, "otherFocus": $(manyFocus[i]).find("textarea[data-name=otherFocus]").val() }
        focusList.push(focus);
      }
      var primaryTarget =
      [{
        "resourceRef": [{"MD_Identifier" :{

          "code": { "CharacterString": $('#primaryTargetCode').val() },
          "codeSpace": { "CharacterString": $('#primaryTargetCodeSpace').val() }
        }}]
      }]
      var manyTargets = $("#targetList").find("ul[data-name=primaryTarget]");
      for (var i = 0; i < manyTargets.length; i += 1) {
         primaryTarget.push({"resourceRef": { "MD_Identifier" : {"code" : {"CharacterString" : $(manyTargets[i]).find("input[data-name=targetcode]").val()},
                                                  "codeSpace" : {"CharacterString" : $(manyTargets[i]).find("input[data-name=targetcodespace]").val()}}}})
      }
      if (focusList.length > 0) {
        primaryTarget[0].dataFocus = focusList;
      }
      if ($("#natureOfTarget").val() !== ''){
        primaryTarget[0].natureOfTarget =  { "MD_ScopeCode": $("#natureOfTarget").val() };
      }
      this.formdata.primaryTarget = primaryTarget;
    },

    appendRating: function () {
      if ($('#star').raty('score') != undefined) {
        if (document.getElementById("justification").value == '') {
          throw ("Please provide a justification for the provided score");
        }
        this.formdata.rating = [{ "justification": document.getElementById("justification").value, "score": $('#star').raty('score') }];
      }
    },

    appendCitation: function () {
      var manyCitations = $("#citationElementList").find("div[data-name=publication]");
      var publicationlist = [];
      for (var i = 0; i < manyCitations.length ; i += 1) {
        var citation = {};
        var publInputFields = $($(manyCitations[i]).find(":input")).serializeArray();
        $.each(publInputFields, function (i, field) {
          if (field.name === "volume" && field.value !==''){
              citation[field.name] = {"Integer" : field.value};
          }
          else if( field.name === "title" | field.name === "DOI" | field.name === "issue" | field.name === "pages"){
            if (field.value !== ''){
              citation[field.name] = {"CharacterString" : field.value}
            };
          }
        });
        var citationDate = $(manyCitations[i]).find("[data-name=date]");
        if (citationDate.val() !== '') {
          citation["date"] = [{ "date": {"Date" : citationDate.val()}, "dateType": {"CI_DateTypeCode" : $(manyCitations[i]).find("[data-name=dateType] :selected").val() }}];
        }
        citation["purpose"] = {"GVQ_PublicationPurposeCode" : $(manyCitations[i]).find("[data-name=purpose] :selected").val()};
        citation["category"] = {"GVQ_PublicationCategoryCode" : $(manyCitations[i]).find("[data-name=category] :selected").val()};
        citation["target"] = [{ "MD_Identifier" : {"code" : {"CharacterString" : $(manyCitations[i]).find("[data-name=code]").val()},
                                                  "codeSpace" : {"CharacterString" : $(manyCitations[i]).find("[data-name=codespace]").val()}}}];
        if (!($.isEmptyObject(citation))) {
          publicationlist.push(citation);
        }
      }
      if (publicationlist.length > 0) {
        this.formdata.citation = publicationlist;
      }
    },

    appendDomain: function () {
      var manyDomains = $.map($("#manyDomains").find("input:text"), function (item, index) { return $(item).val() });
      if (manyDomains.length > 0 && manyDomains[0] !== ""){
        this.formdata.domainURN = manyDomains;
      }
    },

    appendTags: function () {
      var manyTags = $.map($("#manyTags").find("input:text"), function (item, index) { return $(item).val() });
      if (manyTags[0] !== '') {
        this.formdata.tags = manyTags.join();
      }
    },

    appendExternalFeedback: function () {
      var externalElements = $("#externalElementList").find("div[data-name=onlineResource]");
      var externalList = [];
      for (var i = 0; i < externalElements.length; i += 1) {
        var onlineResource = {};
        var onlineInputFields = $($(externalElements[i]).find(":input")).serializeArray();
        $.each(onlineInputFields, function (i, field) {
          if (field.name === "linkage"){
            onlineResource[field.name] = {"URL" : field.value}
          }
          else {
            onlineResource[field.name] = {"CharacterString" : field.value};
          }
        });
        onlineResource["function"] = {"CI_OnLineFunctionCode": $(externalElements[i]).find("[data-name=function] :selected").val()};
        if (!($.isEmptyObject(onlineResource))) {
          externalList.push(onlineResource);
        }
      }
      if (externalList.length > 0) {
        this.formdata.externalFeedback = externalList;
      }

    },

    appendSecondaryTarget: function () {
    },

    appendSupplementaryTarget: function () {
    },
    appendReplyTo: function () {
    },

    appendUsage: function () {
      var usageElements  = $("#manyUsageReports").find("div[data-name=usageReport]");
      var usageList = [];
      for (var i = 0; i < usageElements.length; i +=1){
        var usageReport = {};
        usageReport["reportAspect"] = {"GVQ_ReportAspectCode" : $(usageElements[i]).find("[data-name=reportAspectCode] :selected").val()};
        usageReport["usageDescription"] = $(usageElements[i]).find("[data-name= usageDescription]").val();
        var discoveredIssues = $(usageElements[i]).find("div[data-name= issue]");
        var issueList = [];
        for (var j = 0; j < discoveredIssues.length; j +=1){
          var discoveredIssue = {};
          discoveredIssue["knownProblem"] = {"CharacterString" : $(discoveredIssues[j]).find("[data-name=knownProblem]").val()};
          discoveredIssue["workAround"] = {"CharacterString" : $(discoveredIssues[j]).find("[data-name=workAround]").val()};
          discoveredIssue["target"] = [{"MD_Identifier" :{"code" : {"CharacterString" : $(discoveredIssues[j]).find("[data-name=code]").val()},
                                                  "codeSpace" : {"CharacterString" : $(discoveredIssues[j]).find("[data-name=codespace]").val()}}}];

          var referenceDocs = $(discoveredIssues[j]).find("div[data-name=publication]");
          var referenceList = []
          for (var k = 0; k < referenceDocs.length; k += 1){
            var referenceDoc = {};
            var publInputFields = $($(referenceDocs[k]).find(":input")).serializeArray();
            $.each(publInputFields, function (i, field) {
              if (field.name === "volume" && field.value !==''){
                  referenceDoc[field.name] = {"Integer" : field.value};
              }
              else if( field.name === "title" | field.name === "DOI" | field.name === "issue" | field.name === "pages"){
                if (field.value !== ''){
                  referenceDoc[field.name] = {"CharacterString" : field.value}
                };
              }
            });
            var citationDate = $(referenceDocs[k]).find("[data-name=date]");
            if (citationDate.val() !== '') {
              referenceDoc["date"] = [{ "date": {"Date" : citationDate.val()}, "dateType": {"CI_DateTypeCode" : $(referenceDocs[k]).find("[data-name=dateType] :selected").val() }}];
            }
            referenceDoc["purpose"] = {"GVQ_PublicationPurposeCode" : $(referenceDocs[k]).find("[data-name=purpose] :selected").val()};
            referenceDoc["category"] = {"GVQ_PublicationCategoryCode" : $(referenceDocs[k]).find("[data-name=category] :selected").val()};
            referenceDoc["target"] = [{ "MD_Identifier" :{"code" : {"CharacterString" : $(referenceDocs[k]).find("[data-name=code]").val()},
                                                      "codeSpace" : {"CharacterString" : $(referenceDocs[k]).find("[data-name=codespace]").val()}}}];

            if (!($.isEmptyObject(referenceDoc))){
              referenceList.push(referenceDoc);
            }
          }
          if (referenceList.length > 0){
            discoveredIssue["referenceDoc"] = referenceList;
          }
          //fixedResource(MD_Identifier)
          issueList.push(discoveredIssue);
        }
        if (issueList.length > 0){
          usageReport["discoveredIssue"] = issueList;
        }
        if (!($.isEmptyObject(usageReport))) {
          usageList.push(usageReport);
        }
      }
      if (usageList.length > 0){
        this.formdata.usage = usageList;
      }
    },

    appendQualityOverride: function () {
    },

  };//Form object functions and initial values created.

  //Create the object.
  try {
    formObject.appendComment();
    formObject.appendPrimaryTarget();
    formObject.appendRating();
    formObject.appendCitation();
    formObject.appendUserInformation();
    formObject.appendDomain();
    formObject.appendTags();
    formObject.appendExternalFeedback();
    formObject.appendSecondaryTarget();
    formObject.appendSupplementaryTarget();
    formObject.appendReplyTo();
    formObject.appendUsage();
    formObject.appendQualityOverride();
  }
  catch (err) {
    alert("Error: " + err);
    return
  }
  post(JSON.stringify(formObject.formdata))
};

var post = function (data) {

  var xhr = new XMLHttpRequest();
  xhr.open("post", getPostURL(), 'true');
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  // send the collected data as JSON/
  xhr.send(data);

  xhr.onloadend = function () {
    if (xhr.status == 201){
        var location = xhr.getResponseHeader("Location");
      $('<div>Feedback item created: <br><a href="'+ getServerName() + location.slice(location.indexOf("api")) +'"><b>Feedback item</b></a></div>').dialog(
        { modal: true,
            buttons: {
              Ok: function () { $(this).dialog("close");
                                //Refresh the page.
                                history.go(0);
                              },
            "Go back": function (){ $(this).dialog("close");
                                    history.go(-1);
                                  }

            }
        }
        );
    }
    else {
      $('<div>Server response: ' + xhr.responseText + ' ' + xhr.statusText + ' (' + xhr.status + ')</div>').dialog(
        { modal: true,
            buttons: {
                Ok: function () { $(this).dialog("close");
                                },
                "Go back": function (){ $(this).dialog("close");
                                        history.go(-1);
                                      }
            }
        }
        );
    }
  }
}


// button click-event handler for first button in ul(unordered list) met id 'many'
function attachTextFields(id) {
  $(id).find("input:button").first().val("+")
    .click(function () {
      $("<li/>").append($("<div class='form-horizontal'/>").append($("<input class='span3' type='text'/>"))
        .append($("<input type='button' class='btn'/>").val("-")
          .click(function () {
            $(this).parent().remove();
          })))
        .appendTo($(id));
    });
};

function attachDivElement(parent, listElement, title) {
  parent.find("input:button").first().val("+")
    .click(function () {
      var listElementClone = listElement.clone();

      $("<li><label >" + title + "</label></li>")
      .append($("<input type='button' class='btn btn-small' />").val("remove")
        .click(function () {
          $(this).parent().remove();
        })
      )
      .append($("<input type='button' class='btn btn-small' />").val("collapse")
        .click(function () {
          listElementClone.slideToggle(function () {
            $(this).val((listElementClone.is(':visible')) ? "collapse" : "expand")
          }.bind(this));
        })
      )
      .append(listElementClone)
      .appendTo(parent.children("ul"));

      // nested expansion
      var expandable = listElementClone.find("div[data-factory]");
      $.each(expandable, function (i, item) {
        var element = $(item);
        attachDivElement(element, window[element.data("factory")](), element.data("title"));
      });

      addDateTimePickers();

      listElementClone.find("input:file").filestyle();
    });
};

function addDateTimePickers() {
  $("#full_form").find("[data-class=datepicker]").datepicker({ dateFormat: 'yy-mm-dd' });
  $("#full_form").find("[data-class=timepicker]").timepicker({ controlType: 'select', timeFormat: 'hh:mm:ss', dateFormat: 'yy-mm-dd' });
  $("#full_form").find("[data-class=datetimepicker]").datetimepicker({ controlType: 'select', timeFormat: "hh:mm:ss", dateFormat: "yy-mm-dd" ,separator: 'T'});
}

function createExternalFeedbackElement() {
  return $(
    "<div data-name='onlineResource'>" +
      "<p><label>Linkage:</label><input type='url' name='linkage' data-name='linkage'>" +
        "<span class='help-block'>Put here a link e.g.: http://www.link.com</span>" +
      "</p>" +
      "<p><label>Protocol:</label><input type='text' name='protocol' data-name='protocol'></p>" +
      "<p><label>Application Profile:</label><input type='text' name='applicationProfile' data-name='applicationProfile'></p>" +
      "<p><label>Name:</label><input type='text' name='name' data-name='name'></p>" +
      "<p><label>Description:</label><input type='text' name='description' data-name='description'></p>" +
      "<p><label>Online Function:</label>" +
        "<select name='function' data-name='function'>" +
          "<option value='download'>download</option>" +
          "<option value='information'>information</option>" +
          "<option value='offlineAccess'>offlineAccess</option>" +
          "<option value='search'>search</option>" +
        "</select>" +
      "</p>" +
    "</div>"
  );
}

function createUsageElement() {
  return $(
    "<div data-name='usageReport'>" +
      "<p>" +
        "<label>Report Aspect Code:</label>" +
        "<select data-name='reportAspectCode'>" +
          "<option value='Usage'>Usage</option>" +
          "<option value='Problem'>Problem</option>" +
          "<option value='FitnessForPurpose'>Fitness for Purpose</option>" +
          "<option value='Alternatives'>Alternatives</option>" +
        "</select>" +
      "</p>" +
      "<p><label>Usage Description: </label><textarea data-name='usageDescription' name='usageDescription' maxlength='1000' class='span5' rows=6></textarea></p>" +
      "<div data-name='manyIssues' data-title='Discovered Issue' data-factory='createDiscoveredItem' ><p><label><input type='button' class='btn btn-small' /> Add Discovered Issue</label></p>" +
        "<ul data-name='issue'></ul>" +
      "</div>" +
    "</div>"
  );
}

function createCIDateElement() {
  return $(
    "<ul>" +
      "<li>Date:</li><input type='text' data-name='date' data-class='datepicker'>" +
      "<li>" +
        "<label>DateType:</label>" +
        "<select data-name='dateType'>" +
          "<option value='creation'>Creation</option>" +
          "<option value='publication'>Publication</option>" +
          "<option value='revision'>Revision</option>" +
        "</select>" +
      "</li>" +
    "</ul>"
  );
}

function createPublicationElement() {
  return $(
    "<div data-name='publication'>" +
      "<p><label>Title:</label><input type='text' name='title'></p>" +
      "<p><label>Doi:</label><input type='text' name='DOI'></p>" +
      "<p><label>Volume:</label><input type='number' name='volume'></p>" +
      "<p><label>Issue:</label><input type='text' name='issue'></p>" +
      "<p><label>Pages:</label><input type='text' name='pages'></p>" +
      "<p><label>Date:</label></p>" +
    "</div>"
  )
  .append(createCIDateElement())
  .append(
    "<p><label>Purpose:</label>" +
      "<select data-name='purpose'>" +
        "<option value='compare'>compare</option>" +
        "<option value='derive'>derive</option>" +
        "<option value='describe'>describe</option>" +
        "<option value='evaluate'>evaluate</option>" +
      "</select>" +
    "</p>" +
    "<p><label>Category:</label>" +
      "<select data-name='category'>" +
        "<option value='book'>book</option>" +
        "<option value='bookChapter'>book chapter</option>" +
        "<option value='report'>report</option>" +
        "<option value='journalArticle'>journal/article</option>" +
        "<option value='magazineNewsPaper'>magazine/newspaper</option>" +
        "<option value='atlasPaperMap'>atlas/paper map</option>" +
        "<option value='applicationProgram'>application program</option>" +
        "<option value='conferenceProceedings'>conference proceedings</option>" +
        "<option value='cdDvd'>cd/dvd</option>" +
        "<option value='blogWiki'>blog wiki</option>" +
        "<option value='webPage'>webpage</option>" +
        "<option value='webSite'>website</option>" +
        "<option value='onlineVideo'>online video</option>" +
      "</select>" +
    "</p>" +
    "<p><label>Target:</label></p>"
  )
  .append(createMDIdentifier)
}

function createMDIdentifier() {
  return $(
    "<ul data-name='md_identifier'>"+
      "<li><p><label>Code: </label><input type='text' data-name='code' name='code'></p></li>"+
      "<li><p><label>Codespace: </label><input type='text' data-name='codespace' name='codespace'></p></li>"+
    "</ul>")
}


function createDiscoveredItem() {
  return $(
    "<div data-name='issue'>" +
      "<p><label>Known Problem: </label><textarea data-name='knownProblem' name='knownProblem' maxlength='1000' class='span5' rows=6 /></textarea></p>" +
      "<p><label>Workaround: </label><textarea data-name='workAround' name='usageDescription' maxlength='1000' class='span5' rows=6/></textarea></p>" +
    "</div>"
  )
  .append(
  "<p><label>Target:</label></p>"
  )
  .append(createMDIdentifier)
  .append(
    "<div data-name='manyReferences' data-title='Reference Documentation' data-factory='createPublicationElement' ><p><label><input type='button' class='btn btn-small' /> Add Reference Documentation</label></p>" +
      "<ul data-name='referenceDoc'></ul>" +
    "</div>"
  );
}

function createReferenceDocumentation() {
  return $("<p><label></label></p>");
}

function createTarget(targetcode, targetcodespace) {
    return $(
             "<ul data-name='primaryTarget'>"+
             "<li><p><label >Target code</label><input data-name = 'targetcode' name='sprimaryTargetCode' value='" +targetcode +"' readonly='true'/></p>"+
             "<p><label >Target codespace</label><input data-name = 'targetcodespace' name='sprimaryTargetCodespace' value='" + targetcodespace+"' readonly='true'/></p></li>"+
             "</ul>");
}
function createFocusElement() {
  return $(
    "<div data-name='focus'class='offset0'><p><p><label>BoundingBox:</label></p>" +
      "<p><input data-name='north' name='north' type='number' min='-90.0' max='90.0' value='90' required ><label class='span1'>North</label></p>" +
      "<p><input data-name='south' name='south' type='number' min='-90.0' max='90.0' value='-90'required ><label class='span1'>South</label></p>" +
      "<p><input data-name='east' name='east' type='number' min='-180.0' max='180.0' value='-180'required ><label class='span1'>East</label></p>" +
      "<p><input data-name='west' name='west' type='number' min='-180.0' max='180.0' value='180'required ><label class='span1'>West</label></p>" +
      "<p></p>" +
      "<p><label>Time Period:</label></p>" +
      "<p><input data-class='datetimepicker' data-name='beginDate' name='beginDate' type='text' required ><label class='span1'>Start</label></p>" +
      "<p><input data-class='datetimepicker' data-name='endDate' name='endDate' type='text' required><label class='span1'>End</label></p>" +
      "<p><label>Other Focus: </label><textarea data-name='otherFocus' name='otherFocus' maxlength='1000' class='span5' val='' rows=6></textarea></p>" +
    "</div>"
  );
}

function createExtentFromInput(north, east, west, south, begintime, endtime) {
  return (
    "<gmd:EX_SpatialTemporalExtent>" +
      "<gmd:extent>" +
        "<gml:TimePeriod gml:id='ID'>" +
          "<gml:beginPosition>" + begintime + "</gml:beginPosition>" +
          "<gml:endPosition>" + endtime + "</gml:endPosition>" +
        "</gml:TimePeriod>" +
      "</gmd:extent>" +
      "<gmd:spatialExtent>" +
        "<gmd:EX_GeographicBoundingBox>" +
          "<gmd:westBoundLongitude>" +
            "<gco:Decimal>" + west + "</gco:Decimal>" +
          "</gmd:westBoundLongitude>" +
          "<gmd:eastBoundLongitude>" +
            "<gco:Decimal>" + east + "</gco:Decimal>" +
          "</gmd:eastBoundLongitude>" +
          "<gmd:southBoundLatitude>" +
            "<gco:Decimal>" + south + "</gco:Decimal>" +
          "</gmd:southBoundLatitude>" +
          "<gmd:northBoundLatitude>" +
            "<gco:Decimal>" + north + "</gco:Decimal>" +
          "</gmd:northBoundLatitude>" +
        "</gmd:EX_GeographicBoundingBox>" +
      "</gmd:spatialExtent>" +
    "</gmd:EX_SpatialTemporalExtent>"
  );
}

function getUrlVars() {
  var vars = [], hash;
  var hashes = decodeURIComponent(window.location.href.slice(window.location.href.indexOf('?') + 1)).split('&');
  for (var i = 0; i < hashes.length; i++) {
    hash = hashes[i].split('=');
    vars.push(hash[0]);
    vars[hash[0]] = hash[1];
  }
  return vars;
}

function getUrlVar(name) {
  return getUrlVars()[name];
}