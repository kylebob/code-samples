/*
Below is some code for ChatWithYourself.com, which is basically a chat room with just you in it.
You can always watch other people talking to themselves or save your chat.
It includes some basic JavaScript as well as some jQuery and AJAX.
*/

$(document).ready(function() {

	var bottomHeight = $('#chatBottom').height(); // height of bottom varies between pages, so it should be stored when the page loads
	var freeScroll = false; // let user see all chat messages by scrolling
	var canSave = false; // user can only save after their chat is long enough when chatting

	//switch to manual scroll on user device input, always manual scroll on saved chats
	if (watching != 2) {
		$('#shouts').bind('scroll mousedown wheel DOMMouseScroll mousewheel keyup touchstart', function(e) {
			if (e.which > 0 || e.type == "mousedown" || e.type == "mousewheel" || e.type == "touchstart") {
				$('#backToBottom').animate({
					height: "64px"
				}, 'fast');
				$('#chatLeft').animate({
					"padding-bottom": ((bottomHeight + 64) + "px")
				}, 'fast');
				freeScroll = true;
			}
		});
	}

	//clicking/touching the down arrows
	$('#backDown').click(function() {
		hideDownArrows();
	});

	//hide arrows to navigate to the bottom, either when the user clicks them or when they manually reach the bottom
	function hideDownArrows() {
		$('#backToBottom').animate({
			height: "0px"
		}, 'fast');
		$('#chatLeft').animate({
			"padding-bottom": (bottomHeight + "px")
		}, 'fast');
		freeScroll = false;
		scrollToBottom();
	}

	//sliding messages up with every new message, so they appear from the bottom
	function scrollToBottom() {
		$('#shouts').animate({
			scrollTop: $('#shoutsWrapper').height()
		}, 'fast');
	}

	//get the messages from the database
	function getshouts() {
		var getShoutsURL = "/getshouts.php?watching=" + watching + "&id=" + id + "&watchid=" + watchID; //get shouts for specific user
		$.ajax({
			url: getShoutsURL,
			context: document.body,
			cache: false,
			dataType: "html",
			success: function(data) {
				$("#shouts").html(data);
				if ((!freeScroll) && (watching != 2)) {
					scrollToBottom(); //move to the bottom of the messages after the newest message loads
				} else if ($('#shouts').scrollTop() >= $('#shoutsWrapper').height()) {
					hideDownArrows();
					freeScroll = false;
				}

				//save if the user's chat is long enough -- just meant to prevent "hi" messages mainly
				if (($('#shoutsWrapper').height() > 200) && (watching === "")) {
					$("#saveChat").removeClass("disabled");
					canSave = true;
				}
			},
			error: function() {
				console.log("Failed to load chat.");
			}
		});
	}

	//get the messages from the database
	function getusers() {
		//get dynamic count of users chatting and watching, but don't show with archived chats
		if (watching != 2) {
			$.ajax({
				url: "/getusers.php?watching=" + watching + "&id=" + id + "&watchid=" + watchID,
				context: document.body,
				cache: false,
				dataType: "html",
				success: function(data) {
					$("#users").html(data);
				},
				error: function() {
					console.log("Failed to load user count.");
				}
			});
		}
	}

	//send a message
	function sendshout() {
		var message = escape($("#shoutText").val());
		if (message.length > 0) { //make sure message is typed
			var shouturl = "/sendshout.php?message=" + message + "&id=" + id; //url to send shout
			$.ajax({ //send shout
				url: shouturl,
				success: function(data) {
					getshouts(); //once the shout is sent, reload the shoutbox
					$("#shoutText").val("");
				},
				error: function() {
					console.log("Failed to send shout.");
				}
			});
		}
	}

	//data for watching a specific chat
	function watchChat() {
		location = "/watch/" + encodeURIComponent($("#chatID").val().value);
		return false;
	}

	//submit chat to insert data into the database
	function submitChat() {
		var title = escape($("#chatName").val());
		if (title.length > 0) //make sure title isn't blank
			document.saveChat.submit();
		else
			console.log("Failed to save chat.");
	}

	//if enter is pressed, send a message
	$("#shoutText").keyup(function(event) {
		if (event.keyCode == 13) sendshout();
	});

	//if send button is pressed, send a message
	$("#shoutButton").click(function(event) {
		sendshout();
	});

	//if enter is pressed, send a message
	$("#chatName").keyup(function(event) {
		if (event.keyCode == 13) submitChat();
	});

	//if send button is pressed, send a message
	$("#submit").click(function(event) {
		submitChat();
	});

	//send to save page if save button is allowed
	$("#saveChat").click(function(event) {
		if (canSave)
			location.href = '/submit.php?id=' + id;
	});

	//send to save page if save button is allowed
	$("#about, #close").click(function(event) {
		$('#aboutDiv').slideToggle("fast");
	});

	getshouts(); //get initial messages
	getusers();

	//run again every second, unless viewing a saved / archived
	if (watching != "2") {
		setInterval(function() {
			getshouts();
		}, 5000);
		setInterval(function() {
			getusers();
		}, 20000);
	}

});