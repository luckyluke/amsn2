// TODO: have info/debug/err functions


// Contact List {{{
function ContactList(_parent)
{
  var groups = {};
  var contacts = {};
  var group_ids = [];
  var parent = _parent;

  parent.update('<p>bite</p><ul><li id="fakegroup" style="display:none"></li></ul>');

  this.setGroups = function(_group_ids){
    console.log("SET GROUPS");
    var prev = $('fakegroup');
    var i, j = 0;

    console.log("group ids = " + _group_ids);
    console.log("length = " + _group_ids.length);

    for (i = group_ids.length - 1; i >= 0; i--) {
      if (_group_ids.indexOf(group_ids[i]) < 0) {
        group_ids.splice(i,1);
        // TODO: remove group
      }
    }

    for (i = 0; i < _group_ids.length; i++) {
      if (group_ids[j] == _group_ids[i]) {
        prev = this.getGroup(_group_ids[i]).getElement();
        j++;
      } else {
        elem = this.getGroup(_group_ids[i]).getElement();
        prev.insert({after: elem});
        prev = elem;
      }
    }
    group_ids = _group_ids;
  }

  this.getContact = function(uid){
    if (contacts[uid] == undefined)
      return null;
    return contacts[uid];
  }

  this.setContact = function(uid, c) {
    contacts[uid] = c;
  }

  this.getGroup = function(uid){
    if (groups[uid] == undefined)
      groups[uid] = new Group(uid);
    return groups[uid];
  }
}

function Group(_gid)
{
  var gid = _gid;
  var contact_ids = [];

  var name = "";

  var elem = new Element('li', {id: 'grp_' + gid,
                         class: 'clGroup'});

  var h;
  h  = '<div id="grp_' + gid + '_hdr"></div>';
  h += '<ul  id="grp_' + gid + '_cts" class="clContacts">';
  h += '<li  id="grp_' + gid + '_fake" style="display:none"></ul>';
  elem.update(h);


  var isCollapsed = false;

  console.log("New group " + gid);

  this.getName = function() {
    return name;
  }

  this.getGid = function() {
    return gid;
  }

  this.setName = function(_name) {
    var hdr  = $('grp_' + gid + '_hdr');
    this.name = _name;
    hdr.update(_name);
  }

  this.setContacts = function(_contact_ids) {
    var prev = $('grp_' + gid + '_fake');
    var i, j = 0;

    for (i = contact_ids.length - 1; i >= 0; i--) {
      if (_contact_ids.indexOf(contact_ids[i]) < 0) {
        contact_ids.splice(i,1);
      }
    }

    for (i = 0; i < _contact_ids.length; i++) {
      if (contact_ids[j] == _contact_ids[i]) {
        prev = this.getContact(_contact_ids[i]).getElement(gid);
        j++;
      } else {
        elem = this.getContact(_contact_ids[i]).getElement(gid);
        prev.insert({after: elem});
        prev = elem;
      }
    }
    contact_ids = _contact_ids;
  }

  this.getContacts = function() {
    return contact_ids;
  }

  this.getElement = function() {
    return elem;
  }

  this.getContact = function(_uid){
    c = contact_list.getContact(_uid);
    if (!c) {
      c = new Contact(gid, _uid);
      contact_list.setContact(_uid, c);
    }
    contact_ids[_uid] = c;
    return c;
  }
}

function Contact(_gid, _uid)
{
  var elem = new Element('li',
                         {id: 'ct_' + _uid + '_' + _gid,
                          class: 'clContact'});

  var elements = {};
  elements[_gid] = elem;

  var name = "";
  var uid = _uid;

  /* FIXME
     element.click(function(){
     $.post('/contactClicked', {uid: uid});
     });
     */

  this.setName = function(_name) {
    name = _name;
    // TODO
    alert(_name);
    for (k in elements) {
      elements[k].update(_name);
    }
  }

  this.getUid = function() {
    return uid;
  }

  this.getName = function() {
    return name;
  }

  this.getElement = function(groupId) {
    if (elements[groupId] == undefined)
      elements[groupId] = elem.clone(true);
    return elements[groupId];
  }
}

// contact_list
var contact_list = null;

function showContactListWindow()
{
  // FIXME
  //$("div.contact_list").show("slow");
}

function hideContactListWindow()
{
  // FIXME
  //$("div.contact_list").hide("slow");
}

function setContactListTitle(title)
{
  // FIXME
  //$("div.contact_list div.title").text(title);
}

function contactListUpdated(groups)
{
  if (contact_list)
    contact_list.setGroups(groups);
}

function groupUpdated(uid, name, contact_ids)
{
  if (contact_list) {
    var group = contact_list.getGroup(uid);
    group.setName(name);
    group.setContacts(contact_ids);
  }
}

function contactUpdated(uid, name)
{
  if (contact_list)
    contact_list.getContact(uid).setName(name);
}
// }}}
// ChatWindow {{{
/*
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
} */ // }}}

// main {{{

var mainWindow = null;

function showMainWindow()
{
  if (!mainWindow) {
    function fixMainWindow() {
      $('mw_minimize').setStyle({left: (mainWindow.getSize()['width'] - 21) + 'px'});
    }

    Event.observe(window, 'resize', fixMainWindow);

    mainWindow = new Window({id: 'mw', className: "win", width: 210, height: (document.viewport.getHeight() - 60), zIndex: 100, resizable: true, draggable: true, closable: false, maximizable: false, detachable: false, minWidth: 205, minHeight: 150, showEffectOptions: {duration: 0}, hideEffectOptions: {duration: 0}});
    mainWindow.setConstraint(true, {left: 0, right: 0, top: 0, bottom: 0});
    fixMainWindow();
    mainWindow.setHTMLContent('<h1>Hello world !!</h1><div id="cl"></div>');
  }
  if (!contact_list) {
    contact_list = new ContactList($('cl'));
  }
  mainWindow.showCenter(false);
  mainWindow.toFront();
}
function hideMainWindow()
{
  mainWindow.hide();
}
function setMainWindowTitle(title)
{
  mainWindow.setTitle(title);
}
function onConnecting(msg)
{
    /* FIXME */
    //$(".message").text(msg);
}
function showLogin()
{
  $('login').show();
}
function hideLogin()
{
  $('login').hide();
} // }}}

function signingIn()
{
  hideLogin();
}

function myInfoUpdated()
{
  // TODO
}

function aMSNStart()
{
  new PeriodicalExecuter(function(pe) {
    //new Ajax.Request('/out', {method: 'get'});
    new Ajax.Request('/out', {method: 'get',
      onException: function(r, e) {//alert(e.name+": "+e.message);
      console.log(e)}
    });
  }, 5);
}

//vim:sw=2:fdm=marker:
