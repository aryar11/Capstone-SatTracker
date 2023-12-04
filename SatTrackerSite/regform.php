<?php
//Registration form 

//take inputs upon submission
if(isset($_POST['submit'])){
    $name = $_POST['name'];
    $username = $_POST['username'];
    $passcode = $_POST['password'];
    $confirm_passcode = $_POST["confirm_password"];
    $password_hash = password_hash($passcode, PASSWORD_BCRYPT);
    $security_question = $_POST['security_question'];
    $security_answer = $_POST['security_answer'];

}

/*Connect to the DB 
define("host", "localhost:3307");
define("db_user", "root");
define("pass", "");
define("db", "users"); */
define("host", "sattrack.ckiq4qoeqhbu.us-east-2.rds.amazonaws.com");
define("db_user", "admin");
define("pass", "SatTracker23");
define("db", "users");

$con = mysqli_connect(host, db_user, null, db);

//set boolean to see if error is caught
$err = false;


if (!$con){
    die("Connection to DB failed" . mysqli_connect_error());
}

//passcode must be 6 chars
if(strlen($passcode) < 6){
    echo "passcode too short";
    header("location: badpassword.html");
    $err = true;
    
}

//password must match confirm password
if($passcode != $confirm_passcode){
    echo"Password don't match!";
    header("location: badpassword.html");
    $err = true;
}

//checking consecutive "."
$arr1 = str_split($username);
for($x=0; $x<=sizeof($arr1); $x++){
    if($arr1[$x] == '.' && $arr1[$x+1] == '.'){
        $err = true;
        header("location: badpassword.html");
        
    }
    
}


//check to make sure email isn't alread in use
$query = "SELECT username from info";

$user_check = mysqli_query($con, $query);
if($user_check->num_rows > 0){
   
    while($row = mysqli_fetch_assoc($user_check)){
        if($username == $row["username"]){
            echo "in use";
            header("location: takenemail.html");
            $err=true;
            break;
        }
        
    }
}

//If passess all test, insert into table and redirect to tool
if(!$err){
$sql = "INSERT INTO info (id, name, username, password, security_question, security_answer) VALUES ('0', '".mysqli_real_escape_string($con, $name)."', '".mysqli_real_escape_string($con, $username)."', '".mysqli_real_escape_string($con, $passcode)."', '$security_question', '".mysqli_real_escape_string($con, $security_answer)."')";

$rs = mysqli_query($con, $sql);
if($rs) {
    echo "entries added!";
     header("location: sessstart.php");
}

}

mysqli_close($con);


?>