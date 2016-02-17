<?

set_time_limit(60*60);

// enable all error reporting
ini_set('display_startup_errors',1);
ini_set('display_errors',1);
error_reporting(-1);

ini_set("auto_detect_line_endings", true);
require_once('connect.php'); //database connection

$lines = file('defs.txt', FILE_IGNORE_NEW_LINES);

foreach($lines as $f){
	// get word and definition from line
	$word = get_string_between($f, "<hw>", "</hw>");
	$word = preg_replace('~[^a-zA-Z ]+~', '', $word);
	$word = strtolower($word);

	if ($word){
		$saved_word = $word;
	}

	$def = get_string_between($f, "<def>", "</def>");
	$def = preg_replace('~[^a-zA-Z ]+~', '', $def);
	$def = strtolower($def);

	if ($def){
		$related = get_related($def);
		$add = "UPDATE `words2` SET `related` = '$related' WHERE `word` = '$saved_word'";
		$adding = mysqli_query($con, $add) or die(mysqli_error());
		$saved_word = "";
	}
}

// parses words and definitions
function get_string_between($string, $start, $end){
    $string = " ".$string;
    $ini = strpos($string,$start);
    if ($ini == 0) return "";
    $ini += strlen($start);
    $len = strpos($string,$end,$ini) - $ini;
    return substr($string,$ini,$len);
}

// breaks definition into related words and removes stop words
function get_related($def){
	$rel = preg_split('/ /', $def);

	$stopwords = array("a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thick", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the");

	foreach ($rel as $key => $r){
		foreach ($stopwords as $s){
			if($r == $s) {
			    unset($rel[$key]);
			}
		}
	}

	// create string
	$related = "";
	foreach ($rel as $r){
		$related .= $r . ",";
	}

	return $related;
}

?>