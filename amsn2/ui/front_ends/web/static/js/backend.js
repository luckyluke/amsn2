// Backend functions


// Contact List {{{
function ContactList()
{
    var groups = {};
    var contacts = {};
    var group_ids = [];
    var head=$("<div/>");

    this.setGroups = function(parent, _group_ids){
        var prev = head;
        var i, j = 0;

        console.log("group ids = " + _group_ids);
        console.log("length = " + _group_ids.length);

        if (prev.parent() != parent)
            parent.append(prev);

        for (i = group_ids.length - 1; i >= 0; i--) {
            if (_group_ids.indexOf(group_ids[i]) < 0) {
                group_ids.splice(i,1);
            }
        }

        for (i = 0; i < _group_ids.length; i++) {
            if (group_ids[j] == _group_ids[i]) {
                prev = this.getGroup(_group_ids[i]).getTop();
                j++;
            } else {
                elem = this.getGroup(_group_ids[i]).getTop();
                elem.insertAfter(prev);
                prev = elem;
            }
        }
        group_ids = _group_ids;
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
    var contact_ids = [];

    var name = "";
    var top = $("<div/>");
    var element = $("<div/>");
    var first = $("<div/>");
    var header = $("<div class='groupheader'/>");

    top.append(header);
    top.append(element);
    element.append(first);

    var elementVisible = true;

    console.log("New group " + _uid);
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

    this.setContacts = function(_contact_ids) {
        var prev = first;
        var i, j = 0;

        for (i = contact_ids.length - 1; i >= 0; i--) {
            if (_contact_ids.indexOf(contact_ids[i]) < 0) {
                contact_ids.splice(i,1);
            }
        }

        for (i = 0; i < _contact_ids.length; i++) {
            if (contact_ids[j] == _contact_ids[i]) {
                prev = contactList.getContact(_contact_ids[i]).getElement(uid);
                j++;
            } else {
                elem = contactList.getContact(_contact_ids[i]).getElement(uid);
                elem.insertAfter(prev);
                prev = elem;
            }
        }
        contact_ids = _contact_ids;
        refresh();
    }

    this.getContacts = function() {
        return contact_ids;
    }

    this.getElement = function() {
        return element;
    }

    this.getContact = function(uid){
        if (contacts[uid] == undefined)
            contacts[uid] = new Contact(uid);
        return contacts[uid];
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
        $.post('/contactClicked', {uid: uid});
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

function groupUpdated(uid, name, contact_ids)
{
  var group = contactList.getGroup(uid);
  group.setName(name);
  group.setContacts(contact_ids);
}

function contactUpdated(uid, name)
{
    contactList.getContact(uid).setName(name);
}
// }}}
// ChatWindow {{{
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
            msg = textInput.val();
            textInput.val("");
            $.post('/sendMsg', {uid: uid, msg: msg});
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

// Chat functions
var chatWindows = {};
var chatWidgets = {};

function newChatWindow(uid)
{
    chatWindows[uid] = new ChatWindow(uid);
}

function addChatWidget(windowUid, widgetUid)
{
    chatWindows[windowUid].addChatWidget(chatWidgets[widgetUid]);
}

function showChatWindow(uid)
{
    chatWindows[uid].show();
}

function hideChatWindow(uid)
{
    chatWindows[uid].hide();
}

function newChatWidget(uid)
{
    chatWidgets[uid] = new ChatWidget(uid);
}

function onMessageReceivedChatWidget(uid, msg)
{
    chatWidgets[uid].onMessageReceived(msg);
}

function nudgeChatWidget(uid)
{
    chatWidgets[uid].nudge();
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
function setMainWindowTitle(title)
{
    $(".mainWindow .ui-dialog-title").text(title);
}
function onConnecting(msg)
{
    $(".message").text(msg);
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
} // }}}

function myInfoUpdated()
{
  // TODO
}

function aMSNStart()
{
  $(".mainWindow").dialog({
        position:['left','top'],
        height: '100%',
        width: '400px',
        stack: false
  });
  Listening();
}

function Listening() {
  $.get("/out", function(data){
    setTimeout(Listening, 500);
    //try {
      eval(data);
    //} catch(e) {}
  });
}

// init
$(document).ready(function()
{
        showLogin();
});
