<?php
//Registration form 

//take inputs upon submission
if(isset($_POST['submit'])){
    $name = $_POST['name'];
    $email = $_POST['email'];
    $passcode = $_POST['password'];
    $confirm_passcode = $_POST["confirm_password"];
    $password_hash = password_hash($passcode, PASSWORD_BCRYPT);
    $security_question = $_POST['security_question'];
    $security_answer = $_POST['security_answer'];

}

//connect to db
define("host", "localhost:3307");
define("db_user", "root");
define("pass", "");
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

//check to make sure email isn't alread in use
$query = "SELECT email from info";

$email_check = mysqli_query($con, $query);
if($email_check->num_rows > 0){
   
    while($row = mysqli_fetch_assoc($email_check)){
        if($email == $row["email"]){
            echo "in use";
            header("location: takenemail.html");
            $err=true;
            break;
        }
        
    }
}

//If passess all test, insert into table and redirect to tool
if(!$err){
$sql = "INSERT INTO info (id, name, email, password, security_question, security_answer) VALUES ('0', '".mysqli_real_escape_string($con, $name)."', '".mysqli_real_escape_string($con, $email)."', '".mysqli_real_escape_string($con, $passcode)."', '$security_question', '".mysqli_real_escape_string($con, $security_answer)."')";

$rs = mysqli_query($con, $sql);
if($rs) {
    echo "entries added!";
    header("location: sessstart.php");
}

}

mysqli_close($con);


?>