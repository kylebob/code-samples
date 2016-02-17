<?php
/* This script is read after clicking the submit button on the submit.php page.
The text goes through a list of filters and word replacements before it is accepted or rejected. It then notifies the user of the final result in an alert box.
To Do - Update Alerts to AJAX */

//limit submissions to 5 per day to avoid repetitive submissions
function dailyLimit($con)
{
	$ip = $_SERVER['REMOTE_ADDR']; //get user ip
	$querySubmissions = "SELECT * FROM submissions WHERE ip = '$ip' AND DATE(date) = CURDATE()"; //check for ip and date combination
	$submissions = mysqli_query($con, $querySubmissions) or die(mysqli_error($con));

	//if user has not submitted 10 times today, add into the database
	if (mysqli_num_rows($submissions) < 10)
		return $ip;
	else
	{
		echo "<script>alert('You have made too many submissions today! Sorry, but this is done to prevent spamming. Please come back tomorrow to submit your thing. Thanks!')</script><script>history.go(-1)</script>";
		exit;
	}

	return false; //continue if everything is okay
}

//preventing offensive words, added spaces on some to prevent good words from being rejected
function filteredWords($text)
{
	$reason = "None";

	$words = array(' cunt', ' fag', 'fuck', ' nigg', 'randomthings', 'random things to do', 'random thing to do', 'awesome button', 'click awesome', 'press awesome', 'do the next');

	//if thing contains filtered word, reject
	foreach($words as $word)
	{
 		if (strlen(strstr(strtolower($text),$word))>0)
			$reason = "profanity or a forbidden term was detected";
 	}

 	//checking regular expressions for personal data and spam
 	if (preg_match("/[^@\s]*@[^@\s]*\.[^@\s]*/", $text, $matches))
		$reason = "an email address was detected";

	else if (preg_match("#((http|https|ftp)://(\S*?\.\S*?))(\s|\;|\)|\]|\[|\{|\}|,|\"|'|:|\<|$|\.\s)#ie", $text))
		$reason = "a URL was detected";

	else if (preg_match("/(\+?[\d-\(\)\s]{7,}?\d)/", $text, $matches))
		$reason = "a phone number was detected";

	else if (strlen($text) < 5)
		$reason = "the submission was too short";

	if ($reason !== "None")
	{
		echo "<script>alert('Your submission cannot be accepted as it is because " . $reason . ". Please read the rules again and make the necessary changes. Thank you!')</script><script>history.go(-1)</script>";
		exit;
	}

	return false; //continue if everything is okay
}

// CHECK IF VALID URL
function checkURL($text)
{
	$reason = "None";

	if (!preg_match("#((http|https|ftp)://(\S*?\.\S*?))(\s|\;|\)|\]|\[|\{|\}|,|\"|'|:|\<|$|\.\s)#ie", $text))
		$reason = "you did not submit a full link (you need to include the http:// part).";

	if ($reason !== "None")
	{
		echo "<script>alert('Your submission cannot be accepted as it is because " . $reason . ". Please read the rules again and make the necessary changes. Thank you!')</script><script>history.go(-1)</script>";
		exit;
	}

	return false; //continue if everything is okay
}

// FIX COMMON TEXT ERRORS
function replaceText($text)
{
	$text = ucfirst($text); 						//capitalize first character

	if (!(preg_match("/[!?.]/", $text)))
		$text .= ".";								//if no punctuation mark, add period

	$text = str_ireplace("\"", "&quot;", $text); 	//change quotes to &quot; for twitter

	$text = str_ireplace("'", "&#39;", $text);		//change apostrophe to &#39 to avoid errors

	return $text;
}

// INSERT SUBMISSION INTO DATABASE AND LOG IP
function insertIntoDatabase($t, $choose, $ip, $con)
{
	//insert thing into database
	$query = "INSERT INTO $choose (id, thing) VALUES ('NULL', '$t');";
	mysqli_query($con, $query);

	//add ip to database
	$ipInsert = "INSERT INTO submissions (id,ip) VALUES ('NULL','$ip')";
	mysqli_query($con, $ipInsert);

	//get the id of the newly submitted thing
	$getNewest = "SELECT id FROM $choose WHERE 1 ORDER BY id DESC LIMIT 1;";
	$newestResult = mysqli_query($con, $getNewest) or die(mysqli_error($con));
	$new = mysqli_fetch_assoc($newestResult);

	//page redirect to newest thing
	if ($choose === "things")
		echo "<script>window.location = '/thankyou/".$new['id']."'</script>";
	else
		echo "<script>alert('Thank you for your submission!')</script><script>window.location = '/submit'</script>";
}

// SUBMIT BUTTON PRESSED
if (!empty($_POST))
{
	// database connection
	include_once("config.php");
	require_once('php/databaseConnection.php');

	//check to see if ip hasn't submitted too many times today
	$ip = dailyLimit($con);

	//remove excess space from before first word and after last word before we start anything
	$t = trim($_POST['thing']);

	//take out html or php tags
	$t = strip_tags($t, '');

	// go through different filters based on submission type
	if ((isset($_POST['choose']) and ($_POST['choose'] !== "")))
	{

		$choose = $_POST['choose'];

		// things to do and suggestions for the site need filters
		if (($choose === "things") or ($choose === "suggestions"))
		{
			//check for filtered words
			$reason = filteredWords($t);
			$t = replaceText($t);
		}

		// spam requires fewer filters since it's not public
		else if ($choose !== "spam")
		{
			exit;
		}

		insertIntoDatabase($t, $choose, $ip, $con);
	} // end type filters

} //end submission post

?>