// Backend functions


function ContactList()
{
    var groups = {};
    var contacts = {};
    var group_ids = [];
    var head=$("<div/>");
    this.setGroups = function(parent, _group_ids){
        var prev = head;
        var k, i, j = 0;

        if (prev.parent() != parent)
            parent.append(prev);

        while (group_ids.length && _group_ids.indexOf(group_ids[j]) < 0)
            group_ids.splice(j,1);

        for (i = 0; i < _group_ids.length; i++) {
            if (group_ids[j] == _group_ids[i]) {
                prev = this.getGroup(_group_ids[i]).getTop();
                j++;
                while (group_ids.length && _group_ids.indexOf(group_ids[j]) < 0)
                    group_ids.splice(j, 1);
            } else {
                if ((k = group_ids.indexOf(_group_ids[i])) > -1)
                    group_ids.splice(k, 1);
                elem = this.getGroup(_group_ids[i]).getTop();
                elem.insertAfter(prev);
                prev = elem;
            }
        }
    }
    this.getContact = function(uid){
        if (contacts[uid] == undefined)
            contacts[uid] = new Contact(uid);
        return contacts[uid];
    }
    this.getGroup = function(uid){
        if (groups[uid] == undefined)
            groups[uid] = new Group(uid);
        return groups[uid];
    }
}

function Group(_uid)
{
    var uid = _uid;
    var contacts = [];

    var name = "";
    var top = $("<div/>");
    var element = $("<div/>");
    var first = $("<div/>");
    var header = $("<div class='groupheader'/>");

    top.append(header);
    top.append(element);
    element.append(first);

    var elementVisible = true;

    header.click(function() {
        element.slideToggle("slow");
        elementVisible = !elementVisible;
        refresh();
    });

    function refresh()
    {
        header.text((elementVisible?'-':'+')+' '+name);
    }

    this.getName = function() {
        return name;
    }
    this.getUid = function() {
        return uid;
    }
    this.setName = function(_name) {
        name = _name;
        refresh();
    }
    this.setContacts = function(_contacts) {
        var prev = first;
        var k, i, j = 0;

        while (contacts.length && _contacts.indexOf(contacts[j]) < 0)
            contacts.splice(j,1);

        for (i = 0; i < _contacts.length; i++) {
            if (contacts[j] == _contacts[i]) {
                prev = contacts[i].getElement(uid);
                j++;
                while (contacts.length && contacts.indexOf(contacts[j]) < 0)
                    contacts.splice(j,1);
            } else {
                if ((k = contacts.indexOf(_contacts[i])) > -1)
                    contacts.splice(k, 1);
                elem = _contacts[i].getElement(uid);
                elem.insertAfter(prev);
                prev = elem;
            }
        }
        contacts = _contacts;
        refresh();
    }
    this.getContacts = function() {
        return contacts;
    }
    this.getElement = function() {
        return element;
    }
    this.getTop = function() {
        return top;
    }
    refresh();
}

function Contact(_uid)
{
    var element = $("<li/>");
    var elements = {};
    refresh();

    var name = "";
    var uid = _uid;

    element.click(function(){
                  Send(["contactClicked",uid]);
    });

    this.setName = function(_name) {
        name = _name;
        refresh();
    }

    this.getUid = function() {
        return uid;
    }

    this.getName = function() {
        return name;
    }

    this.getElement = function(groupId) {
        if (elements[groupId] == undefined)
            elements[groupId] = element.clone(true);
        return elements[groupId];
    }

    function refresh() {
        element.text(name);
        $.each(elements, function(groupId, val) {
            try {
                elements[groupId] = element.clone(true);
                val.replaceWith(elements[groupId]);
            } catch(e) {}
        });
    }
}

function ChatWindow(_uid)
{
    var uid = _uid;
    var element = $("<div class='chatWindow'/>");

    var widgets = [];

    $("body").append(element);

    function callScrollers()
    {
        $.each(widgets,  function (i, w) {
            w.scroll();
        });
    }

    element.dialog({
        position:[Math.floor(Math.random()*600), Math.floor(Math.random()*400)],
        title: 'aMSN 2 Conversation',
        resizeStop: callScrollers,
    });

    this.show = function() {
        element.show("slow");
    }

    this.hide = function() {
        element.hide("slow");
    }

    this.shake = function() {
        element.effect('shake', {times:5}, 50);
    }

    this.addChatWidget = function(widget) {
        widgets.push(widget);
        widget.setParent(this);
        element.append(widget.getElement());
    }
}

function ChatWidget(_uid)
{
    var uid = _uid;
    var parent = null;
    var element = $("<div class='chatWidget'/>");
    var conversation = $("<div class='chatWidgetConversation'/>");
    var textInput = $("<textarea class='chatTextInput' contenteditable='true' onload='this.contentDocument.designMode=\"on\"'></textarea>");
    var bottomDiv = $("<div class='chatBottomDiv'/>");
    var reScroll = true;
    var naive = true;

    element.append(conversation);
    bottomDiv.append(textInput);
    element.append(bottomDiv);

    $(textInput).keydown(function(event) {
        if (event.keyCode == 13) {
            text = textInput.val();
            textInput.val("");
            Send(["sendMessage",_uid,text]);
            return false;
        }
    });

    conversation.scroll(function() {
        reScroll = Math.abs(conversation[0].scrollHeight - conversation.scrollTop() - conversation.outerHeight()) < 20;
    });

    this.setParent = function(parent) {
        this.parent = parent;
    }

    this.getElement = function() {
        return element;
    }

    function scrollBottom()
    {
        if(reScroll)
            conversation.animate({
                 scrollTop: conversation[0].scrollHeight
            });
    }
    this.scroll = scrollBottom;

    this.onMessageReceived = function(txt) {
        var msg = $("<div class='chatMessage'/>");
        msg.text(txt);
        // process smilies on msg
        conversation.append(msg);
        msg.show('fast');
        if (reScroll) {
            if (naive) {
                naive = reScroll = false;
                setTimeout(function(){
                    scrollBottom();
                    reScroll = true;
                }, 1000);
            } else {
                scrollBottom();
            }
        }
    }

    this.nudge = function() {
        this.parent.shake();
    }
}

// main
function showMainWindow()
{
    $("div.mainWindow").show("slow");
}
function hideMainWindow()
{
    $("div.mainWindow").hide("slow");
}
function setMainWindowTitle(titleL)
{
    $(".mainWindow .ui-dialog-title").text(titleL.pop());
}
function onConnecting(mesgL)
{
    var mesg = mesgL.pop();
    $(".message").text(mesg);
}
function showLogin()
{
    $("div.login").show("slow");
}
function hideLogin()
{
    $("div.login").hide("slow");
}

function signingIn()
{
    hideLogin();
}

// splash screen
function setImageSplashScreen()
{
    // TODO
}
function setTextSplashScreen(textL)
{
    $("div.splashScreen").text(textL.pop());
}
function showSplashScreen()
{
    $("div.splashScreen").show("slow");
}
function hideSplashScreen()
{
    $("div.splashScreen").hide("slow");
}


function myInfoUpdated()
{
  // TODO
}

// contact_list
var contactList = new ContactList();

function showContactListWindow()
{
    $("div.contact_list").show("slow");
}

function hideContactListWindow()
{
    $("div.contact_list").hide("slow");
}

function setContactListTitle(title)
{
    $("div.contact_list div.title").text(title);
}

function contactListUpdated(groupsL)
{
    contactList.setGroups($("div.contact_list"), groupsL);
}

function groupUpdated(groupV)
{
  var uid = groupV[0];
  var contact_ids = groupV[1];
  var name = groupV[2];
  var group = contactList.getGroup(uid);
  group.setName(name);
  if (contact_ids) {
    var cuids = contact_ids.split(',');
    var clist = [];
    $.each(cuids, function(){
        clist.push(contactList.getContact(cuids.shift()));
    });
    group.setContacts(clist);
  }
}

function contactUpdated(contactV)
{
    var uid = contactV[0];
    var name = contactV[1];
    contactList.getContact(uid).setName(name);
}

// Chat functions
var chatWindows = {};
var chatWidgets = {};

function newChatWindow(uidL)
{
    var uid = uidL.pop();
    chatWindows[uid] = new ChatWindow(uid);
}

function addChatWidget(uidL)
{
    var windowUid = uidL.shift();
    var widgetUid = uidL.shift();
    chatWindows[windowUid].addChatWidget(chatWidgets[widgetUid]);
}

function showChatWindow(uidL)
{
    var uid = uidL.shift();
    chatWindows[uid].show();
}

function hideChatWindow(uidL)
{
    var uid = uidL.shift();
    chatWindows[uid].hide();
}

function newChatWidget(uidL)
{
    var uid = uidL.pop();
    chatWidgets[uid] = new ChatWidget(uid);
}

function onMessageReceivedChatWidget(omrcwL)
{
    var uid = omrcwL.shift();
    var msg = omrcwL.shift();
    chatWidgets[uid].onMessageReceived(msg);
}

function nudgeChatWidget(uidL)
{
    var uid = uidL.shift();
    chatWidgets[uid].nudge();
}

// Comunication functions
/*
var ReqStack = [];
function Send(msg)
{
    ReqStack.push(msg);
}
function Sending()
{
    try {
        if (ReqStack.length) {
            var xhr;
            var ReqSend = [];

            while (ReqStack.length)
                ReqSend.push(ReqStack.shift().join("\t"));

            ReqStack = [];
            (xhr=$.post("amsn2.php", {in:ReqSend.join("\n")},
                        function(data,textStatus){})).onreadystatechange = function() {
                if (xhr.readyState == 4)
                    setTimeout(Sending, 500);
            }
        } else {
            setTimeout(Sending, 500);
        }
    } catch(e) {}
}
*/
function Listening() {
  $.get("/out", function(data){
    setTimeout(Listening, 5000);
    //try {
      eval(data);
    //} catch(e) {}
  });
}

// init
$(document).ready(function()
{
    $(".mainWindow").dialog({
        position:['left','top'],
        height: '100%',
        width: '400px',
        stack: false
    });
    showLogin();
    //Listening();
});
